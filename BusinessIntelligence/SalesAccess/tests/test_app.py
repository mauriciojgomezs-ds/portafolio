from pathlib import Path
import time
from datetime import date

import pytest
from streamlit.testing.v1 import AppTest

from sales_access import security
from sales_access import data
from sales_access.security import Profile
from sales_access.agents import agent_directory

APP = Path(__file__).resolve().parents[1] / "app.py"


@pytest.fixture
def setup_users(tmp_path, monkeypatch):
    # Las vistas de permisos se prueban con una fuente fija, independiente del CSV local.
    monkeypatch.setattr(data, "load_sales", lambda: (data.demo_sales(agents_per_zone=2), {
        "source": "Demo sintética para pruebas", "currency": "CLP", "revenue_label": "Venta neta"}))
    db = tmp_path / "users.db"
    profiles = [Profile("gerente", "Gerente", "gerente"), Profile("analista", "Analista", "analista"),
                Profile("supervisor_norte", "Supervisor", "supervisor", teams=("Norte",)),
                Profile("supervisor_sur", "Supervisor", "supervisor", teams=("Sur",)),
                Profile("agente_1", "Uno", "agente", agent_id="agente_1"),
                Profile("agente_2", "Dos", "agente", agent_id="agente_2")]
    for profile in profiles:
        security.add_user(profile, "TestPassword_12345", db)
    original_auth, original_get = security.authenticate, security.get_profile
    monkeypatch.setattr(security, "DB", db)
    monkeypatch.setattr(security, "authenticate", lambda u, p: original_auth(u, p, db))
    monkeypatch.setattr(security, "get_profile", lambda u: original_get(u, db))


def enter(at, username):
    at.text_input[0].set_value(username)
    at.text_input[1].set_value("TestPassword_12345")
    at.button[0].click().run()
    assert not at.exception
    return at


@pytest.mark.parametrize("user,agents", [("agente_1", {"agente_1"}), ("agente_2", {"agente_2"}),
    ("supervisor_norte", {"agente_1", "agente_3"}), ("supervisor_sur", {"agente_2", "agente_4"}),
    ("analista", {"agente_1", "agente_2", "agente_3", "agente_4"})])
def test_views_are_scoped(setup_users, user, agents):
    at = AppTest.from_file(str(APP), default_timeout=20).run()
    assert not at.metric and not at.dataframe
    enter(at, user)
    assert len(at.metric) == 8
    assert set(at.dataframe[-1].value.agente_id) == agents
    assert set(at.multiselect[3].options) == agents
    assert {"Rankings", "Mezcla y territorio", "Cartera de clientes"}.issubset({tab.label for tab in at.tabs})
    if user.startswith("supervisor"):
        assert set(at.dataframe[0].value.agente_id) == agents


def test_manager_logout_and_account_switch(setup_users):
    at = enter(AppTest.from_file(str(APP), default_timeout=20).run(), "gerente")
    assert "agente_id" not in at.dataframe[0].value.columns
    assert set(at.dataframe[0].value.equipo) == {"Norte", "Sur"}
    at.button(key="logout").click().run()
    assert not at.metric and not at.dataframe
    enter(at, "agente_2")
    assert set(at.dataframe[0].value.agente_id) == {"agente_2"}


def test_filtered_empty_state(setup_users):
    at = enter(AppTest.from_file(str(APP), default_timeout=20).run(), "analista")
    at.multiselect[0].set_value(["Norte"])
    at.multiselect[2].set_value(["Biobío"]).run()
    assert not at.exception and not at.dataframe
    assert any("No hay ventas" in message.value for message in at.info)


def test_expired_session_returns_to_login(setup_users):
    at = enter(AppTest.from_file(str(APP), default_timeout=20).run(), "agente_1")
    at.session_state["login_time"] = time.time() - 3601
    at.run()
    assert not at.exception and not at.metric and not at.dataframe
    assert len(at.text_input) == 2


