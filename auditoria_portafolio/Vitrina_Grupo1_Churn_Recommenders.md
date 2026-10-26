# Mejoras visuales — Grupo 1 (Churn + Recommenders)

## Resumen

Se agregaron, sin eliminar ni reescribir contenido textual existente, tres tipos de mejoras visuales a los 8 READMEs principales: (1) una línea de badges de Python/scikit-learn/estado inmediatamente debajo del título `#` (mismo párrafo, sin línea en blanco de por medio, para no alterar la extracción automática del párrafo "objetivo"), (2) en los 4 proyectos de churn y en SmartFood (>60 líneas y 5+ encabezados `##`) una tabla de contenidos corta en negrita (`**Contenido:** ...`) justo antes del primer encabezado `##`, que también es ignorada por el parser por empezar con `**`, y (3) una imagen ya generada (`reports/eda/*.png` o `reports/evaluacion/*.png`) incrustada en un punto razonable del cuerpo (tras la sección de resultados o antes de "Reproducción"/"Resultados"), en los 8 proyectos.

**Verificación de seguridad:** en cada uno de los 8 proyectos se leyó `src/*/informe.py` (lógica: `objetivo = paras[1:]` buscando el primer párrafo que NO empiece con `#`, `|`, ` ``` ` ni `**`) y se ejecutó una comprobación automatizada tras la edición que reproduce esa misma lógica sobre el README final. En todos los casos el párrafo "objetivo" extraído sigue siendo la descripción real del proyecto (no la línea de badges ni la línea de TOC). No se modificó ninguna cifra, afirmación, limitación ni enlace existente.

## Detalle por archivo

| ruta | archivo | linea | original | propuesta |
| --- | --- | --- | --- | --- |
| Analisis/churn/ActivityChurn | README.md | 2 (nueva) | (no existía) | `![Python](...)` `![scikit--learn](...)` `![estado](...)` — badges Python 3.10+, scikit-learn 1.6+, estado completado (añadidos en el mismo párrafo que `# ActivityChurn`, sin línea en blanco) |
| Analisis/churn/ActivityChurn | README.md | 4 (nueva) | (no existía) | `**Contenido:** [Datos](#datos-y-particiones) · [Resultados](#modelo-y-resultados-iniciales) · [Reproducción](#reproducción) · [Informe integral](#informe-integral)` |
| Analisis/churn/ActivityChurn | README.md | 44 (nueva) | (no existía) | `![Matriz de decisiones del modelo sobre test](reports/evaluacion/decisiones.png)` insertada después del párrafo final de "Modelo y resultados iniciales" y antes de "## Reproducción" |
| Analisis/churn/BankChurn | README.md | 2 (nueva) | (no existía) | badges Python 3.10+, scikit-learn 1.6+, estado completado |
| Analisis/churn/BankChurn | README.md | 4 (nueva) | (no existía) | `**Contenido:** [Datos](#datos-y-particiones) · [Resultados](#resultado-de-test) · [Reproducción](#reproducción) · [Informe integral](#informe-integral)` |
| Analisis/churn/BankChurn | README.md | 48 (nueva) | (no existía) | `![Matriz de decisiones del modelo sobre test](reports/evaluacion/decisiones.png)` insertada tras el párrafo final de "Resultado de test" y antes de "## Reproducción" |
| Analisis/churn/SubscriptionChurn | README.md | 2 (nueva) | (no existía) | badges Python 3.10+, scikit-learn 1.6+, estado completado |
| Analisis/churn/SubscriptionChurn | README.md | 4 (nueva) | (no existía) | `**Contenido:** [Datos](#datos-y-particiones) · [Resultados](#selección-y-desempeño) · [Reproducción](#reproducción) · [Informe integral](#informe-integral)` |
| Analisis/churn/SubscriptionChurn | README.md | 41 (nueva) | (no existía) | `![Distribución de la variable objetivo de churn](reports/eda/distribucion_target.png)` insertada tras el párrafo final de "Selección y desempeño" y antes de "## Diferencia entre validación y test" |
| Analisis/churn/TelecomChurn | README.md | 2 (nueva) | (no existía) | badges Python 3.10+, scikit-learn 1.6+, estado completado |
| Analisis/churn/TelecomChurn | README.md | 4 (nueva) | (no existía) | `**Contenido:** [Datos](#datos-y-particiones) · [Resultados](#resultados-de-la-ejecución) · [Reproducción](#reproducción) · [Informe integral](#informe-integral)` |
| Analisis/churn/TelecomChurn | README.md | 56 (nueva) | (no existía) | `![Matriz de decisiones del modelo sobre test](reports/evaluacion/decisiones.png)` insertada dentro de "Resultados de la ejecución", antes del párrafo "El maestro completó las cinco etapas..." |
| Analisis/Recommenders/MovieLensRecommender | README.md | 2 (nueva) | (no existía) | badges Python 3.10+, scikit-learn 1.3+, estado completado (sin TOC: README <60 líneas) |
| Analisis/Recommenders/MovieLensRecommender | README.md | 22 (nueva) | (no existía) | `![Figura del análisis exploratorio de MovieLens](reports/eda/eda.png)` insertada dentro de "Evidencia", antes de "Los reportes usan nombres estables." |
| Analisis/Recommenders/NetflixRecommender | README.md | 2 (nueva) | (no existía) | badges Python 3.10+, scikit-learn 1.3+, estado completado (sin TOC: README <60 líneas) |
| Analisis/Recommenders/NetflixRecommender | README.md | 22 (nueva) | (no existía) | `![Figura del análisis exploratorio del catálogo de Netflix](reports/eda/eda.png)` insertada dentro de "Evidencia" |
| Analisis/Recommenders/SpotifyRecommender | README.md | 2 (nueva) | (no existía) | badges Python 3.10+, scikit-learn 1.3+, estado completado (sin TOC: README <60 líneas) |
| Analisis/Recommenders/SpotifyRecommender | README.md | 22 (nueva) | (no existía) | `![Figura del análisis exploratorio de las canciones](reports/eda/eda.png)` insertada dentro de "Evidencia" |
| Analisis/Recommenders/SmartFood | README.md | 2 (nueva) | (no existía) | badges Python 3.10+, scikit-learn 1.3+, estado completado (añadidos tras `# SmartFood`, antes del subtítulo `### De un catálogo...`) |
| Analisis/Recommenders/SmartFood | README.md | 15 (nueva) | (no existía) | `**Contenido:** [Pregunta](#la-pregunta-del-proyecto) · [Datos](#datos-y-principales-hallazgos) · [Resultados](#resultados-de-la-ejecución-actual) · [Ejecutar](#ejecutar-el-proyecto) · [Informe integral](#informe-integral)` insertada antes de "## La pregunta del proyecto" |
| Analisis/Recommenders/SmartFood | README.md | 48 (nueva) | (no existía) | `![Matriz de correlación del subconjunto de recetas filtrado](reports/eda/recipes_filtrado/recipes_filtrado_correlacion.png)` insertada al final de "Datos y principales hallazgos", antes de "## Resultados de la ejecución actual" |

## Notas de verificación

- En los 4 proyectos de churn y en SmartFood, la línea de badges quedó en el MISMO párrafo que el título `#` (un solo salto de línea, sin línea vacía), cumpliendo la regla de seguridad.
- La línea `**Contenido:** ...` siempre comienza con `**`, por lo que el parser de `informe.py` la descarta igual que descarta encabezados y tablas.
- Se confirmó con un script que reproduce exactamente la lógica de `informe.py` (`paras[1:]`, primer párrafo que no empiece con `#`, `|`, ` ``` ` o `**`) que el párrafo "objetivo" extraído en los 8 README finales sigue siendo la descripción real del proyecto.
- No se agregó TOC en MovieLensRecommender, NetflixRecommender ni SpotifyRecommender porque sus READMEs tienen menos de 60 líneas (aunque tengan 5+ encabezados `##`), según la condición combinada del encargo.
- Todas las imágenes referenciadas existen físicamente en las rutas indicadas (verificado con comprobación de archivo tras cada edición).
