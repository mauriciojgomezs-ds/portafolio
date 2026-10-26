# Estructura de NetflixRecommender

Este proyecto utiliza la organización de SmartFood: paquete propio, dependencias locales y notebooks que importan desde su `src/`.

```text
NetflixRecommender/
├── pyproject.toml
├── requirements.txt
├── config.json
├── src/netflix_recommender/
├── scripts/execute_notebooks.py
├── tests/
├── notebooks/00–06
├── data/raw, intermediate, processed, output
├── models/
├── reports/
└── docs/
```

Las funciones de análisis están en `src/netflix_recommender/`. `scripts/` contiene puntos de entrada; los notebooks no buscan funciones dentro de scripts. Las fuentes se resuelven desde este proyecto: `data/raw/Netflix Movies and TV Shows.zip`. Las rutas se mantienen al copiar el proyecto completo a otro lugar.

Desde esta carpeta, instala con `python -m pip install -r requirements.txt`. Ejecuta 00 y luego 06; el maestro mantiene sus tres celdas. Para ejecutar sin Jupyter abierto: `python scripts/execute_notebooks.py`. Para comprobar el código local: `python -m unittest discover -s tests -v`.

La reorganización conserva datos preparados, modelos y reportes históricos. Los resultados de la pasada anterior mantienen su fecha; las comprobaciones de esta migración se registran aparte. No se requiere `tools/src/portfolio_lab` ni `Analisis/churn/src/churn_portfolio` para ejecutar este proyecto.

Las entradas, instrucciones y verificaciones son propias de este proyecto: [fuentes](fuentes.md) y [ejecución](ejecucion.md).

## Organización de reportes

Los reportes se agrupan por etapa dentro de `reports/` y se generan con nombres estables. Repetir una etapa reemplaza sus archivos vigentes.

| Carpeta | Archivos vigentes |
| --- | --- |
| `alertas/` | `00_configuracion_entorno.json`, `01_preparacion_datos.json`, `02_analisis_exploratorio.json`, `03_baseline.json`, `04_modelado.json`, `05_evaluacion.json`, `06_ejecucion_completa.json` |
| `baseline/` | `baseline.json`, `baseline.md` |
| `eda/` | `eda.json`, `eda.md`, `eda.png` |
| `ejecucion/` | `resumen.json` |
| `entorno/` | `environment.json` |
| `evaluacion/` | `evaluacion.json`, `evaluacion.md` |
| `modelado/` | `modelado.json`, `modelado.md` |
| `preparacion/` | `preparacion.json`, `preparacion.md` |

Las copias parciales de fallos se conservan en `runs/fallos/`. Revisa `ejecucion/resumen.json` para distinguir una secuencia completa de ejecuciones parciales. Cada proyecto crea sus carpetas localmente y conserva su independencia.

## Informe integral

Consulta el [informe integral](../reports/informe_final/informe_final.md). Se actualiza con 06 y reúne cifras, conclusiones, limitaciones y próximos pasos. Para regenerarlo con resultados existentes usa `python scripts/generate_report.py`. Consulta la [guía del informe](informe_final.md).
