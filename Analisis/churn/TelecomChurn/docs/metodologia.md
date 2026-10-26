# Metodología: Telecomunicaciones

2.666 filas en el archivo de entrenamiento/validación y 667 en el archivo de test suministrado; target Churn, booleano convertido a 0/1. No hay ID de cliente en las columnas.

Se preserva el test suministrado (`churn-bigml-20.csv`); del archivo `churn-bigml-80.csv` se reserva 20 % para validación con estratificación y semilla 42. `Area code` se trata como categoría y los cuatro cargos por periodo se excluyen de las features por su redundancia con los minutos (correlación superior a 0,99999). La procedencia pública, atribución a Orange, licencia y horizonte de churn quedan pendientes de registrar.

Las decisiones comunes, reportes y limitaciones se explican en la [metodología compartida](ejecucion.md).

## Primera ejecución completa

00 y la secuencia 01–05 terminaron el 7 de octubre de 2026. Se seleccionó la regresión logística sin ponderación por average precision en validación (0,3565 frente a 0,3397). En los 667 registros de test obtiene accuracy 85,91 %, average precision 0,4220 y ROC-AUC 0,8117. El baseline mayoritario obtiene accuracy 85,76 % con recall de churn 0 %. Consulta el [registro de ejecución](ejecuciones.md) y los [resultados](../reports/evaluacion/evaluacion_test.json).

El modelo detecta 28 de los 95 abandonos y genera 27 falsas alertas (matriz `[[545, 27], [67, 28]]`). No se encontraron filas completas idénticas entre train/test ni valid/test, pero al no existir ID de cliente esa ausencia no prueba independencia por persona. La proporción positiva es de aproximadamente 14,5 % en ambos archivos, por lo que accuracy debe acompañarse siempre de recall y average precision; el criterio de selección no optimiza directamente recall ni costes de intervención, y cualquier ajuste de threshold debe decidirse en validación, no sobre el test ya observado.
