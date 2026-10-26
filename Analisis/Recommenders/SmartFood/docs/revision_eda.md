# Revisión de conclusiones del análisis exploratorio

Se revisaron los comentarios y las salidas de [02_analisis_exploratorio.ipynb](../notebooks/02_analisis_exploratorio.ipynb) después de la ejecución informada por el usuario. Las cifras principales se comprobaron leyendo las columnas necesarias de los Parquet intermedios y procesados el 6 de octubre de 2026.

Se corrigieron textos y comentarios sin cambiar las operaciones de filtrado, los parámetros ni las salidas guardadas. Esta revisión no vuelve a ejecutar el notebook completo ni valida los modelos posteriores.

## Cifras verificadas

Esta tabla conserva la instantánea revisada el 6 de octubre de 2026. El notebook ahora genera sus cifras y comentarios durante la ejecución mediante `smartfood.anotaciones`, y exporta la versión actual a `reports/eda/`. Consulta la [guía de notebooks](notebooks.md#cifras-automáticas-del-notebook-02) para actualizar esos reportes. Esta revisión histórica no se modifica automáticamente.

La pasada posterior del maestro confirmó las dimensiones y porcentajes de la tabla e incorporó controles automáticos de referencia al catálogo: 19 pares del conjunto original tienen una receta ausente del catálogo y ninguno del subconjunto presenta ese desajuste. También incorporó Pearson y Spearman entre calorías y proteína. Consulta las [métricas vigentes](../reports/eda/metricas_eda.json) y los [comentarios generados](../reports/eda/conclusiones_eda.md). Los controles de cardinalidad por listas siguen imprimiendo errores.

| Medida | Antes del filtro | Después del filtro |
| --- | ---: | ---: |
| Reseñas | 1.401.982 | 10.343 |
| Usuarios con reseñas | 271.907 | 617 |
| Recetas con reseñas | 271.678 | 190 |
| Recetas del catálogo | 522.517 | 190 |
| Pares usuario–receta únicos | 1.401.982 | 10.343 |
| Ratings 5 | 72,19 % | 77,43 % |
| Ratings 0 | 5,44 % | 1,62 % |
| Ratings >= 4 | 88,54 % | 93,61 % |
| Esparsidad por pares registrados | 99,9981 % | 91,1772 % |
| Desviación estándar de aggregatedrating | 0,642 | 0,191 |

La esparsidad se calculó como `1 - pares únicos / (usuarios × recetas evaluadas)`. Los ratings cero se cuentan como interacciones registradas. No se encontraron pares repetidos, por lo que en estos archivos la fórmula basada en número de filas da el mismo resultado. La tabla no mide error predictivo ni calidad de ranking.

## Conclusiones corregidas

| Afirmación anterior | Evaluación | Corrección aplicada |
| --- | --- | --- |
| 10.343 recetas evaluadas | Confundía reseñas con recetas | Son 10.343 reseñas sobre 190 recetas |
| No hay nulos importantes | Incorrecta para todo el catálogo | aggregatedrating tiene 48,46 % de nulos y reviewcount 47,36 %; se distinguió recetas de reseñas |
| Todas las columnas tienen variabilidad suficiente | No comprobada | Los diagnósticos de cardinalidad fallan por listas; se dejó explícito el límite |
| La dispersión de aggregatedrating mejora tras el filtro | Contradice los resultados | La desviación baja de 0,642 a 0,191: aumenta la concentración |
| Se mantuvo buena representatividad | No demostrada | Se conservan 0,227 % de usuarios, 0,0364 % del catálogo y 0,738 % de reseñas |
| La presencia de ceros sigue siendo alta | Imprecisa | Se cuantificó su descenso de 5,44 % a 1,62 %, sin atribuirles un significado |
| La esparsidad confirma que debe usarse NMF | No demostrada | La elección requiere comparación con baselines y protocolo de evaluación |
| El filtro reduce ruido y garantiza suficiencia | No demostrada | Se verificó reducción de tamaño y aumento de densidad, sin atribuir mejora predictiva |
| El umbral conserva usuarios y recetas con al menos 270 interacciones | No describe el resultado final | El mínimo final es uno para ambos tipos de entidad |

## Hallazgos que sí se sostienen

Las valoraciones se concentran en 5. Los historiales presentan una cola larga: la mediana por usuario es una reseña y la mediana por receta evaluada es dos. La matriz original es extremadamente dispersa y la selección de usuarios y recetas activos reduce su tamaño.

Las salidas no detectan nulos ni filas exactamente duplicadas en reseñas. La comprobación independiente confirma pares usuario–receta únicos en ambos archivos, IDs de receta únicos en el catálogo intermedio y que todas las recetas referenciadas por las reseñas filtradas están presentes en el catálogo filtrado. Esto no constituye una validación semántica completa de los datos.

## Límites del diagnóstico automático

La función `evaluar_viabilidad_modelo_general` utiliza reglas heurísticas. Su mensaje de varianza aceptable solo comprueba si el rating dominante está por debajo del 90 %; no calcula ni evalúa una varianza. La existencia de más de dos valores de rating no es una condición de viabilidad del SVM binario usado después.

Los controles de cardinalidad de recetas fallan con `unhashable type: 'numpy.ndarray'`, tanto antes como después del filtro. Además, seleccionar únicamente `int64` y `float64` excluye campos `int32`. Los textos se corrigieron, pero esos controles de código siguen pendientes.

La tabla de umbrales cuenta entidades que cumplen el mínimo en el dataset original. Después de intersectarlas, algunas pierden gran parte de su historial. Si se desea un mínimo garantizado, debe definirse y evaluarse un filtrado iterativo; no se cambió el algoritmo en esta revisión.

## Implicaciones para el modelado

El 93,61 % de las reseñas filtradas pertenece a la clase positiva de `rating >= 4`. Un clasificador constante alcanzaría esa accuracy sobre todo el subconjunto, por lo que el siguiente notebook debe incluir el baseline y métricas por clase. Este porcentaje no es una evaluación nueva del SVM ni una métrica sobre su test.

Las listas necesitan preparación para TF-IDF. Los ceros requieren una definición, y los mapeos de IDs deben conservarse. También debe revisarse el uso de aggregatedrating para evitar fuga de información. Centrar ratings por usuario puede introducir valores negativos y no debe aplicarse directamente a NMF.

La conclusión válida es que el subconjunto permite prototipar con una matriz pequeña. Su representatividad y la mejora de recomendaciones siguen pendientes de evaluación.
