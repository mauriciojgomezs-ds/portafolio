# Vitrina Grupo 2 — CV, NLP, Clustering y Forecasting

## Resumen

Se mejoró la presentación visual del `README.md` principal de 8 proyectos (ComputerVision ×2, NLP ×2, Clustering ×2, Forecasting ×2) sin modificar cifras, afirmaciones, enlaces ni el contenido textual existente. En cada proyecto se agregó:

1. Una línea de **badges** (Python, scikit-learn, estado de ejecución) pegada al título (`# Nombre\n![badges]`, sin línea en blanco entre ambos) para que título+badges formen un único párrafo y no sean confundidos con el párrafo "objetivo".
2. Una **imagen representativa** ya generada en `reports/eda/*.png` o `reports/evaluacion/*.png`, incrustada (no solo enlazada) en un punto razonable del README.
3. **Tabla de contenidos**: no se agregó en ningún proyecto porque ninguno supera simultáneamente ~60 líneas y 5+ encabezados `##` (máximo detectado: 44 líneas y 3 encabezados en el grupo CV/Forecasting "clásico"; 37 líneas y 6 encabezados en el grupo NLP/Clustering/Forecasting "plantilla"). Ambas condiciones del criterio no se cumplieron en ningún caso.

**Verificación de la regla de seguridad (párrafo "objetivo"):** para cada uno de los 8 proyectos se localizó `src/<paquete>/informe.py`, se confirmó la lógica exacta (`objective.split('\n\n')[1:]`, primer fragmento que no empieza con `#`, `|`, ` ``` ` ni `**`), se aplicó la solución (badges unidos al título con un solo salto de línea) y luego se **ejecutó un script Python que reproduce esa misma lógica de extracción sobre cada README ya editado**, confirmando que el objetivo extraído sigue siendo la descripción real del proyecto (no la línea de badges) en los 8 casos. Resultado: 8/8 correctos.

Ningún número, afirmación, limitación o enlace existente fue modificado o eliminado; solo se añadieron líneas nuevas.

## Detalle por archivo

| ruta | archivo | línea | original | propuesta |
| --- | --- | --- | --- | --- |
| Analisis/ComputerVision/DigitsRecognition | README.md | 1-2 | `# Reconocimiento de dígitos escritos`\n\n`Reconocer dígitos...` (línea en blanco entre título y párrafo) | `# Reconocimiento de dígitos escritos`\n`![Python](...) ![scikit--learn](...) ![estado](...)`\n\n`Reconocer dígitos...` (badges pegados al título, mismo párrafo original intacto a continuación) |
| Analisis/ComputerVision/DigitsRecognition | README.md | ~27-29 (sección "Resultados y documentación") | Bullet `- reports/evaluacion/: métricas...` seguido directo de `Los comentarios se generan...` | Se insertó entre ambos: `![Evaluación del clasificador de dígitos: matriz de confusión y errores](reports/evaluacion/evaluacion.png)` |
| Analisis/ComputerVision/FashionMNISTClassification | README.md | 1-2 | `# Clasificación visual de prendas`\n\n`Identificar diez categorías...` | Badges pegados al título igual que arriba |
| Analisis/ComputerVision/FashionMNISTClassification | README.md | final de "Primera ejecución comprobada" | `...sin converger. Los avisos se conservan... Consulta el [registro de ejecución]...` | Se insertó entre "sin converger." y "Los avisos...": `![Ejemplos de errores de clasificación en Fashion-MNIST](reports/evaluacion/errores_visuales.png)` |
| Analisis/NLP/IMDbSentiment | README.md | 1-2 | `# Sentimiento de reseñas de películas`\n\n`Clasificar reseñas...` | Badges pegados al título |
| Analisis/NLP/IMDbSentiment | README.md | sección "Evidencia" | `...resumen de ejecución del maestro. La última [evaluación]...` | Se insertó entre ambas oraciones: `![Distribución exploratoria de las reseñas de IMDb](reports/eda/eda.png)` |
| Analisis/NLP/NetflixGenreClassification | README.md | 1-2 | `# Categorías de películas desde su sinopsis`\n\n`Predecir varias categorías...` | Badges pegados al título |
| Analisis/NLP/NetflixGenreClassification | README.md | sección "Evidencia" | `...resumen de ejecución del maestro. La última [evaluación]...` | Se insertó: `![Distribución exploratoria de las sinopsis y categorías](reports/eda/eda.png)` |
| Analisis/Clustering/CustomerSegmentation | README.md | 1-2 | `# Segmentación de clientes con RFM`\n\n`Describir grupos de clientes...` | Badges pegados al título |
| Analisis/Clustering/CustomerSegmentation | README.md | sección "Evidencia" | `...resumen de ejecución del maestro. La última [evaluación]...` | Se insertó: `![Segmentos de clientes proyectados por KMeans](reports/evaluacion/clusters.png)` |
| Analisis/Clustering/SpotifySegmentation | README.md | 1-2 | `# Segmentación de canciones`\n\n`Explorar grupos musicales...` | Badges pegados al título |
| Analisis/Clustering/SpotifySegmentation | README.md | sección "Evidencia" | `...resumen de ejecución del maestro. La última [evaluación]...` | Se insertó: `![Segmentos de canciones proyectados por KMeans](reports/evaluacion/clusters.png)` |
| Analisis/Forecasting/CallCenterStaffing | README.md | 1-2 | `# Demanda y dotación de call center`\n\n`Pronosticar llamadas...` | Badges pegados al título |
| Analisis/Forecasting/CallCenterStaffing | README.md | sección "Resultados y documentación" | Bullet `- reports/evaluacion/: métricas...` seguido de `Los comentarios se generan...` | Se insertó: `![Evaluación del pronóstico de llamadas y dotación de agentes](reports/evaluacion/evaluacion.png)` |
| Analisis/Forecasting/RetailSalesForecasting | README.md | 1-2 | `# Pronóstico semanal de compras`\n\n`Predecir el importe...` | Badges pegados al título |
| Analisis/Forecasting/RetailSalesForecasting | README.md | sección "Evidencia" | `...resumen de ejecución del maestro. La última [evaluación]...` | Se insertó: `![Evaluación del pronóstico semanal de compras](reports/evaluacion/evaluacion.png)` |

## Badges usados (idénticos en los 8 proyectos, por consistencia visual)

- `![Python](https://img.shields.io/badge/python-3.10%2B-blue)` — de `requires-python = ">=3.10"` en cada `pyproject.toml`.
- `![scikit--learn](https://img.shields.io/badge/scikit--learn-1.3%2B-orange)` — de `scikit-learn>=1.3` (dependencia clave compartida: TF-IDF, regresión logística, KMeans, Ridge, MLP según el proyecto).
- `![estado](https://img.shields.io/badge/estado-completado-brightgreen)` — de `"estado": "completado"` en `reports/ejecucion/resumen.json` (confirmado en los 8 proyectos).

## Imágenes incrustadas (ya existían en `reports/`, solo se agregó el embed)

| Proyecto | Imagen | Origen |
| --- | --- | --- |
| DigitsRecognition | evaluacion.png | reports/evaluacion/ |
| FashionMNISTClassification | errores_visuales.png | reports/evaluacion/ |
| IMDbSentiment | eda.png | reports/eda/ (único PNG disponible; no hay evaluacion/*.png en este proyecto) |
| NetflixGenreClassification | eda.png | reports/eda/ (único PNG disponible) |
| CustomerSegmentation | clusters.png | reports/evaluacion/ |
| SpotifySegmentation | clusters.png | reports/evaluacion/ |
| CallCenterStaffing | evaluacion.png | reports/evaluacion/ |
| RetailSalesForecasting | evaluacion.png | reports/evaluacion/ |

## Tabla de contenidos

No aplicada en ningún proyecto del grupo: ninguno cumple simultáneamente "más de ~60 líneas" y "5+ encabezados `##`" (criterio de la tarea). Los README más largos tienen 44-47 líneas tras los cambios.
