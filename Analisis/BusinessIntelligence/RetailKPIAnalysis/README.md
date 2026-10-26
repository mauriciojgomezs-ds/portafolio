# Indicadores y ajustes de retail
![Python](https://img.shields.io/badge/python-3.10%2B-blue) ![scikit--learn](https://img.shields.io/badge/scikit--learn-1.3%2B-orange) ![estado](https://img.shields.io/badge/estado-completado-brightgreen)

Explicar la facturación de un comercio mediante indicadores reconciliables de importes positivos, ajustes negativos y neta, con evolución mensual y desglose por país. Incluye análisis por etapas, comentarios calculados, alertas tabuladas e informe final automático.

Online Retail, UCI. Facturas entre diciembre de 2010 y diciembre de 2011, en libras esterlinas (GBP). Cantidades negativas se conservan como ajustes, sin afirmar que cada una sea una devolución de un pedido identificado. Copia local independiente de la utilizada en otros proyectos.

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
| 04_modelado | Indicadores y dashboard |
| 05_evaluacion | Reconciliación de indicadores |

![Distribución de importes y ajustes analizados en el EDA](reports/eda/eda.png)

## Resultados y documentación

- [Informe integral](reports/informe_final/informe_final.md): entrada principal con cifras y conclusiones vigentes.
- [Metodología](docs/metodologia.md): protocolo, supuestos y alcance.
- [Fuentes](docs/fuentes.md): procedencia y recuperación.
- [Cómo actualizar el informe](docs/informe_final.md).
- `reports/ejecucion/resumen.json`: estado y tiempos de los cinco notebooks.
- `reports/alertas/`: avisos de Python agrupados, con significado genérico y detalle original.
- [Dashboard local](reports/modelado/dashboard.html): indicadores mensuales y filtro de países.
- [Estructura del proyecto](docs/estructura.md): organización de carpetas y paquete.
- [Primera ejecución verificada](docs/resultados_iniciales.md): ficha histórica de referencia.

Los comentarios se generan con las métricas de cada ejecución. Un error detiene el maestro y el informe identifica etapas incompletas; ausencia de avisos no equivale a validación. Reejecutar reemplaza la versión vigente, por lo que conviene conservar una versión concreta mediante Git antes de cambiar configuración o fuentes.

## Estructura e independencia

`src/retail_kpi_analysis` contiene todas las funciones del proyecto; `scripts` sus entradas de ejecución; `tests` los controles; `data/raw` las fuentes; `data/processed` las transformaciones; `models` los modelos propios. `reports` se divide en entorno, preparación, EDA, baseline, modelado, evaluación, alertas, ejecución e informe final. Los notebooks se pueden abrir desde la carpeta del proyecto o desde notebooks.

Puedes copiar o renombrar esta carpeta con sus datos locales. No requiere otros proyectos, la carpeta temática ni `back`. Para comprobar controles: `python -m unittest discover -s tests`. Para reunir reportes existentes sin repetir el análisis: `python scripts/generate_report.py`.
