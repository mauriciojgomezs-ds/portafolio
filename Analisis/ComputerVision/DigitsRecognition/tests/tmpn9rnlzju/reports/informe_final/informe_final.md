# Informe integral · tmpn9rnlzju

Generado: 2026-10-26T13:55:19.079599+00:00 (UTC).

Estado del informe: **Ejecución no completada**. Estado del último maestro: **error**.

Este documento reúne los archivos guardados; no ejecuta modelos ni certifica su utilidad. Las fechas y huellas del manifiesto permiten revisar su procedencia.

La secuencia no consta como completada. Los resultados de etapas no terminadas pueden proceder de una pasada anterior; no los interpretes como resultados de esta secuencia.

Etapas sin reporte exportado: **preparacion, eda, baseline, modelado**.

## Objetivo y configuración

Consulta el README del proyecto para el contexto y el objetivo.

## Datos y preparación

No hay un reporte exportado de esta etapa. Consulta su notebook; esta ausencia no implica que nunca se haya ejecutado.

## Hallazgos exploratorios

No hay un reporte exportado de esta etapa. Consulta su notebook; esta ausencia no implica que nunca se haya ejecutado.

## Baseline

No hay un reporte exportado de esta etapa. Consulta su notebook; esta ausencia no implica que nunca se haya ejecutado.

## Modelo y selección

No hay un reporte exportado de esta etapa. Consulta su notebook; esta ausencia no implica que nunca se haya ejecutado.

## Evaluación y conclusiones

Indicadores de [evaluacion.json](../../reports/evaluacion/evaluacion.json):

| Indicador | Valor |
| --- | --- |
| modelo / accuracy | 0.9 |

## Alertas y estado de ejecución

No hay inventarios de alertas disponibles.

Una tabla vacía de warnings no demuestra ausencia de errores o validez del modelo. Consulta [alertas](../alertas/) y [resumen del maestro](../ejecucion/resumen.json).

| Notebook | Celdas ejecutadas guardadas | Última ejecución UTC | Errores guardados |
| --- | --- | --- | --- |


## Limitaciones y próximos pasos

Benchmark cerrado con imágenes 8×8 e intensidades 0–16. Intensidad y gradientes con SVM no constituyen OCR completo. No se puede verificar independencia por escritor. El desplazamiento artificial mide sensibilidad concreta y no robustez general.

- Revisar fuentes, protocolo y alertas de la ejecución.
- Estudiar centrado y aumento de imágenes usando train y validación; reservar una evaluación nueva para las siguientes decisiones.

## Evidencia y reproducción

Desde la carpeta de este proyecto, ejecuta `python scripts/generate_report.py` para reunir los resultados guardados, o 06 para ejecutar los análisis y actualizar el informe.

Consulta el [README](../../README.md), la [guía del informe](../../docs/informe_final.md) y el [manifiesto con datos y huellas](informe_final.json). El informe conserva una versión vigente por proyecto.