def test_missing_costs_not_reported_as_zero(setup_users, monkeypatch):
    sales = data.demo_sales(agents_per_zone=2)
    sales["costo"] = float("nan")
    sales["margen"] = float("nan")
    monkeypatch.setattr(data, "load_sales", lambda: (sales, {
        "source": "Kaggle para prueba", "currency": "U.M.", "revenue_label": "Importe estimado", "simulated_assignments": True}))
    at = enter(AppTest.from_file(str(APP), default_timeout=20).run(), "gerente")
    assert at.metric[1].value == "Sin costos"
    assert at.metric[2].value == "—"
    assert "margen" not in at.dataframe[0].value.columns
    assert "simulados" in at.info[0].value


def test_quick_period_comparison_and_rank_metric(setup_users):
    at = enter(AppTest.from_file(str(APP), default_timeout=20).run(), "analista")
    at.selectbox(key="period_preset").set_value("Últimos 30 días").run()
    assert not at.exception
    assert at.metric[0].delta
    assert any("con los mismos filtros" in caption.value for caption in at.caption)
    at.selectbox(key="ranking_metric").set_value("Unidades").run()
    assert not at.exception
    ranking = at.dataframe[0].value
    assert ranking.unidades.is_monotonic_decreasing
    at.multiselect[3].set_value(["agente_1"]).run()
    assert not at.exception
    assert set(at.dataframe[0].value.agente_id) == {"agente_1"}
    assert set(at.dataframe[-1].value.agente_id) == {"agente_1"}


def test_analyst_comparison_axes_custom_period_and_filters(setup_users):
    at = enter(AppTest.from_file(str(APP), default_timeout=20).run(), "analista")
    assert any("No hay historial suficiente" in item.value for item in at.info)
    at.selectbox(key="period_preset").set_value("Últimos 30 días").run()
    comparisons = [table.value for table in at.dataframe if "importe_referencia" in table.value.columns]
    assert len(comparisons) == 1
    assert "producto" in comparisons[0]
    at.selectbox(key="comparison_axis").set_value("agente_id")
    at.multiselect[3].set_value(["agente_1"]).run()
    assert not at.exception
    comparison = next(table.value for table in at.dataframe if "importe_referencia" in table.value.columns)
    assert set(comparison.agente_id) == {"agente_1"}
    at.radio(key="comparison_mode").set_value("Período personalizado").run()
    at.date_input(key="comparison_reference").set_value((date(2026, 8, 1), date(2026, 8, 31))).run()
    assert not at.exception
    assert any("distinta duración" in item.value for item in at.warning)


@pytest.mark.parametrize("user", ["gerente", "supervisor_norte", "agente_1"])
def test_comparator_is_only_visible_to_analyst(setup_users, user):
    at = enter(AppTest.from_file(str(APP), default_timeout=20).run(), user)
    assert not at.radio
    assert all("importe_referencia" not in table.value.columns for table in at.dataframe)


def test_changing_source_resets_incompatible_dates_and_filters(setup_users, monkeypatch):
    at = enter(AppTest.from_file(str(APP), default_timeout=20).run(), "analista")
    at.multiselect[2].set_value(["Antofagasta"]).run()
    new_sales = data.demo_sales(agents_per_zone=2)
    new_sales["fecha"] = new_sales.fecha + data.pd.DateOffset(years=1)
    monkeypatch.setattr(data, "load_sales", lambda: (new_sales, {
        "source": "Nueva fuente sintética", "currency": "CLP", "revenue_label": "Ventas"}))
    at.run()
    assert not at.exception
    assert at.date_input(key="report_period").value[0].year == 2027
    assert not at.multiselect[2].value


@pytest.mark.parametrize("user,count,team", [("gerente", 40, None), ("analista", 40, None),
    ("supervisor_norte", 20, "Norte"), ("supervisor_sur", 20, "Sur")])
def test_directory_options_are_authorized(setup_users, user, count, team):
    at = enter(AppTest.from_file(str(APP), default_timeout=20).run(), user)
    options = at.selectbox(key="directory_agent").options
    assert len(options) == count
    directory = agent_directory()
    if team:
        allowed = directory[directory.equipo.eq(team)]
        blocked = directory[directory.equipo.ne(team)]
        assert all(any(name in option for name in allowed.nombre) for option in options)
        displayed = " ".join(item.value for item in at.markdown)
        assert all(email not in displayed for email in blocked.email)
    selected = directory.iloc[-1] if not team else directory[directory.equipo.eq(team)].iloc[-1]
    at.selectbox(key="directory_agent").set_value(selected.agente_id).run()
    assert not at.exception
    assert any(selected.email in item.value for item in at.markdown)


