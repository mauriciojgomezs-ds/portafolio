import argparse
import hashlib
import io
import json
from pathlib import Path
import sys
import urllib.request
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sales_access.data import ROOT, COLUMNS
from sales_access.kaggle_import import transform


def main():
    parser = argparse.ArgumentParser(description="Importa DataRegina con agentes/equipos simulados.")
    parser.add_argument("--archive", type=Path, help="ZIP descargado de Kaggle")
    parser.add_argument("--download", action="store_true", help="Descargar el ZIP público")
    args = parser.parse_args()
    if bool(args.archive) == bool(args.download):
        parser.error("Indica --archive ruta.zip o --download")
    target = ROOT / "data" / "ventas.csv"
    if target.exists():
        parser.error("Ya existe data/ventas.csv. Renómbralo antes de importar para conservarlo.")
    payload = args.archive.read_bytes() if args.archive else urllib.request.urlopen(
        "https://www.kaggle.com/api/v1/datasets/download/dataregina/datasets-para-proyecto-bi", timeout=30).read()
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        data, metadata = transform(archive)
    metadata["archive_sha256"] = hashlib.sha256(payload).hexdigest()
    target.parent.mkdir(parents=True, exist_ok=True)
    raw = ROOT / ".local" / "kaggle_dataregina.zip"
    raw.parent.mkdir(parents=True, exist_ok=True)
    raw.write_bytes(payload)
    metadata_path = target.with_suffix(".metadata.json")
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    data[COLUMNS].to_csv(target, index=False)
    print(json.dumps(metadata, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
