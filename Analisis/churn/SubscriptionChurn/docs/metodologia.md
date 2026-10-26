# Metodología: Suscripciones

440.833 filas de entrenamiento y 64.374 de prueba; target Churn. Hay una fila de entrenamiento sin objetivo.

Se preserva test y se reserva un 20 % del entrenamiento para validación. CustomerID se excluye. La coincidencia de IDs no debe interpretarse automáticamente como el mismo cliente sin confirmar su significado.

Las decisiones comunes, reportes y limitaciones se explican en la [metodología compartida](ejecucion.md).

## Primera ejecución completa

00 y 01–05 terminaron el 6 de octubre de 2026. Se seleccionó regresión logística balanceada por average precision de validación, con una ventaja mínima sobre la variante sin ponderar. La accuracy pasa de 89,46 % en validación a 58,10 % en test. En test obtiene average precision 0,6389 y ROC-AUC 0,6887; el baseline tiene accuracy 47,37 %.

El recall de churn alcanza 98,75 %, pero la precisión positiva es 53,10 % y se generan 26.593 falsas alertas. Los archivos presentan diferencias descriptivas y hay 50.320 IDs compartidos entre train y test. Debe verificarse su significado y la procedencia de ambas fuentes antes de atribuir la caída a una causa específica o asumir independencia. Consulta el [registro](ejecuciones.md) y la [auditoría descriptiva](../reports/eda/auditoria_distribuciones.json).
