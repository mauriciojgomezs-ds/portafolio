# Anomalías en temperatura de una máquina
![Python](https://img.shields.io/badge/python-3.10%2B-blue) ![scikit--learn](https://img.shields.io/badge/scikit--learn-1.3%2B-orange) ![estado](https://img.shields.io/badge/estado-completado-brightgreen)

Detectar desviaciones en una serie de temperatura de máquina del benchmark NAB.

## Método y alcance

Serie realKnownCause/machine_temperature_system_failure.csv; split cronológico 60/20/20. Media y escala de 48 observaciones anteriores; umbrales candidatos por cuantiles de train, seleccionados por F1 de validación.

Precisión, recall, F1 y matriz por punto usando las ventanas oficiales de etiquetas. No es la puntuación oficial NAB ni una evaluación de eventos independientes; una avería puede generar muchos puntos alertados.

## Cómo ejecutar

Abre [00 · Entorno](notebooks/00_configuracion_entorno.ipynb) desde la carpeta del proyecto y selecciona tu Python. Tras comprobar el entorno, guarda y cierra 01–05 y ejecuta [06 · Maestro](notebooks/06_ejecucion_completa.ipynb). También puedes ejecutar las etapas por separado y en orden. El maestro tiene tres celdas de código.

| Notebook | Función |
| --- | --- |
| 01_preparacion_datos | Limpieza, partición cronológica y controles |
| 02_analisis_exploratorio | Distribuciones y gráfico de la serie |
| 03_baseline | Referencia sin alertas |
| 04_modelado | Selección de umbral por F1 de validación |
| 05_evaluacion | Evaluación por punto y limitaciones |

![Serie de temperatura con umbral de alerta y tramo de validación](reports/eda/eda.png)

La fuente está definida en [config.json](config.json) y se lee desde su propio `data/raw/`. Este proyecto incluye su propio `pyproject.toml` y `requirements.txt`. Los datos preparados y modelos se guardan dentro del proyecto.

## Evidencia

Las etapas generan JSON y Markdown con cifras y conclusiones automáticas: `preparacion`, `eda`, `baseline`, `modelado` y `evaluacion`. Se añade una figura de EDA, alertas por notebook y resumen de ejecución del maestro. La última [evaluación](reports/evaluacion/evaluacion.md) y el [resumen de ejecución](reports/ejecucion/resumen.json) estarán disponibles después de ejecutar 01–05; no se inventan resultados antes de correrlos.

Los reportes usan nombres estables. Repetir la ejecución reemplaza esos archivos; un fallo puede dejar reportes de etapas anteriores, así que debe revisarse siempre el resumen del maestro. Los ZIP, datos procesados y modelos no se versionan. La procedencia y condiciones de uso se contrastan con el [inventario](docs/fuentes.md) antes de publicar.

Consulta la [metodología propia](docs/metodologia.md) y la [guía de ejecución local](docs/ejecucion.md).

## Estructura local

Consulta la [estructura y comandos del proyecto](docs/estructura.md). Las funciones se importan desde su propio `src/`; los requisitos se instalan desde esta carpeta. Los datos de entrada están en `data/raw` y sus rutas se declaran en `config.json`.

## Independencia

El proyecto incluye su código, requisitos, datos de entrada e instrucciones. Se puede copiar o renombrar conservando esta carpeta completa; la ejecución no utiliza otros proyectos ni una carpeta temática. Los datos están excluidos del versionado: consulta las [fuentes](docs/fuentes.md) para preparar una copia nueva.

Los reportes se agrupan por etapa en `reports/entorno`, `preparacion`, `eda`, `baseline`, `modelado` y `evaluacion`. Consulta el [contenido de cada carpeta](docs/estructura.md#organización-de-reportes).

## Informe integral

Consulta el [informe integral](reports/informe_final/informe_final.md). Se actualiza con 06 y reúne cifras, conclusiones, limitaciones y próximos pasos. Para regenerarlo con resultados existentes usa `python scripts/generate_report.py`. Consulta la [guía del informe](docs/informe_final.md).
