# Registro de ejecución de SubscriptionChurn

## Pasada vigente

El maestro completó 01–05 el **6 de octubre de 2026, de 23:04:36 a 23:04:51**, en America/Santiago, en aproximadamente 15,03 segundos. El [resumen](../reports/ejecucion/resumen.json) guarda fechas UTC, intérprete y límite de 900 segundos por celda.

00 produjo su informe a las 23:04:20 locales. Sus imports y `pip check` pasaron; las versiones están en [environment.json](../reports/entorno/environment.json). Los reportes de alertas de 00–05 están vacíos.

| Etapa | Duración | Estado |
| --- | ---: | --- |
| 01 · Preparación | 2,73 s | Completado |
| 02 · EDA | 2,29 s | Completado |
| 03 · Baseline | 1,89 s | Completado |
| 04 · Modelado | 2,98 s | Completado |
| 05 · Evaluación | 5,13 s | Completado |

## Preparación y selección

Una fila del CSV de entrenamiento carece de objetivo y se descarta. El entrenamiento utilizable se divide en 352.665 registros de train y 88.167 de validación; los 64.374 registros del test suministrado se conservan. La preparación registra 50.320 IDs compartidos entre train y test.

La variante balanceada se selecciona por average precision de validación: 0,9739347608 frente a 0,9739336335 de la no ponderada. No se interpreta esta diferencia mínima como una superioridad estable. El modelo se ajustó solo en train.

## Resultados y revisión

Accuracy del modelo: 0,894586 en validación y 0,580995 en test. Average precision pasa de 0,973935 a 0,638912; ROC-AUC de 0,958971 a 0,688741.

La matriz de test, con filas reales y columnas predichas en orden 0/1, es `[[7288, 26593], [380, 30113]]`. Recall positivo: 0,987538; precisión positiva: 0,531037; recall negativo: 0,215106. El baseline predice siempre positivo y obtiene accuracy 0,473685.

La revisión descriptiva encontró diferencias entre train y test en soporte, retrasos de pago, gasto y contratos. Los valores se guardan en [auditoria_distribuciones.json](../reports/eda/auditoria_distribuciones.json). No se atribuye una causa definitiva a la caída y no se ajustaron modelos con test.

Se actualizaron README, metodología, cabeceras de notebooks y estado general. No se volvió a entrenar durante esta revisión. La definición del objetivo, fuente y significado de los IDs siguen pendientes; los resultados no son directamente comparables con BankChurn o ActivityChurn.

## Comprobación después de homologar

El 7 de octubre de 2026 se comprobaron el paquete local, las rutas a back, la apertura desde raíz/proyecto/notebooks y el comando de ejecución. Se reejecutaron 00 y 05 con los modelos existentes; no se volvió a entrenar ni se cambió el criterio de selección. El resumen del maestro mantiene la pasada completa anterior. Consulta el [registro de estructura](verificacion_estructura.json).

## Independencia de la carpeta de proyecto

Las fuentes se localizaron en data/raw y las instrucciones y registros se copiaron a docs. La comprobación de copia y renombrado está en [verificacion_independencia.json](verificacion_independencia.json); no implica una nueva selección de modelos.

## Reportes agrupados por etapa

El 7 de octubre de 2026 se agruparon los reportes por etapa y se actualizaron las rutas de generación y lectura. Se reejecutaron 00, 02, 05 para comprobar las nuevas rutas; las pruebas locales y los enlaces se comprobaron correctamente. No se reentrenaron los modelos de 03 y 04. El resumen del maestro conserva la pasada completa anterior. Consulta la [verificación de reportes](verificacion_reportes.json).
