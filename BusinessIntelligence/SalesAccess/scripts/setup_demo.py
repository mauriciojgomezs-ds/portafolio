"""Crea cuentas de demo una sola vez, sin sobrescribir usuarios existentes."""
from pathlib import Path
import secrets
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sales_access.security import DB, Profile, add_user, get_profile
from sales_access.agents import agent_directory

PROFILES = [
    Profile("gerente", "Gerencia comercial", "gerente"),
    Profile("analista", "Análisis comercial", "analista"),
    Profile("supervisor_norte", "Supervisión Norte", "supervisor", teams=("Norte",)),
    Profile("supervisor_sur", "Supervisión Sur", "supervisor", teams=("Sur",)),
] + [Profile(a["agente_id"], f"{a['nombre']} · {a['equipo']}",
             "agente", agent_id=a["agente_id"]) for a in agent_directory().to_dict("records")]


def main():
    credentials = DB.parent / "credenciales_demo.txt"
    created = 0
    for profile in PROFILES:
        if get_profile(profile.username) is not None:
            continue
        password = secrets.token_urlsafe(15)
        add_user(profile, password)
        with credentials.open("a", encoding="utf-8") as file:
            file.write(f"{profile.username}: {password}\n")
        created += 1
    print(f"Cuentas creadas: {created}. Credenciales locales: {credentials}")


if __name__ == "__main__":
    main()
