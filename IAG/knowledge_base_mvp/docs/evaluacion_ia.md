# Evaluación y evolución hacia IA

## Objetivo

Comprobar si un asistente con IA ayuda a resolver preguntas técnicas mejor que el MVP actual, usando fuentes pertinentes y afirmaciones respaldadas. La calidad se medirá por recuperación, cobertura y corrección, además de fluidez, tiempo y costo.

Este documento define un protocolo propuesto. No presenta resultados ni afirma que exista una implementación RAG.

## Preparar la referencia

Crear un conjunto inicial de preguntas revisadas por una persona con conocimiento del dominio. Incluir temas conocidos y nuevos, paráfrasis, requisitos faltantes, documentación contradictoria o desactualizada y preguntas fuera de alcance. Mantener una captura documental común para comparar versiones sin confundir mejoras del sistema con cambios de la web.

Separar desarrollo y evaluación final antes de ajustar reglas. Las preguntas finales no deben registrarse en `validated_qa` ni usarse para elegir pesos, prompts o modelos. Registrar los casos fallidos y sin respuesta, no solo los exitosos.

| Campo por caso | Contenido |
| --- | --- |
| `case_id`, `split`, `source_tag`, `topic` | Identidad, partición, origen y tema. |
| `question` | Pregunta exacta y lenguaje. |
| `relevant_sources` | URLs y versiones relevantes según revisión humana. |
| `required_steps` | Pasos esenciales, cada uno con evidencia de referencia. |
| `answerable` | Si la captura documental permite responder suficientemente. |
| `snapshot_id`, `reviewed_at`, `reviewer` | Referencia de documentos, fecha y responsable de revisión. |

No hay una cantidad de casos obligatoria para demostrar validez. Publicar el tamaño y la distribución reales; una muestra pequeña solo permite conclusiones exploratorias.

## Comparaciones

| Variante | Estado | Propósito |
| --- | --- | --- |
| Recuperación FTS5/BM25 sin reglas adicionales | Comparador por construir | Medir el aporte del ranking heurístico. |
| MVP por reglas | Implementación existente; calidad sin evaluar | Referencia funcional de recuperación y respuestas. |
| Recuperación semántica o híbrida | Propuesta | Medir recuperación de paráfrasis y temas nuevos. |
| Recuperación más generación con citas | Propuesta | Medir si la redacción por un LLM mejora cobertura y respaldo. |

Para comparar respuesta, mantener documentos equivalentes cuando sea posible. Para comparar recuperación, usar el mismo corpus, el mismo k y referencias etiquetadas. Separar respuestas reutilizadas desde feedback de las construidas por cada variante.

## Métricas y revisión

| Métrica | Cálculo | Precaución |
| --- | --- | --- |
| Precision@k | Documentos relevantes entre los k recuperados, dividido por k | Deduplicar por documento y establecer cómo se penalizan posiciones vacías. |
| Recall@k | Documentos relevantes recuperados, dividido por el total relevante etiquetado | Requiere referencias suficientemente completas; no calcular si el conjunto relevante está vacío. |
| Respaldo | Afirmaciones o pasos con citas que sostienen el contenido / total revisado | Evaluación humana de la relación entre cita y afirmación; citar una URL no basta. |
| Cobertura correcta | Pasos esenciales correctos y respaldados / pasos esenciales esperados | No premiar pasos adicionales sin evidencia. |
| Abstención correcta | Casos insuficientes en que el sistema reconoce la falta de evidencia / casos insuficientes | Reportar también abstenciones indebidas en preguntas respondibles. |
| Errores de contexto o vigencia | Casos con fuentes ajenas o desactualizadas / casos evaluados | Distinguir error documental de error del sistema. |
| Operación | Latencia mediana y p95, fallos, tokens y costo por consulta | Separar búsqueda/ingesta de respuesta y distinguir consultas locales de consultas web. |

Fijar una rúbrica antes de evaluar, conservar los casos individuales y reportar denominadores. Presentar métricas por tema y origen, junto con ejemplos de error. No comparar una consulta local ya cargada con una consulta web completa como si midieran la misma operación.

## Registro de una ejecución

Guardar identificador del caso, versión del código y reglas, configuración, corpus y versiones, URLs/fragmentos seleccionados, respuesta, tiempos, errores y revisión. En la futura variante generativa, agregar proveedor/modelo, prompt, parámetros, tokens y costo. El MVP guarda parte de la información documental y algunos tiempos, pero no tiene todavía este registro integral por consulta.

Publicar un informe con tamaño del conjunto, protocolo, resultados de cada variante, ejemplos representativos y limitaciones. Las cifras deben provenir de ejecuciones guardadas, no de estimaciones.

## Etapas de evolución

1. **Consolidar la base:** corregir indexación histórica, alcance de tags, filtros y observabilidad; repetir una demostración reproducible.
2. **Medir el MVP:** etiquetar preguntas y ejecutar los comparadores con una captura común.
3. **Mejorar recuperación:** dividir documentos en fragmentos con URL, versión y fecha; comparar búsqueda semántica o híbrida frente a la léxica.
4. **Incorporar generación:** entregar evidencia seleccionada a un LLM, exigir citas por paso y declarar información faltante. Tratar el texto de las páginas como datos, sin ejecutar instrucciones contenidas en él.
5. **Analizar la mejora:** comparar cobertura, respaldo, abstención y costo. Definir los criterios de aceptación antes de observar la evaluación final.

La elección de proveedor o modelo se hará al implementar, considerando calidad medida y costo. Esta documentación no añade dependencias ni claves de IA.

## Extensión al resto del portafolio

Un caso posterior sería responder preguntas sobre reportes de churn, segmentación o pronóstico citando métricas, población y limitaciones. Requiere un lector de informes locales y metadatos de proyecto/ejecución: `ingest-file` actualmente lee listas de URLs. El asistente debería distinguir métricas observadas de interpretaciones y abstenerse cuando el informe no sustente una conclusión.
