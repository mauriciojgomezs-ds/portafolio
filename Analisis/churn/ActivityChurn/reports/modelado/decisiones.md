# Calibración y política de decisión

Modelo adicional: **4368 filas para ajuste** y **374 para calibración**. Última fecha de train para calibración; ajuste solo fechas anteriores. Se comparan dos ponderaciones por AP de validación; calibración sigmoid fijada de antemano. El umbral **0.32** minimiza coste ilustrativo FN=5.0, FP=1.0 en la grilla de validación. Se conserva el modelo original para su comparación histórica; las métricas de decisiones corresponden a este ajuste adicional. Validación selecciona modelo y umbral: su rendimiento es optimista y el test queda reservado.
