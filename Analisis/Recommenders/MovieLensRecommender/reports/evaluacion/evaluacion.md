# Recomendación colaborativa de películas: evaluacion

El modelo supera el baseline por NDCG@10: **0.0448** frente a **0.0253**, en **469 objetivos positivos**. Hay **19 objetivos sin historial del ítem** en train.

Se evalúa una muestra de usuarios existentes con un objetivo retenido por usuario; no mide satisfacción real ni usuarios nuevos. Los cortes son temporales por usuario, no un corte global: las interacciones de otros usuarios pueden ser posteriores al objetivo de un usuario. Un top solicitado puede quedar incompleto si no hay suficientes candidatos con señal positiva.
