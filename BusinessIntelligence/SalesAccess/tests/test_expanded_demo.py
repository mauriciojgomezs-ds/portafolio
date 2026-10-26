import pandas as pd
import pytest

from sales_access.data import demo_sales, agent_roster
from sales_access.analytics import rank_extremes
from sales_access.security import Profile, authorized_sales


@pytest.fixture(scope="module")
def expanded():
    return demo_sales()


def test_forty_agents_stable_assignments_and_own_clients(expanded):
    assert len(agent_roster()) == expanded.agente_id.nunique() == 40
    assert expanded.groupby("equipo").agente_id.nunique().to_dict() == {"Norte": 20, "Sur": 20}
    assert expanded.groupby("agente_id")[["equipo", "region", "sector"]].nunique().eq(1).all().all()
    assert expanded.groupby("cliente_id").agente_id.nunique().eq(1).all()
    assert expanded.groupby("producto").apply(lambda group: (group.costo / group.unidades).nunique(), include_groups=False).eq(1).all()
    assert expanded.venta_id.is_unique and expanded.margen.gt(0).all()
    assert expanded.agente_id.str.extract(r"(\d+)$")[0].astype(int).mod(2).eq(1).equals(expanded.equipo.eq("Norte"))


@pytest.mark.parametrize("zone", ["Norte", "Sur"])
def test_each_zone_has_top_five_bottom_five_with_no_overlap(expanded, zone):
    scoped = authorized_sales(expanded, Profile("s", "Supervisor", "supervisor", teams=(zone,)))
    assert scoped.agente_id.nunique() == 20
    top, bottom = rank_extremes(scoped, "agente_id")
    assert len(top) == len(bottom) == 5
    assert set(top.agente_id).isdisjoint(bottom.agente_id)
    assert top.importe.min() > bottom.importe.max()


def test_reproducibility_and_agents_at_end_of_roster(expanded):
    pd.testing.assert_frame_equal(expanded, demo_sales())
    for agent, zone in [("agente_39", "Norte"), ("agente_40", "Sur")]:
        scoped = authorized_sales(expanded, Profile(agent, "Agente", "agente", agent_id=agent))
        assert not scoped.empty
        assert set(scoped.agente_id) == {agent} and set(scoped.equipo) == {zone}
