# Metodología: Actividad

5.496 filas, 43 columnas, 2.251 usuarios y 14 fechas; target flagChurn. El dominio SaaS mencionado en el ZIP queda por confirmar.

Train utiliza fechas hasta febrero de 2025, validación marzo y test abril. Se excluyen idUsuario, dtRef y qtdeChurn. Antes de afirmar una predicción futura valida hay que confirmar horizonte de churn y disponibilidad temporal de las variables.

Las decisiones comunes, reportes y limitaciones se explican en la [metodología compartida](ejecucion.md).

## Primera ejecución completa

La secuencia 01–05 terminó el 6 de octubre de 2026. Se seleccionó regresión logística sin ponderación por average precision en validación. La evaluación de abril de 2025 obtiene accuracy 77,23 %, average precision 0,8218 y ROC-AUC 0,8374 sobre 303 registros. El baseline mayoritario obtiene accuracy 49,50 %. Consulta el [registro de ejecución](ejecuciones.md) y los [resultados](../reports/evaluacion/evaluacion_test.json).

185 IDs de entrenamiento reaparecen en test; el protocolo permite usuarios conocidos en meses posteriores. La interpretación prospectiva todavía requiere confirmar cuándo estaban disponibles los atributos y qué intervalo define el churn. La mejora sobre el baseline es descriptiva de este test, sin una estimación de estabilidad en otros meses.