def test_agent_has_only_own_contact_card(setup_users):
    at = enter(AppTest.from_file(str(APP), default_timeout=20).run(), "agente_1")
    assert not any(select.key == "directory_agent" for select in at.selectbox)
    displayed = " ".join(item.value for item in at.markdown)
    assert "agente.01@ventas.example" in displayed
    assert "agente.02@ventas.example" not in displayed


def test_ranking_button_opens_contact_and_individual_sales_summary(setup_users):
    at = enter(AppTest.from_file(str(APP), default_timeout=20).run(), "gerente")
    button = next(button for button in at.button if button.key and button.key.startswith("view_agent_") and button.key != "view_agent_agente_1")
    target = button.key.removeprefix("view_agent_")
    button.click().run()
    assert not at.exception
    assert at.selectbox(key="directory_agent").value == target
    assert at.session_state["workspace_tab"] == "Directorio de agentes"
    record = agent_directory().set_index("agente_id").loc[target]
    assert any(record.email in item.value for item in at.markdown)
    assert any(f"Resumen de ventas · {record.nombre}" in item.value for item in at.markdown)
    at.multiselect[3].set_value(["agente_1"]).run()
    assert not at.exception
    assert any("Este agente no tiene operaciones" in item.value for item in at.info)


def test_directory_zone_branch_search_and_independent_report(setup_users):
    at = enter(AppTest.from_file(str(APP), default_timeout=20).run(), "gerente")
    assert {"Reporte de ventas", "Directorio de agentes"}.issubset({tab.label for tab in at.tabs})
    revenue = at.metric[0].value
    at.selectbox(key="directory_zone").set_value("Sur").run()
    assert len(at.selectbox(key="directory_agent").options) == 20
    assert "La Serena" not in at.selectbox(key="directory_branch").options
    at.selectbox(key="directory_branch").set_value("Concepción").run()
    assert len(at.selectbox(key="directory_agent").options) == 5
    assert all("Concepción" in option for option in at.selectbox(key="directory_agent").options)
    assert at.metric[0].value == revenue
    at.selectbox(key="directory_zone").set_value("Norte").run()
    assert at.selectbox(key="directory_branch").value == "Todas las sucursales"
    at.selectbox(key="directory_branch").set_value("La Serena").run()
    assert len(at.selectbox(key="directory_agent").options) == 5
    at.selectbox(key="directory_branch").set_value("Todas las sucursales")
    at.text_input(key="directory_search").set_value("Mariana Caceres").run()
    assert len(at.selectbox(key="directory_agent").options) == 1
    assert at.selectbox(key="directory_agent").value == "agente_39"
    assert not at.exception


def test_supervisor_directory_filters_stay_inside_own_zone(setup_users):
    at = enter(AppTest.from_file(str(APP), default_timeout=20).run(), "supervisor_sur")
    assert at.selectbox(key="directory_zone").options == ["Todas las zonas", "Sur"]
    assert "La Serena" not in at.selectbox(key="directory_branch").options
    at.selectbox(key="directory_branch").set_value("Concepción").run()
    assert len(at.selectbox(key="directory_agent").options) == 5
    assert all("Concepción" in option for option in at.selectbox(key="directory_agent").options)


def test_empty_directory_search_keeps_report_available(setup_users):
    at = enter(AppTest.from_file(str(APP), default_timeout=20).run(), "analista")
    at.text_input(key="directory_search").set_value("Nombre inexistente").run()
    assert not at.exception and len(at.metric) == 8
    assert any("No hay agentes" in item.value for item in at.info)
    assert not any(select.key == "directory_agent" for select in at.selectbox)
    at.text_input(key="directory_search").set_value("").run()
    assert len(at.selectbox(key="directory_agent").options) == 40
