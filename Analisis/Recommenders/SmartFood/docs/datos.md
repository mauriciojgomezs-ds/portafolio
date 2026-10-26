# Datos y reproducción

El proyecto utiliza recetas y reseñas atribuidas en la documentación original a [Food.com Recipes and Reviews](https://www.kaggle.com/datasets/irkaal/foodcom-recipes-and-reviews). Las entradas esperadas son `recipes.csv` y `reviews.csv`, o sus versiones Parquet.

Los datos se gestionan localmente y se excluyen del versionado. La procedencia exacta, versión de descarga y huellas de los archivos aún deben registrarse. El [diccionario](diccionario_datos.md) distingue descripciones heredadas de tipos comprobados.

## Flujo y artefactos

| Etapa | Entrada | Artefacto generado |
| --- | --- | --- |
| Conversión opcional desde CSV | `data/raw/recipes.csv`, `reviews.csv` | `recipes.parquet`, `reviews.parquet` en la misma carpeta |
| [01 · Preparación](../notebooks/01_preparacion_datos.ipynb) | Parquet originales | `recipes_limpio.parquet`, `reviews_limpio.parquet` en `data/intermediate/` |
| [02 · Exploración](../notebooks/02_analisis_exploratorio.ipynb) | Parquet intermedios | Datos filtrados en `data/processed/`; reportes y figuras en `reports/` |
| [03 · Baseline](../notebooks/03_baseline_perfil_usuario.ipynb) | Datos procesados | Recomendaciones mostradas en el notebook |
| [04 · NMF](../notebooks/04_filtrado_colaborativo_nmf.ipynb) | Datos procesados | Factores de usuarios y recetas y predicciones en `models/` |
| [05 · SVM](../notebooks/05_clasificacion_ranking_svm.ipynb) | Datos procesados | `data/output/recomendaciones_svm.csv` |
| [00 · Entorno](../notebooks/00_configuracion_entorno.ipynb) | Python activo y requisitos | Diagnóstico y versiones en `reports/entorno/` |

Si partes de CSV, ejecuta `scripts/prepare_data.py` desde el entorno del proyecto. Si ya tienes los Parquet originales, no necesitas volver a convertirlos. La conversión carga un CSV completo por vez y no normaliza su contenido.

## Inventario comprobado

Los metadatos de los archivos locales se revisaron el 6 de octubre de 2026.

| Archivo | Filas | Columnas |
| --- | ---: | ---: |
| `data/raw/recipes.parquet` | 522.517 | 28 |
| `data/raw/reviews.parquet` | 1.401.982 | 8 |
| `data/intermediate/recipes_limpio.parquet` | 522.517 | 28 |
| `data/intermediate/reviews_limpio.parquet` | 1.401.982 | 8 |
| `data/processed/recipes_filtrado.parquet` | 190 | 28 |
| `data/processed/reviews_filtrado.parquet` | 10.343 | 8 |

La pasada vigente del maestro regeneró los Parquet intermedios y procesados, con estas mismas dimensiones. El [registro](ejecuciones.md) identifica la ejecución y la [evaluación](evaluacion.md) describe las métricas actuales del modelado.

## Transformaciones de preparación

`smartfood.limpieza` elimina columnas que empiezan por `Unnamed`, normaliza nombres de columnas y aplica normalización Unicode, conversión a ASCII, eliminación de puntuación y minúsculas a valores de texto de columnas seleccionadas.

La función de texto devuelve sin cambios los valores que no son cadenas. Los campos de listas anidadas presentes en los Parquet no se convierten automáticamente en texto ni se limpian elemento por elemento. Las fechas ya tipadas como timestamp tampoco pasan por esa normalización textual.

El notebook 05 convierte explícitamente listas y arrays de ingredientes a texto mediante `smartfood.texto.texto_ingredientes`, antes del merge y del entrenamiento. Los documentos vacíos se consideran ausentes. La conversión es en memoria; los Parquet conservan listas. La función separada de similitud TF-IDF también prepara ese contenido. Todavía deben revisarse los diagnósticos de cardinalidad sobre columnas de listas. Para campos que lleguen como cadenas, la eliminación general de puntuación puede alterar URLs, duraciones y cantidades; conviene aplicar reglas por campo.

El inventario confirma dimensiones y tipos, pero no demuestra eliminación de duplicados, ausencia de nulos ni calidad semántica del resultado.

## Filtrado y recodificación

El notebook 02 conserva un umbral de 270 interacciones por usuario y receta, calculado antes de intersectar ambos conjuntos. No es un filtrado iterativo ni garantiza 270 interacciones por entidad en el resultado final. Su valor no está validado como óptimo.

Los IDs se recodifican con `pd.Categorical(...).codes`. Actualmente el código no exporta los mapeos a IDs originales. Deben conservarse para interpretar recomendaciones y relacionarlas con el catálogo.

## Validaciones pendientes

Las métricas actuales verifican pares únicos, nulos en usuario/receta/rating y referencias al catálogo. Hay 19 pares registrados cuyo ID de receta no aparece en el catálogo original; el filtrado elimina ese desajuste en el subconjunto. Los conteos no sustituyen una validación semántica.

- Comprobar nulos, claves únicas, ratings, pares usuario–receta y coherencia entre tablas.
- Definir qué representa un rating cero y cómo se utiliza en cada enfoque.
- Registrar procedencia, versión y huellas de entradas y artefactos.
- Evaluar la representatividad de la cobertura cuantificada en `reports/eda/`.
- Completar el tratamiento de listas en todos los controles de exploración; los ingredientes para TF-IDF ya se convierten a texto.
- Revisar condiciones de uso en la fuente antes de redistribuir datos.

Consulta [ejecuciones](ejecuciones.md) para el estado del flujo y [mejoras](mejoras.md) para el orden de trabajo.
