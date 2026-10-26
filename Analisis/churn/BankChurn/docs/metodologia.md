# Metodología: Bancario

10.000 registros y 14 columnas; target Exited. Se utiliza uno de los tres archivos bancarios idénticos.

Split estratificado 60/20/20. Se excluyen RowNumber, CustomerId y Surname. La variable Exited requiere documentar su ventana de observación en la fuente.

Las decisiones comunes, reportes y limitaciones se explican en la [metodología compartida](ejecucion.md).

## Primera ejecución completa

00 y la secuencia 01–05 terminaron el 6 de octubre de 2026. La regresión logística sin ponderar se seleccionó por average precision en validación. En los 2.000 registros de test obtiene accuracy 81,00 %, average precision 0,4806 y ROC-AUC 0,7752. El baseline obtiene accuracy 79,65 %. Consulta el [registro](ejecuciones.md) y los [resultados detallados](../reports/evaluacion/evaluacion_test.json).

El recall de churn es 19,41 %: detecta 79 de 407 casos y omite 328. La precisión positiva es 60,31 %. La mejora de accuracy no implica una detección suficiente para un caso de uso de retención. El criterio de selección por average precision y la decisión binaria cumplen funciones diferentes; cualquier ajuste de threshold debe seleccionarse en validación.
