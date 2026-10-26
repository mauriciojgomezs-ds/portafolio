# Registro de ejecución de ActivityChurn

## Pasada vigente

El 6 de octubre de 2026, de 22:59:57 a 23:00:13 en America/Santiago, el maestro completó 01–05 en aproximadamente 16,02 segundos. El [resumen](../reports/ejecucion/resumen.json) registra las fechas en UTC, Python 3.14 y un límite de 900 segundos por celda. El informe de entorno identifica la versión activa como la instalación Python 3.14; los notebooks se ejecutaron con Python 3.14.4.

El notebook 00 generó el diagnóstico a las 22:59:33 locales. Sus imports terminaron y `pip check` pasó. Las versiones exactas están en [environment.json](../reports/entorno/environment.json).

| Etapa | Duración | Estado |
| --- | ---: | --- |
| 01 · Preparación | 5,12 s | Completado |
| 02 · EDA | 2,18 s | Completado |
| 03 · Baseline | 1,83 s | Completado |
| 04 · Modelado | 5,07 s | Completado |
| 05 · Evaluación | 1,82 s | Completado |

Las seis tablas de alertas de 00–05 están vacías. La ausencia de warnings no acredita una validación semántica de la fuente o de las variables.

## Resultados y alcance

La preparación conserva las 5.496 filas, sin objetivos ausentes. Las particiones temporales contienen 4.742, 451 y 303 registros respectivamente. El [reporte de preparación](../reports/preparacion/preparacion.json) incluye la huella SHA-256 y 185 IDs compartidos entre entrenamiento y test.

Se eligió la regresión logística sin ponderación por average precision en validación (0,857134 frente a 0,856209 de la ponderada). El modelo se ajustó en train y no se reentrenó utilizando validación antes del test.

En test obtiene accuracy 0,772277, average precision 0,821799 y ROC-AUC 0,837407. Su matriz de confusión, con filas reales y columnas predichas en orden 0/1, es `[[113, 37], [32, 121]]`. El baseline obtiene accuracy 0,495050 y ROC-AUC 0,5; predice siempre cero.

Los datos corresponden a abril de 2025. Estos resultados no estiman por sí solos el comportamiento en otros meses o para usuarios nuevos. Deben confirmarse la definición temporal del target y de las features antes de presentar el modelo como una predicción prospectiva validada.

## Documentación actualizada

Se contrastaron los reportes de entorno, preparación, validación, test, alertas y ejecución. Se actualizaron README, metodología y estado del proyecto. No se volvió a entrenar el modelo durante esta revisión.

## Comprobación después de homologar

El 7 de octubre de 2026 se comprobaron el paquete local, las rutas a back, la apertura desde raíz/proyecto/notebooks y el comando de ejecución. Se reejecutaron 00 y 05 con los modelos existentes; no se volvió a entrenar ni se cambió el criterio de selección. El resumen del maestro mantiene la pasada completa anterior. Consulta el [registro de estructura](verificacion_estructura.json).

## Independencia de la carpeta de proyecto

Las fuentes se localizaron en data/raw y las instrucciones y registros se copiaron a docs. La comprobación de copia y renombrado está en [verificacion_independencia.json](verificacion_independencia.json); no implica una nueva selección de modelos.

## Reportes agrupados por etapa

El 7 de octubre de 2026 se agruparon los reportes por etapa y se actualizaron las rutas de generación y lectura. Se reejecutaron 00, 02, 05 para comprobar las nuevas rutas; las pruebas locales y los enlaces se comprobaron correctamente. No se reentrenaron los modelos de 03 y 04. El resumen del maestro conserva la pasada completa anterior. Consulta la [verificación de reportes](verificacion_reportes.json).
