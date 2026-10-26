import pandas as pd

from sales_access.analytics import percent_change, previous_period, rank_extremes, segment_summary, compare_segments
from sales_access.data import demo_sales
from sales_access.security import Profile, authorized_sales


def test_rankings_disjoint_and_contributions():
    data = demo_sales(agents_per_zone=2)
    top, bottom = rank_extremes(data, "agente_id")
    assert len(top) == len(bottom) == 2
    assert set(top.agente_id).isdisjoint(bottom.agente_id)
    assert top.importe.min() >= bottom.importe.max()
    summary = segment_summary(data, "agente_id")
    assert abs(summary.participacion.sum() - 1) < 1e-10
    assert summary.importe.sum() == data.venta_neta.sum()


def test_single_agent_and_own_client_rankings():
    data = authorized_sales(demo_sales(agents_per_zone=2), Profile("u", "U", "agente", agent_id="agente_1"))
    top, bottom = rank_extremes(data, "agente_id")
    assert set(top.agente_id) == {"agente_1"} and bottom.empty
    clients = segment_summary(data, "cliente_id")
    assert clients.operaciones.sum() == len(data)


def test_previous_period_equal_length_and_segment_only():
    data = authorized_sales(demo_sales(agents_per_zone=2), Profile("u", "U", "supervisor", teams=("Norte",)))
    previous, start, end, available = previous_period(data, "2026-09-01", "2026-09-30")
    assert available and (end - start).days == 29
    assert start == pd.Timestamp("2026-08-02") and end == pd.Timestamp("2026-08-31")
    assert set(previous.equipo) == {"Norte"}
    assert previous.fecha.max() < pd.Timestamp("2026-09-01")


def test_missing_history_zero_baseline_and_zero_revenue():
    data = demo_sales(agents_per_zone=2)
    _, _, _, available = previous_period(data, "2026-01-01", "2026-01-30")
    assert not available
    assert percent_change(100, 50, available) is None
    assert percent_change(100, 0, True) is None
    assert percent_change(75, 100, True) == "-25.0%"
    data["venta_neta"] = 0
    assert segment_summary(data, "producto").participacion.eq(0).all()


def test_comparison_includes_new_and_disappearing_products():
    current = pd.DataFrame({"producto": ["Nuevo", "Compartido"], "venta_neta": [20., 120.]})
    reference = pd.DataFrame({"producto": ["Anterior", "Compartido"], "venta_neta": [40., 100.]})
    result = compare_segments(current, reference, "producto").set_index("producto")
    assert set(result.index) == {"Nuevo", "Anterior", "Compartido"}
    assert result.loc["Anterior", "variacion_pct"] == -100
    assert pd.isna(result.loc["Nuevo", "variacion_pct"])
    assert result.loc["Compartido", "variacion_pct"] == 20
    assert result.diferencia.sum() == current.venta_neta.sum() - reference.venta_neta.sum()
    assert abs(result.aporte_variacion_pp.sum()) < 1e-10


def test_comparison_zero_reference_and_empty_current():
    current = pd.DataFrame({"producto": ["P"], "venta_neta": [10.]})
    reference = pd.DataFrame({"producto": ["P"], "venta_neta": [0.]})
    result = compare_segments(current, reference, "producto")
    assert result.variacion_pct.isna().all() and result.aporte_variacion_pp.isna().all()
    lost = compare_segments(current.iloc[:0], current, "producto")
    assert lost.diferencia.sum() == -10 and lost.variacion_pct.iloc[0] == -100
