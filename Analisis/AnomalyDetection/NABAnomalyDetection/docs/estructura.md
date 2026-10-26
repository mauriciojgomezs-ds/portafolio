# Estructura de NABAnomalyDetection

Este proyecto utiliza la organización de SmartFood: paquete propio, dependencias locales y notebooks que importan desde su `src/`.

```text
NABAnomalyDetection/
├── pyproject.toml
├── requirements.txt
├── config.json
├── src/nab_anomaly_detection/
├── scripts/execute_notebooks.py
├── tests/
├── notebooks/00–06
├── data/raw, intermediate, processed, output
├── models/
├── reports/
└── docs/
```

Las funciones de análisis están en `src/nab_anomaly_detection/`. `scripts/` contiene puntos de entrada; los notebooks no buscan funciones dentro de scripts. Las fuentes se resuelven desde este proyecto: `data/raw/NAB.zip`. Las rutas se mantienen al copiar el proyecto completo a otro lugar.

Desde esta carpeta, instala con `python -m pip install -r requirements.txt`. Ejecuta 00 y luego 06; el maestro mantiene sus tres celdas. Para ejecutar sin Jupyter abierto: `python scripts/execute_notebooks.py`. Para comprobar el código local: `python -m unittest discover -s tests -v`.

La reorganización conserva datos preparados, modelos y reportes históricos. Los resultados de la pasada anterior mantienen su fecha; las comprobaciones de esta migración se registran aparte. No se requiere `tools/src/portfolio_lab` ni `Analisis/churn/src/churn_portfolio` para ejecutar este proyecto.

Las entradas, instrucciones y verificaciones son propias de este proyecto: [fuentes](fuentes.md) y [ejecución](ejecucion.md).

## Organización de reportes

Cada etapa guarda sus resultados en una carpeta propia dentro de `reports/`:

| Carpeta | Contenido |
| --- | --- |
| `entorno/` | `environment.json`: versiones y comprobación de dependencias |
| `preparacion/` | `preparacion.json` y `preparacion.md` |
| `eda/` | `eda.json`, `eda.md` y `eda.png` |
| `baseline/` | `baseline.json` y `baseline.md` |
| `modelado/` | `modelado.json` y `modelado.md` |
| `evaluacion/` | `evaluacion.json`, `evaluacion.md`, `evaluacion.png` y `predicciones_test.csv` |
| `alertas/` | Avisos y descripciones por notebook |
| `ejecucion/` | `resumen.json` del maestro |
| `runs/fallos/` | Copias parciales de notebooks, solo si una ejecución falla |

Las carpetas se crean automáticamente cuando cada etapa escribe sus reportes. Los nombres estables conservan una versión vigente por archivo; revisa el resumen del maestro para comprobar que todas las etapas terminaron en la misma pasada.

## Informe integral

Consulta el [informe integral](../reports/informe_final/informe_final.md). Se actualiza con 06 y reúne cifras, conclusiones, limitaciones y próximos pasos. Para regenerarlo con resultados existentes usa `python scripts/generate_report.py`. Consulta la [guía del informe](informe_final.md).
