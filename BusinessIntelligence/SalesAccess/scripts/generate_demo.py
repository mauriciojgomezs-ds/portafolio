"""Activa la demo ampliada, conservando una copia de la fuente anterior."""
from datetime import datetime
import json
from pathlib import Path
import shutil
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sales_access.data import ROOT, COLUMNS, demo_sales
from sales_access.agents import agent_directory


def main():
    data = demo_sales()
    folder = ROOT / "data"
    folder.mkdir(exist_ok=True)
    target = folder / "ventas.csv"
    metadata_file = target.with_suffix(".metadata.json")
    if target.exists() or metadata_file.exists():
        backup = ROOT / ".local" / "source_backups" / datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        backup.mkdir(parents=True)
        for original in (target, metadata_file):
            if original.exists():
                shutil.copy2(original, backup / original.name)
        print(f"Fuente anterior preservada en: {backup}")
    metadata = {
        "source": "Demo sintética · 40 agentes · 20 Norte / 20 Sur · CLP · enero–septiembre 2026",
        "currency": "CLP", "revenue_label": "Venta neta simulada",
        "synthetic_data": True, "seed": 42, "agents_per_zone": 20,
        "rows": len(data), "clients_per_agent": 15,
        "rules": ["Equipo, región y sector fijos por agente", "Carteras exclusivas por agente",
                  "Precios y costos de catálogo fijos por producto", "Descuentos por sector",
                  "Capacidad y mezcla propias por agente", "Crecimiento mensual y menor actividad en fines de semana"],
    }
    data[COLUMNS].to_csv(target, index=False)
    metadata_file.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    roster_path = folder / "agentes_demo.csv"
    agent_directory().to_csv(roster_path, index=False)
    print(json.dumps(metadata, ensure_ascii=True))


if __name__ == "__main__":
    main()
