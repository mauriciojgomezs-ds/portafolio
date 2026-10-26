"""Configuración común de avisos para los notebooks, sin imports de modelos."""

import warnings
import json
from html import escape
from pathlib import Path


_alertas = {}
_mostrar_original = warnings.showwarning
_descripciones = {
    "UndefinedMetricWarning": (
        "Una métrica no se puede calcular con los casos o predicciones disponibles.",
        "Revisar las clases presentes, la matriz de confusión y la convención zero_division.",
    ),
    "ConvergenceWarning": (
        "El algoritmo terminó sin alcanzar el criterio de convergencia solicitado.",
        "Revisar escalamiento, tolerancia y número de iteraciones antes de interpretar el modelo.",
    ),
    "RuntimeWarning": (
        "Una operación numérica encontró una condición que puede afectar el resultado.",
        "Revisar el mensaje original, divisiones por cero, nulos e infinitos.",
    ),
    "FutureWarning": (
        "Una biblioteca cambiará este comportamiento en una versión futura.",
        "Revisar la operación indicada y preparar su actualización; no prueba un fallo actual.",
    ),
    "DeprecationWarning": (
        "Se está utilizando una función o comportamiento en retirada.",
        "Consultar la alternativa indicada antes de actualizar dependencias.",
    ),
    "DataConversionWarning": (
        "La biblioteca tuvo que convertir el tipo o la forma de los datos.",
        "Comprobar tipos, dimensiones y que la conversión preserve el significado.",
    ),
    "UserWarning": (
        "La biblioteca señala una condición que conviene revisar.",
        "Leer el detalle original y comprobar cómo afecta esta etapa del análisis.",
    ),
}


def _registrar_aviso(message, category, filename, lineno, file=None, line=None):
    tipo = category.__name__
    clave = (tipo, str(message))
    descripcion, accion = _descripciones.get(tipo, _descripciones["UserWarning"])
    registro = _alertas.setdefault(clave, {
        "tipo": tipo, "mensaje": str(message), "descripcion": descripcion,
        "accion_sugerida": accion, "apariciones": 0, "origenes": [],
    })
    registro["apariciones"] += 1
    origen = f"{filename}:{lineno}"
    if origen not in registro["origenes"]:
        registro["origenes"].append(origen)


def obtener_alertas():
    """Devuelve una copia serializable de los avisos emitidos en este proceso."""
    return [dict(r, origenes=list(r["origenes"])) for r in _alertas.values()]


def configurar_notebook():
    """Inicia el registro tabulado de avisos; una nueva llamada lo vacía.

    Captura warnings del proceso actual, no excepciones, logs ni subprocesos.
    Los avisos se consultan con mostrar_alertas(), incluso tras una celda fallida.
    """
    _alertas.clear()
    warnings.showwarning = _registrar_aviso
    warnings.simplefilter("always", UserWarning)
    warnings.simplefilter("always", RuntimeWarning)
    warnings.simplefilter("always", DeprecationWarning)


def restaurar_avisos():
    """Devuelve la presentación de warnings a la función previa al registro."""
    warnings.showwarning = _mostrar_original


def mostrar_alertas(ruta=None):
    """Muestra el resumen, con el mensaje original, y opcionalmente guarda JSON."""
    from IPython.display import HTML, display

    registros = obtener_alertas()
    if ruta is not None:
        destino = Path(ruta)
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(json.dumps(registros, ensure_ascii=False, indent=2), encoding="utf-8")
    if not registros:
        display(HTML("<p><strong>Alertas de Python:</strong> no se registraron avisos en este proceso desde la configuración inicial. Esto no certifica que todos los controles hayan pasado.</p>"))
    else:
        filas = []
        for r in registros:
            origenes = "<br>".join(escape(o) for o in r["origenes"])
            detalle = f'<details><summary>Ver detalle y origen</summary><pre>{escape(r["mensaje"])}</pre>{origenes}</details>'
            filas.append("<tr>" + "".join(f"<td>{v}</td>" for v in (
                escape(r["tipo"]), str(r["apariciones"]), escape(r["descripcion"]),
                escape(r["accion_sugerida"]), detalle,
            )) + "</tr>")
        display(HTML(
            "<h3>Alertas de Python de esta ejecución</h3><p>Descripciones genéricas: revisa el detalle para determinar el impacto.</p>"
            "<table><thead><tr><th>Tipo</th><th>Veces</th><th>Qué significa</th><th>Qué revisar</th><th>Detalle original</th></tr></thead><tbody>"
            + "".join(filas) + "</tbody></table>"
        ))
    return None
