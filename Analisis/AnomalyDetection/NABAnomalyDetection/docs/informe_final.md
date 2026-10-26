# Informe integral del proyecto

La entrada principal es [reports/informe_final/informe_final.md](../reports/informe_final/informe_final.md). El [JSON complementario](../reports/informe_final/informe_final.json) contiene resultados disponibles, fechas, estados y huellas SHA-256 de las entradas utilizadas.

## Actualización automática

El maestro 06 y `python scripts/execute_notebooks.py` regeneran el informe al guardar el avance, al completar etapas, al terminar y ante un error de notebook. Así, una secuencia fallida muestra su estado y señala que pueden quedar resultados anteriores. La celda final de alertas de cada notebook 01–05 también regenera el informe. La celda de resumen de 06 permite actualizarlo y abrir su enlace.

Para reunir resultados después de ejecutar notebooks individuales, desde la carpeta del proyecto utiliza:

```powershell
python scripts/generate_report.py
```

Este comando reúne archivos existentes; no descarga datos ni entrena modelos. No necesita otro proyecto, una API o servicios de IA.

## Contenido y reglas

El informe incluye objetivo y configuración, datos preparados, hallazgos exploratorios, baseline, selección de modelos, evaluación, comparación de indicadores pertinentes, alertas, estado de notebooks, limitaciones y próximos pasos. Los comentarios originales de cada etapa se reutilizan; las cifras provienen de JSON y las comparaciones se recalculan. No se utilizan cifras fijas del README para evaluar el modelo.

Las comparaciones respetan la tarea: menor MAE/RMSE en pronóstico; mayor F1, recall, precision, average precision o NDCG cuando corresponde. Los indicadores de contenido y clustering se interpretan como descriptivos. La correlación conserva los criterios y umbrales del EDA.

Si una etapa no exporta reporte, aparece como no disponible. Un maestro incompleto se identifica explícitamente, y los archivos modificados después de su última pasada completa se señalan como actualizaciones por etapa. Completar un notebook no acredita utilidad ni una validación independiente. La tabla de celdas ejecutadas y los manifiestos sirven para revisar procedencia; no garantizan por sí solos que un modelo guardado corresponda a los datos actuales.

Cada regeneración reemplaza una única versión vigente del Markdown y JSON. Los reportes detallados por etapa se conservan en sus carpetas. Al copiar el proyecto completo, el comando sigue usando únicamente su `src/`, notebooks y reportes locales.
