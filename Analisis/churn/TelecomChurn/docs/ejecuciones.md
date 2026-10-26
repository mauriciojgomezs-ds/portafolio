# Registro de ejecución de TelecomChurn

## Pasada vigente

El maestro completó 01–05 el **7 de octubre de 2026, de 09:39:39 a 09:39:52**, en America/Santiago. El tiempo transcurrido fue aproximadamente 12,82 segundos. El [resumen](../reports/ejecucion/resumen.json) conserva fechas UTC, intérprete y límite de 900 segundos por celda.

El diagnóstico de 00 se generó a las 09:39:14 locales; los imports y `pip check` pasaron. Las versiones están en [environment.json](../reports/entorno/environment.json).

| Etapa | Duración | Estado |
| --- | ---: | --- |
| 01 · Preparación | 1,87 s | Completado |
| 02 · EDA | 2,13 s | Completado |
| 03 · Baseline | 5,08 s | Completado |
| 04 · Modelado | 1,88 s | Completado |
| 05 · Evaluación | 1,84 s | Completado |

No se encontraron salidas de error en 00–05 y los seis reportes de alertas están vacíos. Esto no acredita calidad predictiva ni valida el significado del objetivo.

## Resultados y límites

Se conservaron las 3.333 filas de origen. Las particiones son 2.132 de train, 534 de validación y 667 de test, con 310, 78 y 95 positivos respectivamente. No hay filas completas idénticas entre train/test o valid/test. La ausencia de ID impide verificar independencia por cliente.

Se eligió la regresión logística sin ponderación por average precision en validación: 0,356547 frente a 0,339699 de la variante balanceada. Esta última tiene mayor recall de validación (62,82 % frente a 21,79 %), con menor precisión (32,03 % frente a 42,50 %). No se escogió usando test.

El modelo obtiene en test accuracy 0,859070, average precision 0,421966 y ROC-AUC 0,811704. Recall positivo: 0,294737; precisión positiva: 0,509091. La matriz, con filas reales y columnas predichas en orden 0/1, es `[[545, 27], [67, 28]]`: 28 abandonos detectados, 67 omitidos y 27 falsas alertas.

El baseline predice siempre cero: accuracy 0,857571, average precision 0,142429, ROC-AUC 0,5 y recall positivo cero. La mejora de accuracy es 0,15 puntos porcentuales, aunque las métricas de ranking mejoran.

Se contrastaron entorno, preparación, validación, test, alertas y salidas guardadas. No se volvió a entrenar ni se cambió el criterio de selección. Los próximos ajustes de umbral deben estudiarse en validación y evaluarse con un protocolo que contemple que este test ya se ha observado. Procedencia pública, licencia, atribución a Orange y horizonte del churn siguen pendientes de confirmar.

## Comprobación después de homologar

El 7 de octubre de 2026 se comprobaron el paquete local, las rutas a back, la apertura desde raíz/proyecto/notebooks y el comando de ejecución. Se reejecutaron 00 y 05 con los modelos existentes; no se volvió a entrenar ni se cambió el criterio de selección. El resumen del maestro mantiene la pasada completa anterior. Consulta el [registro de estructura](verificacion_estructura.json).

## Independencia de la carpeta de proyecto

Las fuentes se localizaron en data/raw y las instrucciones y registros se copiaron a docs. La comprobación de copia y renombrado está en [verificacion_independencia.json](verificacion_independencia.json); no implica una nueva selección de modelos.

## Reportes agrupados por etapa

El 7 de octubre de 2026 se agruparon los reportes por etapa y se actualizaron las rutas de generación y lectura. Se reejecutaron 00, 02, 05 para comprobar las nuevas rutas; las pruebas locales y los enlaces se comprobaron correctamente. No se reentrenaron los modelos de 03 y 04. El resumen del maestro conserva la pasada completa anterior. Consulta la [verificación de reportes](verificacion_reportes.json).
