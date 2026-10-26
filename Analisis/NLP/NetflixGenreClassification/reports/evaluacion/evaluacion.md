# Categorías de películas desde su sinopsis: evaluacion

En **1,222 textos de test**, el modelo obtiene **F1 macro 0.1716** y supera el baseline (0.0000). Hay **0 asignaciones de categorías fuera del vocabulario de train** y **8 categorías presentes en test con recall cero**. Las métricas solo cubren categorías conocidas; deben interpretarse junto con esos conteos y el detalle por categoría. Superar el baseline no acredita que el modelo detecte adecuadamente todas las categorías. Las entradas contienen exclusivamente sinopsis.
