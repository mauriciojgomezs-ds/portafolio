from dataclasses import replace
import sqlite3

import pytest

from sales_access.data import demo_sales, export_csv, validate
from sales_access.security import Profile, add_user, authenticate, authorized_sales, get_profile


@pytest.fixture(scope="module")
def sales():
    return demo_sales(agents_per_zone=2)


@pytest.mark.parametrize("role", ["gerente", "analista"])
def test_global_access(sales, role):
    assert len(authorized_sales(sales, Profile("u", "User", role))) == len(sales)


def test_supervisor_intersection(sales):
    profile = Profile("u", "User", "supervisor", teams=("Norte",), sectors=("Retail",), regions=("Antofagasta",))
    visible = authorized_sales(sales, profile)
    assert not visible.empty
    assert set(visible.agente_id) == {"agente_1"}
    assert authorized_sales(sales, replace(profile, regions=("Biobío",))).empty


def test_multiple_segments_union_within_axis(sales):
    profile = Profile("u", "User", "supervisor", regions=("Antofagasta", "Biobío"))
    assert set(authorized_sales(sales, profile).agente_id) == {"agente_1", "agente_2"}


@pytest.mark.parametrize("profile", [Profile("u", "U", "supervisor"), Profile("u", "U", "agente"), Profile("u", "U", "admin")])
def test_deny_by_default(sales, profile):
    assert authorized_sales(sales, profile).empty


def test_agent_isolation_and_export(sales):
    one = authorized_sales(sales, Profile("agente_1", "U", "agente", agent_id="agente_1"))
    two = authorized_sales(sales, Profile("agente_2", "U", "agente", agent_id="agente_2"))
    assert not one.empty and not two.empty
    assert set(one.venta_id).isdisjoint(two.venta_id)
    assert b"agente_2" not in export_csv(one)
    assert b"agente_1" not in export_csv(two)


def test_authentication_lockout_and_revocation(tmp_path):
    db = tmp_path / "users.db"
    profile = Profile("agente_1", "U", "agente", agent_id="agente_1")
    add_user(profile, "TestPassword_12345", db)
    assert authenticate("agente_1", "TestPassword_12345", db) == profile
    assert authenticate("' OR 1=1 --", "TestPassword_12345", db) is None
    for _ in range(5):
        assert authenticate("agente_1", "wrong", db) is None
    assert authenticate("agente_1", "TestPassword_12345", db) is None
    with sqlite3.connect(db) as con:
        row = con.execute("SELECT password_hash,salt FROM users").fetchone()
        assert row[0] != "TestPassword_12345" and len(row[1]) == 32
        con.execute("UPDATE users SET locked_until=1")
    assert authenticate("agente_1", "TestPassword_12345", db) == profile
    with sqlite3.connect(db) as con:
        con.execute("UPDATE users SET active=0")
    assert get_profile("agente_1", db) is None
    assert authenticate("agente_1", "TestPassword_12345", db) is None


def test_invalid_data_and_formula_escape(sales):
    for column, value in [("costo", float("inf")), ("venta_neta", -1), ("unidades", 1.5), ("region", "  "), ("fecha", "wrong")]:
        invalid = sales.copy()
        invalid[column] = invalid[column].astype(object)
        invalid.loc[0, column] = value
        with pytest.raises(ValueError):
            validate(invalid)
    dangerous = sales.iloc[:1].copy()
    dangerous["producto"] = "=1+1"
    assert b"'=1+1" in export_csv(dangerous)
