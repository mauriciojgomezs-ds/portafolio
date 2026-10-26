# Recomendación colaborativa de películas: modelado

Se eligieron **30 vecinos** por NDCG@10 en validación. La similitud usa únicamente valoraciones positivas de train; se excluyen todas las películas ya valoradas en train, incluso las negativas. No se reentrena con validación.
