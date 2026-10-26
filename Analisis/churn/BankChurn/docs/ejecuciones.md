# Registro de ejecución de BankChurn

## Pasada vigente

El maestro completó 01–05 el **6 de octubre de 2026, de 23:01:12 a 23:01:21**, en America/Santiago. El tiempo transcurrido fue aproximadamente 9,62 segundos. El [resumen](../reports/ejecucion/resumen.json) guarda fechas UTC, intérprete y límite de 900 segundos por celda.

El diagnóstico de 00 se generó a las 23:00:52 locales; sus imports y `pip check` pasaron. Las versiones exactas están en [environment.json](../reports/entorno/environment.json).

| Etapa | Duración | Estado |
| --- | ---: | --- |
| 01 · Preparación | 1,89 s | Completado |
| 02 · EDA | 2,15 s | Completado |
| 03 · Baseline | 1,83 s | Completado |
| 04 · Modelado | 1,88 s | Completado |
| 05 · Evaluación | 1,85 s | Completado |

No se encontraron salidas de error en 00–05 y los seis reportes de alertas están vacíos. Esto no valida semánticamente el objetivo o las features.

## Resultados

La preparación conserva las 10.000 filas y genera 6.000 de train, 2.000 de validación y 2.000 de test. No hay IDs compartidos entre train y test. El target positivo representa 20,35 % del test.

Se eligió la regresión logística sin ponderación por average precision en validación: 0,463021 frente a 0,455291 de la versión balanceada. Esta elección no optimiza directamente el recall de churn ni un coste de negocio.

El test obtiene accuracy 0,81, average precision 0,480620 y ROC-AUC 0,775208. La matriz, con filas reales y columnas predichas en orden 0/1, es `[[1541, 52], [328, 79]]`. Recall positivo: 0,194103; precisión positiva: 0,603053.

El baseline predice siempre cero: accuracy 0,7965, average precision 0,2035, ROC-AUC 0,5 y recall positivo cero. La mejora en accuracy es 1,35 puntos porcentuales, con 328 casos de churn todavía omitidos por el modelo.

## Alcance de esta revisión

Se contrastaron preparación, entorno, validación, test, alertas y resumen, y se actualizó la documentación. No se volvió a entrenar ni se cambió el criterio de selección. Ajustar un threshold o cambiar el objetivo de selección requiere validación y una estrategia de evaluación independiente; la comparación directa con ActivityChurn no establece cuál modelo es mejor porque sus poblaciones y particiones son distintas.

## Comprobación después de homologar

El 7 de octubre de 2026 se comprobaron el paquete local, las rutas a back, la apertura desde raíz/proyecto/notebooks y el comando de ejecución. Se reejecutaron 00 y 05 con los modelos existentes; no se volvió a entrenar ni se cambió el criterio de selección. El resumen del maestro mantiene la pasada completa anterior. Consulta el [registro de estructura](verificacion_estructura.json).

## Independencia de la carpeta de proyecto

Las fuentes se localizaron en data/raw y las instrucciones y registros se copiaron a docs. La comprobación de copia y renombrado está en [verificacion_independencia.json](verificacion_independencia.json); no implica una nueva selección de modelos.

## Reportes agrupados por etapa

El 7 de octubre de 2026 se agruparon los reportes por etapa y se actualizaron las rutas de generación y lectura. Se reejecutaron 00, 02, 05 para comprobar las nuevas rutas; las pruebas locales y los enlaces se comprobaron correctamente. No se reentrenaron los modelos de 03 y 04. El resumen del maestro conserva la pasada completa anterior. Consulta la [verificación de reportes](verificacion_reportes.json).
