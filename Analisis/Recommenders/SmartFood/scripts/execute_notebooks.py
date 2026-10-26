"""Ejecuta 01–05 en orden, cada uno con un kernel nuevo del Python activo."""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from smartfood.informe import generar_informe

import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager


NOTEBOOKS = [
    "01_preparacion_datos.ipynb",
    "02_analisis_exploratorio.ipynb",
    "03_baseline_perfil_usuario.ipynb",
    "04_filtrado_colaborativo_nmf.ipynb",
    "05_clasificacion_ranking_svm.ipynb",
]


def ejecutar_notebook(origen, raiz, fallo, timeout=900):
    """Actualiza las salidas del original al terminar; conserva una copia si falla."""
    notebook = nbformat.read(origen, as_version=4)
    # Evitar salidas históricas en celdas que esta ejecución no llega a ejecutar.
    for celda in notebook.cells:
        if celda.cell_type == "code":
            celda.outputs = []
            celda.execution_count = None
    manager = KernelManager(kernel_name="python3")
    manager.kernel_spec.argv[0] = sys.executable
    cliente = NotebookClient(
        notebook, km=manager, timeout=timeout, startup_timeout=60,
        allow_errors=False, record_timing=True,
        resources={"metadata": {"path": str(raiz)}},
    )
    try:
        cliente.execute(cleanup_kc=True)
    except BaseException:
        fallo.parent.mkdir(parents=True, exist_ok=True)
        nbformat.write(notebook, fallo)
        raise
    temporal = origen.with_suffix(".ipynb.tmp")
    try:
        nbformat.write(notebook, temporal)
        os.replace(temporal, origen)
    finally:
        if temporal.exists():
            temporal.unlink()


def ejecutar_secuencia(raiz, timeout=900):
    reporte = raiz / "reports" / "ejecucion" / "resumen.json"
    reporte.parent.mkdir(parents=True, exist_ok=True)
    resumen = {
        "inicio_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.executable, "timeout_por_celda_segundos": timeout,
        "estado": "en_ejecucion", "notebooks": [],
    }

    def guardar():
        reporte.write_text(json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8")
        generar_informe(raiz)

    guardar()
    for nombre in NOTEBOOKS:
        print(f"Ejecutando {nombre}...", flush=True)
        inicio = time.monotonic()
        etapa = {"notebook": nombre, "estado": "en_ejecucion"}
        resumen["notebooks"].append(etapa)
        guardar()
        try:
            ejecutar_notebook(
                raiz / "notebooks" / nombre, raiz,
                raiz / "reports" / "runs" / "fallos" / nombre, timeout,
            )
        except BaseException as error:
            etapa.update(estado="error", error=f"{type(error).__name__}: {error}")
            resumen["estado"] = "interrumpida" if isinstance(error, KeyboardInterrupt) else "error"
            etapa["duracion_segundos"] = round(time.monotonic() - inicio, 2)
            resumen["fin_utc"] = datetime.now(timezone.utc).isoformat()
            guardar()
            print(f"Se detuvo la secuencia en {nombre}. Revisa {reporte} y reports/runs/fallos/.", flush=True)
            return 1
        etapa.update(estado="completado", duracion_segundos=round(time.monotonic() - inicio, 2))
        guardar()
        print(f"Completado {nombre} ({etapa['duracion_segundos']} s)", flush=True)
    resumen.update(estado="completado", fin_utc=datetime.now(timezone.utc).isoformat())
    guardar()
    print("Los cinco notebooks terminaron sin errores de ejecución.", flush=True)
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", type=int, default=900, help="Límite por celda, en segundos.")
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error("El timeout debe ser positivo.")
    sys.exit(ejecutar_secuencia(Path(__file__).resolve().parents[1], args.timeout))
