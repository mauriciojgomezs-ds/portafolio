# Análisis de redes y comunidades
![Python](https://img.shields.io/badge/python-3.11%2B-blue) ![networkx](https://img.shields.io/badge/networkx-3.2%2B-orange) ![estado](https://img.shields.io/badge/estado-completado-brightgreen)

Explorar estructura de comunicación, detectar comunidades y contrastar su estabilidad y correspondencia con departamentos.

Proyecto independiente, con comentarios calculados, alertas tabuladas y reportes por etapa.

## Ejecutar

Desde esta carpeta, con Python 3.11 o superior:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
```

Selecciona ese Python como kernel. Ejecuta [00](notebooks/00_configuracion_entorno.ipynb) y después las tres celdas de [06](notebooks/06_ejecucion_completa.ipynb), que recorren 01–05. Si 00 instala bibliotecas, reinicia el kernel y repite la comprobación. Guarda y cierra 01–05 antes de ejecutar el maestro. Desde terminal: `python scripts/execute_notebooks.py`.

| Etapa | Propósito |
| --- | --- |
| 01 | Fuente, controles y preparación |
| 02 | Distribuciones y diagnóstico |
| 03 | Componentes conexas como referencia |
| 04 | Louvain con parámetros fijados |
| 05 | Departamentos y estabilidad entre semillas |

![Distribución de grados y estructura de la red de comunicación en el EDA](reports/eda/eda.png)

## Resultados y documentación

- [Informe integral automático](reports/informe_final/informe_final.md).
- [Metodología y límites](docs/metodologia.md).
- [Fuentes y recuperación](docs/fuentes.md).
- [Estructura autónoma](docs/estructura.md).
- [Guía del informe](docs/informe_final.md).
- `reports/ejecucion/resumen.json`: avance y tiempos del maestro.
- `reports/alertas`: mensajes originales y descripciones genéricas.

Con resultados guardados, `python scripts/generate_report.py` regenera el informe sin recalcular modelos. Tests: `python -m unittest discover -s tests -v`. Cada proyecto conserva una versión vigente por reporte. Se puede copiar o renombrar con sus fuentes y crear un entorno nuevo sin los demás proyectos.

Los resultados describen la misma red, sin evaluación predictiva fuera de muestra.
