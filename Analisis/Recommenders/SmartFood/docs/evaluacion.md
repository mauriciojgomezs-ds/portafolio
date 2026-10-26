# Evaluación y limitaciones

## Ejecución analizada

Este documento describe las salidas de los notebooks 03–05 regeneradas por el maestro el **6 de octubre de 2026**. El [registro de ejecución](ejecuciones.md) identifica el Python, los tiempos y la evidencia. Las tablas siguientes conservan la revisión del 6 de octubre de 2026. El [informe integral automático](../reports/informe_final/informe_final.md) contiene las cifras y conclusiones regeneradas con la última ejecución; las cifras académicas anteriores se conservan en las referencias y el respaldo local.

Completar los notebooks prueba que sus celdas terminaron, no que los modelos sean útiles ni que todos los diagnósticos de datos hayan pasado.

## Baseline por perfil

El notebook 03 calcula la categoría más frecuente y las calorías medias de las recetas del historial. Excluye recetas evaluadas, candidatos sin los atributos requeridos y categorías distintas; ordena por distancia calórica.

El ejemplo actual del usuario 198 devuelve cinco recetas para un top-5. `top_n` es un máximo: puede devolver menos o ninguna según los candidatos. Utiliza todas las recetas evaluadas, no exclusivamente las valoraciones positivas. No se ha publicado una métrica cuantitativa de relevancia comparable con los otros enfoques.

## SVM: accuracy equivalente al baseline mayoritario

El target es `rating >= 4`. Los ingredientes se convierten de listas o arrays a texto antes del merge y el split. Los documentos vacíos se consideran ausentes y se excluyen junto con los casos sin calorías. La pasada utiliza 8.260 interacciones para entrenamiento y 2.065 para test, con un split aleatorio de 20 % y semilla 42.

El pipeline combina TF-IDF, imputación y escalamiento de atributos numéricos, codificación de categoría y `LinearSVC`.

| Clase real / predicción | Negativa | Positiva |
| --- | ---: | ---: |
| Negativa | 0 | 128 |
| Positiva | 0 | 1.937 |

Todos los casos se predicen positivos. La accuracy es `1937 / 2065 ≈ 93,8015 %`; el recall negativo es cero y el F1 macro guardado se redondea a 0,48. Predecir siempre la clase mayoritaria del entrenamiento —positiva— obtiene la misma accuracy en este test. Por tanto, la accuracy no acredita mejora sobre ese baseline.

`classification_report(..., zero_division=0)` representa como cero las métricas indefinidas y evita warnings repetidos. No resuelve la falta de predicciones negativas. La interpretación automática informa el comportamiento y compara contra la regla mayoritaria.

### Alcance del ranking

- El modelo no recibe atributos del usuario. Los rankings por usuario excluyen recetas vistas y utilizan scores globales para el resto.
- La función por receta excluye la referencia, pero no calcula similitud con ella: ordena por el margen del SVM.
- La función por keywords reemplaza los ingredientes de los candidatos por la consulta; no calcula similitud con su contenido real.
- Los scores normalizados no son probabilidades y requieren manejar el caso de márgenes constantes.
- La similitud separada por TF-IDF sí usa coseno entre ingredientes. Su ejemplo muestrea con reemplazo y puede repetir recetas; construye una matriz densa.

### Riesgos del protocolo

`aggregatedrating` puede contener información de interacciones usadas en test. Su disponibilidad temporal debe verificarse antes de afirmar ausencia de fuga de información. El split aleatorio permite recetas compartidas entre entrenamiento y test, por lo que no estima desempeño sobre recetas nuevas.

La exploración de thresholds utiliza test: no debe utilizarse para elegir el umbral final sin reservar validación y un test independiente. `LinearSVC()` tampoco fija su propia semilla; registrar versiones exactas y controlar esa aleatoriedad ayudaría a reproducir resultados futuros.

## NMF: reconstrucción de interacciones ocultas

La matriz usuario–receta promedia los ratings por par y rellena ausencias con cero. La evaluación oculta el 20 % de entradas positivas y mide el error sobre esas interacciones. Los ratings cero no participan en el conjunto positivo que se oculta.

| Componentes | RMSE de la revisión del 6 de octubre | Interacciones ocultas |
| --- | ---: | ---: |
| 10 | 4,19964 | 2.035 |
| 20 | 4,29185 | 2.035 |
| 70 | 4,4884 | 2.035 |

El grid explora de 10 a 190 componentes en pasos de 10. El menor RMSE corresponde a 10, pero se conserva la selección de 70 para el entrenamiento y las recomendaciones. La anotación detecta esa diferencia; no modifica automáticamente el parámetro.

El ajuste también penaliza ceros que representan ausencia de interacción. La búsqueda reutiliza las mismas entradas ocultas sin un test final independiente. El RMSE de reconstrucción no mide la calidad del ranking posterior por vecinos ni prueba que NMF supere medias de rating u otros baselines.

## Datos y controles que condicionan la interpretación

La selección final contiene 617 usuarios, 190 recetas y 10.343 reseñas. El 93,61 % de las interacciones es positivo bajo `rating >= 4`. El filtro aumenta la concentración de ratings máximos y reduce considerablemente la cobertura.

El EDA registra 19 pares cuya receta no está en el catálogo original; el subconjunto no tiene ese desajuste. Los diagnósticos de cardinalidad de recetas siguen fallando por arrays. Las alertas tabuladas registran warnings, no esos errores capturados e impresos.

Las correlaciones de calorías y proteína en el catálogo filtrado son Pearson ≈ 0,713 y Spearman ≈ 0,797. La magnitud se clasifica según cortes explícitos del proyecto: no demuestra causalidad, significancia estadística ni capacidad predictiva.

## Siguiente protocolo de evaluación

1. Definir relevancia, semántica del rating cero y objetivo: rating, clasificación o top-K.
2. Separar entrenamiento, validación y test antes de ajustar componentes o thresholds. Revisar el sesgo introducido por filtrar antes del split.
3. Comparar popularidad, medias y clase mayoritaria en la misma tarea y partición.
4. Revisar la disponibilidad temporal de features y el tratamiento de usuarios o recetas sin historial.
5. Medir Precision@K, Recall@K, NDCG@K y cobertura con candidatos y exclusión de historial definidos.
6. Registrar versiones, parámetros, semillas, huellas de datos y mapeos de IDs originales.

La ejecución está reproducida; estas mejoras de evaluación continúan pendientes. No se comparan directamente accuracy con RMSE ni se presenta una mejora de recomendación todavía no medida.
