# Knowledge Base MVP: análisis documental e IA aplicada

## Problema y valor

Resolver preguntas técnicas suele requerir consultar varias páginas, distinguir documentación relevante y ordenar prerrequisitos, configuración y validación. Este proyecto explora un asistente que consulta sitios configurados y reúne información para orientar ese trabajo.

Su aporte al portafolio combina ingeniería de datos, recuperación de información y análisis de cobertura documental. La evolución propuesta incorpora IA generativa para redactar respuestas apoyadas en los documentos recuperados. Esa integración todavía no está implementada.

## Capacidades actuales verificadas en el código

| Etapa | Implementación |
| --- | --- |
| Configuración de fuentes | Registro de sitios y filtros de URL mediante etiquetas en SQLite. |
| Descubrimiento e ingesta | Búsqueda de URLs, scraping de texto y seguimiento limitado de enlaces. Incluye descubrimiento genérico, un conector de búsqueda de documentación y reglas para temas específicos. |
| Persistencia | Documentos, versiones, hashes de contenido y registro de cambios. |
| Recuperación | Búsqueda léxica con SQLite FTS5/BM25 y ranking heurístico por términos, intención y URL. En discovery se priorizan las URLs de la ejecución, con fallback a la base local si no hay documentos. |
| Respuesta | Extracción de frases y guías predefinidas para temas conocidos; reutilización de respuestas registradas como validadas. |
| Cobertura | Checklist por coincidencias de términos que marca fuentes encontradas o pendientes. |
| Retroalimentación | Registro manual de respuestas validadas, errores y consultas exitosas; no implica entrenamiento automático. |

El flujo principal es: pregunta → descubrimiento de URLs → extracción y almacenamiento → selección de documentos → respuesta y fuentes candidatas. `ask` consulta la base local; `ask-live --discover` incorpora descubrimiento e ingesta.

## Límites de la evidencia actual

La revisión corresponde al código y la documentación, sin ejecutar consultas contra sitios externos ni medir su calidad. No hay resultados cuantitativos publicados en esta ficha.

El proyecto no utiliza embeddings, un modelo entrenado ni un LLM. Los pasos de varios temas están escritos en el código: recuperar documentos y mostrar URLs no demuestra que cada paso esté respaldado por ellos. La checklist usa coincidencias de texto, por lo que una fuente marcada como encontrada no acredita cobertura suficiente ni corrección técnica. El fallback a documentos anteriores y la reutilización de respuestas validadas también requieren evaluar relevancia y vigencia.

## Evolución propuesta: generación apoyada en recuperación (RAG)

1. Dividir los documentos en fragmentos, conservando URL, versión y fecha de captura.
2. Mantener la recuperación léxica como referencia e incorporar búsqueda semántica para comparar su aporte.
3. Entregar los fragmentos seleccionados a un modelo de lenguaje para construir el paso a paso. Cada paso debe citar la evidencia correspondiente y declarar los puntos sin respaldo suficiente.
4. Separar en la respuesta los hechos recuperados de las sugerencias y evitar completar procedimientos cuando falten fuentes esenciales.
5. Conservar pregunta, documentos usados, versión del modelo, respuesta, tiempo y costo para analizar resultados reproducibles.

Esta propuesta aprovecha la base documental existente. La comparación con el MVP por reglas permitiría comprobar si la IA mejora las respuestas y a qué costo.

## Cómo combinar IA con análisis

Preparar un conjunto de preguntas con documentos relevantes, pasos esperados y casos sin evidencia suficiente, revisado por una persona con conocimiento del tema. Separar las preguntas usadas para ajustar reglas de las destinadas a la evaluación final e incluir temas conocidos, temas nuevos, paráfrasis y consultas de distintos orígenes.

| Dimensión | Medición propuesta | Qué permite analizar |
| --- | --- | --- |
| Recuperación | Precision@k y Recall@k contra documentos etiquetados | Si se seleccionan las fuentes necesarias y cuánto ruido se incorpora. |
| Respaldo | Proporción de pasos cuyas citas sostienen la afirmación, revisada manualmente | Si la respuesta está fundamentada. |
| Cobertura | Proporción de pasos esenciales correctamente cubiertos | Si el procedimiento queda completo. |
| Incertidumbre | Abstenciones correctas y respuestas sin respaldo en casos insuficientes | Si el asistente reconoce la falta de información. |
| Vigencia y contexto | Respuestas con versiones desactualizadas o fuentes ajenas al tema | Si el almacenamiento y el fallback introducen errores. |
| Operación | Latencia, fallos de ingesta y costo por consulta con LLM | Si la mejora de calidad compensa el tiempo y el costo. |

Comparar recuperación léxica, ranking actual y futura versión RAG con las mismas preguntas y una captura documental común. Informar resultados por tema y origen, junto con ejemplos de errores; no atribuir la calidad a la IA solo por producir texto más fluido.

Como extensión posterior, el asistente podría explicar reportes de churn, segmentación o pronóstico del portafolio, citando métricas y limitaciones de los informes. Esto requeriría agregar ingesta de archivos locales: la ingesta actual trabaja con URLs y `ingest-file` lee listas de URLs, no informes Markdown o PDF.

## Presentación del proyecto

**Asistente de investigación documental:** MVP en Python que recupera documentación desde sitios configurados, almacena versiones en SQLite y construye guías mediante búsqueda léxica y reglas. Incluye fuentes candidatas y revisión heurística de cobertura. Su siguiente etapa propuesta es incorporar IA generativa con citas y evaluar relevancia, respaldo, completitud y costo frente al sistema actual.

Las instrucciones de instalación y ejecución están en el [README](../README.md).
