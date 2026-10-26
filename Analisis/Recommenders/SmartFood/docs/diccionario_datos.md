# Diccionario de datos

Este documento describe el esquema físico observado en los Parquet locales y la correspondencia entre columnas originales y normalizadas. Se comprobaron los metadatos el 6 de octubre de 2026; no se validaron aquí todos los valores, nulos, rangos ni claves.

Los tipos corresponden a Arrow, no necesariamente a los dtypes que pandas presenta al cargar un archivo. Las descripciones y unidades proceden de la documentación original.

## Recetas

Cada registro representa una receta del catálogo. `AuthorId` identifica al autor de la receta.

| Original | Normalizada | Tipo en raw | Tipo en intermediate | Descripción |
| --- | --- | --- | --- | --- |
| `RecipeId` | `recipeid` | `double` | `double` | Identificador de la receta; clave de relación entre recetas y reseñas. Su unicidad y compatibilidad de tipos requieren validación. |
| `Name` | `name` | `string` | `string` | Nombre de la receta. |
| `AuthorId` | `authorid` | `int32` | `int32` | Identificador del autor de la receta. |
| `AuthorName` | `authorname` | `string` | `string` | Nombre del autor de la receta. |
| `CookTime` | `cooktime` | `string` | `string` | Tiempo de cocción (en formato ISO 8601, ej: PT30M). |
| `PrepTime` | `preptime` | `string` | `string` | Tiempo de preparación (en formato ISO 8601). |
| `TotalTime` | `totaltime` | `string` | `string` | Tiempo total estimado (suma de cocción y preparación). |
| `DatePublished` | `datepublished` | `timestamp[us, tz=UTC]` | `timestamp[us, tz=UTC]` | Fecha en que fue publicada la receta. |
| `Description` | `description` | `string` | `string` | Descripción breve de la receta. |
| `Images` | `images` | `list<string>` | `list<string>` | Lista o enlace(s) a imágenes asociadas con la receta. |
| `RecipeCategory` | `recipecategory` | `string` | `string` | Categoría general de la receta (ej: postre, entrada, sopa). |
| `Keywords` | `keywords` | `list<string>` | `list<string>` | Palabras clave asociadas con la receta (a menudo separadas por comas). |
| `RecipeIngredientQuantities` | `recipeingredientquantities` | `list<string>` | `list<string>` | Cantidades específicas de ingredientes (ej: "1 taza", "2 cucharadas"). |
| `RecipeIngredientParts` | `recipeingredientparts` | `list<string>` | `list<string>` | Ingredientes utilizados, en texto plano (ej: "harina", "huevo", etc.). |
| `AggregatedRating` | `aggregatedrating` | `double` | `double` | Puntuación promedio otorgada por los usuarios (de 1 a 5). |
| `ReviewCount` | `reviewcount` | `int32` | `double` | Número total de reseñas recibidas. |
| `Calories` | `calories` | `double` | `double` | Cantidad estimada de calorías por porción. |
| `FatContent` | `fatcontent` | `double` | `double` | Contenido total de grasas (gramos). |
| `SaturatedFatContent` | `saturatedfatcontent` | `double` | `double` | Contenido de grasas saturadas (gramos). |
| `CholesterolContent` | `cholesterolcontent` | `double` | `double` | Contenido de colesterol (miligramos). |
| `SodiumContent` | `sodiumcontent` | `double` | `double` | Contenido de sodio (miligramos). |
| `CarbohydrateContent` | `carbohydratecontent` | `double` | `double` | Contenido total de carbohidratos (gramos). |
| `FiberContent` | `fibercontent` | `double` | `double` | Contenido de fibra dietética (gramos). |
| `SugarContent` | `sugarcontent` | `double` | `double` | Contenido de azúcares (gramos). |
| `ProteinContent` | `proteincontent` | `double` | `double` | Contenido de proteínas (gramos). |
| `RecipeServings` | `recipeservings` | `int32` | `double` | Número estimado de porciones que rinde la receta. |
| `RecipeYield` | `recipeyield` | `string` | `string` | Descripción textual del rendimiento (formato libre, puede incluir texto). |
| `RecipeInstructions` | `recipeinstructions` | `list<string>` | `list<string>` | Lista de instrucciones paso a paso para preparar la receta. |

## Reseñas

Cada registro representa una reseña. `AuthorId` identifica a quien evalúa una receta y define al usuario del recomendador; no debe confundirse con el autor del catálogo de recetas.

| Original | Normalizada | Tipo en raw | Tipo en intermediate | Descripción |
| --- | --- | --- | --- | --- |
| `ReviewId` | `reviewid` | `int32` | `int32` | ID único de la reseña. |
| `RecipeId` | `recipeid` | `int32` | `int32` | Identificador de la receta; clave de relación entre recetas y reseñas. Su unicidad y compatibilidad de tipos requieren validación. |
| `AuthorId` | `authorid` | `int32` | `int32` | Identificador del usuario que evalúa la receta. |
| `AuthorName` | `authorname` | `string` | `string` | Nombre del usuario que evalúa la receta. |
| `Rating` | `rating` | `int32` | `int32` | Valoración registrada en la reseña. La documentación heredada describe estrellas de 1 a 5; los notebooks también consideran ratings cero, cuyo significado debe validarse. |
| `Review` | `review` | `string` | `string` | Comentario textual (puede estar ausente). |
| `DateSubmitted` | `datesubmitted` | `timestamp[us, tz=UTC]` | `timestamp[us, tz=UTC]` | Fecha de envío de la reseña. |
| `DateModified` | `datemodified` | `timestamp[us, tz=UTC]` | `timestamp[us, tz=UTC]` | Fecha de última edición de la reseña (si corresponde). |

## Campos utilizados en los enfoques

| Enfoque | Campos principales | Uso |
| --- | --- | --- |
| Baseline | `authorid`, `recipeid`, `calories`, `recipecategory` | Construir el perfil y excluir recetas evaluadas |
| NMF | `authorid`, `recipeid`, `rating` | Construir la matriz usuario–receta |
| SVM | `rating`, `recipeingredientparts`, `calories`, `aggregatedrating`, `recipecategory` | Crear el target y los atributos de receta |

## Decisiones de tratamiento pendientes

- `recipeingredientparts`, `keywords`, `images`, cantidades e instrucciones son listas en los archivos observados. TF-IDF requiere preparar una representación de texto; la limpieza actual no transforma el contenido de esas listas.
- `RecipeId` es `double` en recetas e `int32` en reseñas. Se debe comprobar integridad y compatibilidad antes de unir tablas o recodificar IDs.
- `ReviewCount` y `RecipeServings` aparecen como `int32` en raw y `double` en intermediate. El cambio está observado; este documento no atribuye su causa ni garantiza que los valores sean equivalentes.
- Las fechas son timestamps UTC en ambos esquemas. Las duraciones se almacenan como texto y todavía no se convierten a minutos.
- Los ratings cero necesitan una definición explícita. La clasificación SVM los trata como negativos y la evaluación NMF oculta solo entradas positivas.
- `aggregatedrating` requiere revisar su disponibilidad temporal antes de usarlo para predecir valoraciones de usuarios.

Para el flujo de archivos y las transformaciones, consulta [datos](datos.md). Para los riesgos de evaluación, consulta [evaluación](evaluacion.md).

