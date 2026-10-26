"""Recupera fuentes públicas declaradas en config.json, sin reemplazar archivos."""
from pathlib import Path
import json
from urllib.request import urlopen, Request
import shutil
PROJECT_ROOT=Path(__file__).resolve().parents[1]
cfg=json.loads((PROJECT_ROOT/"config.json").read_text(encoding="utf-8"))
jobs=[
    ("https://huggingface.co/datasets/stanfordnlp/imdb/resolve/main/plain_text/train-00000-of-00001.parquet", PROJECT_ROOT/cfg["source"]),
    ("https://huggingface.co/datasets/stanfordnlp/imdb/resolve/main/plain_text/test-00000-of-00001.parquet", PROJECT_ROOT/cfg["test_source"]),
    ("https://huggingface.co/datasets/stanfordnlp/imdb/raw/main/README.md", (PROJECT_ROOT/cfg["source"]).parent/"README_fuente.md"),
]

if __name__=="__main__":
    for url,dest in jobs:
        dest=dest.resolve()
        if dest.exists():
            print(f"Ya existe: {dest.name}")
            continue
        dest.parent.mkdir(parents=True,exist_ok=True)
        partial=dest.with_suffix(dest.suffix+".part")
        with urlopen(Request(url,headers={"User-Agent":"portfolio-dataset-download"}),timeout=45) as src, partial.open("wb") as dst:
            shutil.copyfileobj(src,dst)
        partial.replace(dest)
        print(f"Descargado: {dest.name}")
