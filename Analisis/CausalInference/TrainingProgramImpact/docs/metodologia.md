# Metodología y límites

La pregunta es el efecto de la **asignación** a un programa de capacitación sobre ingresos de 1978. Se usa únicamente la submuestra experimental NSW Dehejia–Wahba con ingresos previos RE74. Incluye tratados y controles experimentales, sin mezclar controles observacionales CPS/PSID. No se deduplican individuos por tener atributos iguales. Los ingresos son USD nominales de esos años.

Estimando: efecto promedio de asignación en esta muestra seleccionada. No se estima el efecto por completar capacitación ni un efecto para todos los trabajadores. La interpretación causal requiere que la asignación experimental y la selección de esta submuestra mantengan comparabilidad, además de consistencia y ausencia de interferencia.

No se crean train/valid/test: se estima un contraste sobre participantes del experimento. 02 describe covariables pretratamiento mediante diferencias estandarizadas; |SMD| > 0,10 es una referencia descriptiva, no una prueba de aleatoriedad. 03 estima diferencia de medias y un intervalo Welch. 04 estima un ajuste OLS de tipo Lin: covariables centradas, asignación e interacciones asignación × covariables, con errores robustos HC3 e intervalo basado en t con n−p grados de libertad. Se declara antes de comparar efectos; no se elige el método que produce significancia.

Solo se usan age, education, black, hispanic, married, nodegree, re74 y re75 como ajustes previos. RE78 es exclusivamente resultado. El coeficiente de asignación corresponde al contraste en el promedio centrado de estas covariables.

05 usa 1.000 réplicas bootstrap estratificadas por brazo, preservando sus tamaños y recalculando el ajuste y centrado. Se registran réplicas sin rango completo y el proceso falla si superan 5 %. Los intervalos percentiles son una comprobación adicional de incertidumbre, no una garantía exacta ni un efecto verdadero conocido. Se muestran estimadores e intervalos sin comparar accuracy o afirmar que un efecto mayor sea mejor.

El conjunto es histórico, pequeño y seleccionado; no demuestra impacto en programas actuales. El ajuste puede ser sensible a observaciones influyentes y a la forma del modelo. La incertidumbre estadística no elimina errores de medición, problemas de selección ni límites de generalización.

## Referencia metodológica

[Lin (2013), ajuste por regresión en experimentos](https://arxiv.org/abs/1208.2301).
