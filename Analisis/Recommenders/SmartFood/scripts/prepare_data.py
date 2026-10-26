"""Convertir los CSV originales a Parquet sin normalizar su contenido."""

import argparse
from pathlib import Path

import pandas as pd


def prepare_data(data_dir: Path, overwrite: bool = False) -> list[Path]:
    """Validar ambas entradas antes de convertir un archivo completo por vez."""
    sources = [data_dir / f"{name}.csv" for name in ("recipes", "reviews")]
    missing = [str(path) for path in sources if not path.is_file()]
    if missing:
        raise FileNotFoundError("Faltan archivos de entrada: " + ", ".join(missing))
    targets = [source.with_suffix(".parquet") for source in sources]
    existing = [str(path) for path in targets if path.exists()]
    if existing and not overwrite:
        raise FileExistsError(
            "Ya existen archivos Parquet; utiliza --overwrite para reemplazarlos: "
            + ", ".join(existing)
        )
    for source, target in zip(sources, targets):
        frame = pd.read_csv(source)
        frame.to_parquet(target, index=False)
        print(f"{source.name} -> {target.name}: {len(frame):,} filas")
        del frame
    return targets


def main() -> None:
    default_dir = Path(__file__).resolve().parents[1] / "data" / "raw"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=default_dir)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    try:
        prepare_data(args.data_dir, args.overwrite)
    except (FileNotFoundError, FileExistsError) as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
