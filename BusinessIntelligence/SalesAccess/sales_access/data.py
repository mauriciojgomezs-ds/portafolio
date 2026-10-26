from pathlib import Path
import math
import random
import json

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
COLUMNS = ["venta_id", "fecha", "agente_id", "equipo", "sector", "region", "producto", "cliente_id", "unidades", "venta_neta", "costo"]


def validate(data: pd.DataFrame) -> pd.DataFrame:
    missing = set(COLUMNS) - set(data.columns)
    if missing:
        raise ValueError("Faltan columnas: " + ", ".join(sorted(missing)))
    df = data[COLUMNS].copy()
    if df.empty or df.drop(columns="costo").isna().any().any():
        raise ValueError("El archivo debe contener ventas sin valores vacíos, excepto costo si no está disponible.")
    for column in COLUMNS[:8]:
        if column != "fecha":
            df[column] = df[column].astype(str).str.strip()
            if df[column].eq("").any():
                raise ValueError(f"Hay valores vacíos en {column}.")
    if df.venta_id.duplicated().any():
        raise ValueError("venta_id debe ser único por fila.")
    df["fecha"] = pd.to_datetime(df.fecha, format="%Y-%m-%d", errors="raise")
    for column in ["unidades", "venta_neta", "costo"]:
        df[column] = pd.to_numeric(df[column], errors="raise")
        if not df[column].dropna().map(math.isfinite).all() or df[column].lt(0).any():
            raise ValueError(f"{column} debe ser finito y no negativo.")
    if df.unidades.le(0).any() or df.unidades.mod(1).ne(0).any():
        raise ValueError("Las unidades deben ser enteros positivos.")
    df["margen"] = df.venta_neta - df.costo
    return df.sort_values("fecha").reset_index(drop=True)


def agent_roster(agents_per_zone=20):
    if not isinstance(agents_per_zone, int) or not 1 <= agents_per_zone <= 100:
        raise ValueError("agents_per_zone debe ser un entero entre 1 y 100.")
    north = ["Antofagasta", "Tarapacá", "Atacama", "Coquimbo"]
    south = ["Biobío", "Los Lagos", "La Araucanía", "Los Ríos"]
    return [{"agente_id": f"agente_{2*i+offset}", "equipo": team,
             "sector": ("Retail" if i % 2 == 0 else "Empresas") if team == "Norte" else ("Empresas" if i % 2 == 0 else "Retail"),
             "region": regions[i % len(regions)]}
            for i in range(agents_per_zone)
            for offset, team, regions in [(1, "Norte", north), (2, "Sur", south)]]


def demo_sales(agents_per_zone=20) -> pd.DataFrame:
    rng = random.Random(42)
    rows = []
    assignments = agent_roster(agents_per_zone)
    prices = {"Notebook": 650000, "Monitor": 180000, "Accesorios": 35000,
              "Teclado": 45000, "Mouse": 22000, "Impresora": 240000,
              "Tablet": 320000, "Audífonos": 65000, "Webcam": 55000,
              "Router": 85000, "SSD": 95000, "Dock USB": 75000}
    # Capacidad y preferencia comercial permanentes por agente; costos por producto.
    capacities = {a["agente_id"]: rng.uniform(1.0, 5.0) for a in assignments}
    preferred = {a["agente_id"]: rng.sample(list(prices), 4) for a in assignments}
    unit_costs = {product: round(prices[product] * rng.uniform(.58, .76)) for product in prices}
    for day in pd.date_range("2026-01-01", "2026-09-30"):
        season = 1 + (day.month - 1) * .035
        weekday_factor = .4 if day.weekday() >= 5 else 1.0
        for number, assignment in enumerate(assignments):
            agent, team, sector, region = (assignment[c] for c in ["agente_id", "equipo", "sector", "region"])
            volume = max(1, round(capacities[agent] * season * weekday_factor * rng.uniform(.7, 1.3)))
            for _ in range(volume):
                product = rng.choice(preferred[agent] if rng.random() < .7 else list(prices))
                units = rng.randint(2, 8) if sector == "Empresas" else rng.randint(1, 4)
                discount = rng.uniform(.86, .96) if sector == "Empresas" else rng.uniform(.94, 1.0)
                sale = round(prices[product] * units * discount)
                client = f"C{number*15+rng.randint(1, 15):04}"
                rows.append([f"V{len(rows)+1:06}", day.strftime("%Y-%m-%d"), agent, team, sector,
                             region, product, client, units, sale,
                             unit_costs[product] * units])
    return validate(pd.DataFrame(rows, columns=COLUMNS))


def load_sales(path: Path | None = None):
    path = path or ROOT / "data" / "ventas.csv"
    if path.exists():
        metadata_path = path.with_suffix(".metadata.json")
        metadata = json.loads(metadata_path.read_text(encoding="utf-8")) if metadata_path.exists() else {
            "source": "CSV local · moneda CLP", "currency": "CLP", "revenue_label": "Venta neta"}
        if not isinstance(metadata, dict) or any(not isinstance(metadata.get(key), str) or not metadata[key].strip()
                                                 for key in ("source", "currency", "revenue_label")):
            raise ValueError("Los metadatos requieren source, currency y revenue_label como textos no vacíos.")
        return validate(pd.read_csv(path, dtype={c: str for c in COLUMNS[:8]})), metadata
    return demo_sales(), {"source": "Demo sintética · 40 agentes · 20 Norte / 20 Sur · CLP · enero–septiembre 2026",
                          "currency": "CLP", "revenue_label": "Venta neta simulada", "synthetic_data": True}


def export_csv(data: pd.DataFrame) -> bytes:
    # Evita ejecutar fórmulas cuando Excel abre texto de una fuente externa.
    safe = data.copy()
    for column in safe.select_dtypes(include=["object", "str", "string"]).columns:
        safe[column] = safe[column].map(lambda v: "'" + v if isinstance(v, str) and v.lstrip().startswith(("=", "+", "-", "@")) else v)
    return safe.to_csv(index=False).encode("utf-8-sig")
