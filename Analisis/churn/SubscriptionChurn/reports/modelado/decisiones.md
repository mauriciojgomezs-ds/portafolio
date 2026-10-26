# Calibración y política de decisión

Modelo adicional: **264498 filas para ajuste** y **88167 para calibración**. Separación 75/25 por ID de cliente dentro de train. Se comparan dos ponderaciones por AP de validación; calibración sigmoid fijada de antemano. El umbral **0.18** minimiza coste ilustrativo FN=5.0, FP=1.0 en la grilla de validación. Se conserva el modelo original para su comparación histórica; las métricas de decisiones corresponden a este ajuste adicional. Validación selecciona modelo y umbral: su rendimiento es optimista y el test queda reservado.
