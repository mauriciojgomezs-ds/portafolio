# Anomalías industriales en sensores
![Python](https://img.shields.io/badge/python-3.10%2B-blue) ![scikit--learn](https://img.shields.io/badge/scikit--learn-1.3%2B-orange) ![estado](https://img.shields.io/badge/estado-completado-brightgreen)

Detectar observaciones de sensores compatibles con fallos en el benchmark sintético AI4I y comparar la calidad de las alertas de z-scores e Isolation Forest. Incluye análisis por etapas, comentarios calculados, alertas tabuladas e informe final automático.

AI4I 2020, UCI. Fuente sintética de 10.000 filas; no corresponde a una planta industrial. Se excluyen IDs y todas las etiquetas de fallo como entradas. La descarga conserva el ZIP original y registra su SHA-256.

## Ejecutar

Abre esta carpeta como proyecto y selecciona su entorno de Python. Python 3.10 o superior, con versiones compatibles de las dependencias.

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
```

Selecciona `.venv` como kernel. Ejecuta [00_configuracion_entorno](notebooks/00_configuracion_entorno.ipynb) para comprobar bibliotecas y preparar la fuente. Después ejecuta [06_ejecucion_completa](notebooks/06_ejecucion_completa.ipynb): sus tres celdas recorren 01–05 en orden. Si 00 instala dependencias, reinicia el kernel antes de continuar. Desde terminal también puedes usar `python scripts/execute_notebooks.py` con ese mismo entorno.

| Notebook | Función |
| --- | --- |
| 01_preparacion_datos | Limpieza, controles y datos locales |
| 02_analisis_exploratorio | Distribuciones y gráficos |
| 03_baseline | Referencia inicial |
| 04_modelado | Ajuste y selección con validación |
| 05_evaluacion | Evaluación reservada y limitaciones |

![Distribución de variables de sensores y alertas detectadas en el EDA](reports/eda/eda.png)

## Resultados y documentación

- [Informe integral](reports/informe_final/informe_final.md): entrada principal con cifras y conclusiones vigentes.
- [Metodología](docs/metodologia.md): protocolo, supuestos y alcance.
- [Fuentes](docs/fuentes.md): procedencia y recuperación.
- [Cómo actualizar el informe](docs/informe_final.md).
- `reports/ejecucion/resumen.json`: estado y tiempos de los cinco notebooks.
- `reports/alertas/`: avisos de Python agrupados, con significado genérico y detalle original.
- `reports/evaluacion/`: métricas, predicciones y evidencia gráfica.

Los comentarios se generan con las métricas de cada ejecución. Un error detiene el maestro y el informe identifica etapas incompletas; ausencia de avisos no equivale a validación. Reejecutar reemplaza la versión vigente, por lo que conviene conservar una versión concreta mediante Git antes de cambiar configuración o fuentes.

## Estructura e independencia

`src/industrial_anomaly_detection` contiene todas las funciones del proyecto; `scripts` sus entradas de ejecución; `tests` los controles; `data/raw` las fuentes; `data/processed` las transformaciones; `models` los modelos propios. `reports` se divide en entorno, preparación, EDA, baseline, modelado, evaluación, alertas, ejecución e informe final. Los notebooks se pueden abrir desde la carpeta del proyecto o desde notebooks.

Puedes copiar o renombrar esta carpeta con sus datos locales. No requiere otros proyectos, la carpeta temática ni `back`. Para comprobar controles: `python -m unittest discover -s tests`. Para reunir reportes existentes sin repetir el análisis: `python scripts/generate_report.py`.
