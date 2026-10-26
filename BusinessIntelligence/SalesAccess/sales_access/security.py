from dataclasses import dataclass
import hashlib
import hmac
import json
from pathlib import Path
import secrets
import sqlite3
import time

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / ".local" / "users.sqlite3"
ROLES = {"gerente", "analista", "supervisor", "agente"}
ITERATIONS = 600_000


@dataclass(frozen=True)
class Profile:
    username: str
    name: str
    role: str
    teams: tuple[str, ...] = ()
    sectors: tuple[str, ...] = ()
    regions: tuple[str, ...] = ()
    agent_id: str | None = None


def password_hash(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), ITERATIONS).hex()


def initialize(db: Path = DB):
    db.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db) as con:
        con.execute("""CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY, name TEXT NOT NULL, role TEXT NOT NULL,
            teams TEXT NOT NULL, sectors TEXT NOT NULL, regions TEXT NOT NULL,
            agent_id TEXT, salt TEXT NOT NULL, password_hash TEXT NOT NULL,
            active INTEGER NOT NULL DEFAULT 1, failed INTEGER NOT NULL DEFAULT 0,
            locked_until REAL NOT NULL DEFAULT 0)""")


def add_user(profile: Profile, password: str, db: Path = DB):
    if profile.role not in ROLES or len(password) < 12:
        raise ValueError("Rol inválido o contraseña de menos de 12 caracteres.")
    if profile.role == "supervisor" and not any((profile.teams, profile.sectors, profile.regions)):
        raise ValueError("Un supervisor necesita al menos un segmento.")
    if profile.role == "agente" and not profile.agent_id:
        raise ValueError("Un agente necesita su identificador.")
    initialize(db)
    salt = secrets.token_hex(16)
    with sqlite3.connect(db) as con:
        con.execute("""INSERT INTO users
            (username,name,role,teams,sectors,regions,agent_id,salt,password_hash)
            VALUES (?,?,?,?,?,?,?,?,?)""", (
                profile.username, profile.name, profile.role, json.dumps(profile.teams),
                json.dumps(profile.sectors), json.dumps(profile.regions), profile.agent_id,
                salt, password_hash(password, salt)))


def _profile(row) -> Profile | None:
    if row is None or not row["active"] or row["role"] not in ROLES:
        return None
    return Profile(row["username"], row["name"], row["role"],
                   tuple(json.loads(row["teams"])), tuple(json.loads(row["sectors"])),
                   tuple(json.loads(row["regions"])), row["agent_id"])


def get_profile(username: str, db: Path = DB) -> Profile | None:
    if not db.exists():
        return None
    with sqlite3.connect(db) as con:
        con.row_factory = sqlite3.Row
        return _profile(con.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone())


def authenticate(username: str, password: str, db: Path = DB) -> Profile | None:
    if not db.exists():
        return None
    # Serializa intentos por cuenta; el bloqueo se comparte entre sesiones.
    with sqlite3.connect(db, timeout=15) as con:
        con.row_factory = sqlite3.Row
        con.execute("BEGIN IMMEDIATE")
        row = con.execute("SELECT * FROM users WHERE username=?", (username.strip().lower(),)).fetchone()
        candidate = password_hash(password, row["salt"] if row else "00" * 16)
        if row is None or not row["active"] or row["locked_until"] > time.time():
            return None
        if not hmac.compare_digest(candidate, row["password_hash"]):
            failed = row["failed"] + 1 if row["locked_until"] == 0 else 1
            until = time.time() + 300 if failed >= 5 else 0
            con.execute("UPDATE users SET failed=?,locked_until=? WHERE username=?", (failed, until, row["username"]))
            return None
        con.execute("UPDATE users SET failed=0,locked_until=0 WHERE username=?", (row["username"],))
        return _profile(row)


def authorized_sales(data, profile: Profile):
    """Denegación por defecto. Los ejes configurados se intersectan (AND)."""
    if profile.role in {"gerente", "analista"}:
        return data.copy()
    if profile.role == "agente" and profile.agent_id:
        return data.loc[data["agente_id"].eq(profile.agent_id)].copy()
    if profile.role == "supervisor" and any((profile.teams, profile.sectors, profile.regions)):
        mask = data.index.to_series().map(lambda _: True)
        for column, values in [("equipo", profile.teams), ("sector", profile.sectors), ("region", profile.regions)]:
            if values:
                mask &= data[column].isin(values)
        return data.loc[mask].copy()
    return data.iloc[:0].copy()
