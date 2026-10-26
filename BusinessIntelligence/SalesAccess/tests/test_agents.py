import pytest

from sales_access.agents import agent_directory, visible_directory, BRANCHES, agent_sales_summary
from sales_access.data import demo_sales
from sales_access.security import Profile


def test_directory_consistency_and_demo_contacts():
    directory = agent_directory()
    assert len(directory) == 40 and directory.agente_id.is_unique
    assert directory.nombre.is_unique and directory.email.is_unique
    assert directory.email.str.endswith("@ventas.example").all()
    assert directory.movil.str.contains("XXXX").all() and directory.oficina.str.contains("XXXX").all()
    assert directory.sucursal.equals(directory.region.map(BRANCHES))
    assert directory.iniciales.str.len().eq(2).all()


@pytest.mark.parametrize("profile,count,teams", [
    (Profile("g", "G", "gerente"), 40, {"Norte", "Sur"}),
    (Profile("a", "A", "analista"), 40, {"Norte", "Sur"}),
    (Profile("s", "S", "supervisor", teams=("Norte",)), 20, {"Norte"}),
    (Profile("s", "S", "supervisor", teams=("Sur",)), 20, {"Sur"}),
    (Profile("agente_39", "U", "agente", agent_id="agente_39"), 1, {"Norte"}),
    (Profile("agente_40", "U", "agente", agent_id="agente_40"), 1, {"Sur"}),
])
def test_directory_respects_role(profile, count, teams):
    visible = visible_directory(profile)
    assert len(visible) == count and set(visible.equipo) == teams
    if profile.role == "agente":
        assert set(visible.agente_id) == {profile.agent_id}


def test_directory_intersects_scopes_and_denies_missing_scopes():
    visible = visible_directory(Profile("s", "S", "supervisor", teams=("Norte",), sectors=("Retail",), regions=("Antofagasta",)))
    assert len(visible) == 5
    assert set(visible.equipo) == {"Norte"} and set(visible.sector) == {"Retail"} and set(visible.region) == {"Antofagasta"}
    assert visible_directory(Profile("s", "S", "supervisor")).empty
    assert visible_directory(Profile("u", "U", "agente", agent_id="unknown")).empty


def test_sales_summary_is_only_for_selected_agent_and_handles_missing_costs():
    sales = demo_sales(agents_per_zone=2)
    own = sales[sales.agente_id.eq("agente_1")]
    summary = agent_sales_summary(sales, "agente_1")
    assert summary["importe"] == own.venta_neta.sum()
    assert summary["margen"] == own.margen.sum()
    assert summary["operaciones"] == len(own)
    assert summary["unidades"] == own.unidades.sum()
    assert summary["clientes"] == own.cliente_id.nunique()
    assert summary["importe_por_operacion"] == own.venta_neta.mean()
    assert agent_sales_summary(sales, "agente_39") is None
    sales.loc[sales.agente_id.eq("agente_1"), "costo"] = float("nan")
    assert agent_sales_summary(sales, "agente_1")["margen"] is None
