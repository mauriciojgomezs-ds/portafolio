# Referencias académicas y lectura actual

El proyecto procede de un trabajo académico sobre sistemas de recomendación. Estos archivos se conservan como fuentes originales; la documentación del portafolio describe el código y la evidencia que pueden comprobarse actualmente.

## Fuentes conservadas

| Documento | Qué aporta |
| --- | --- |
| [Enunciado del trabajo final](references/Enunciado_Trabajo_final.pdf) | Objetivos, criterios de evaluación y casos de estudio solicitados |
| [Informe académico original](references/TF_RS_Mauricio_Gomez_Sandoval.docx) | Diseño, resultados y conclusiones presentados por Mauricio Gómez Sandoval el 5 de abril de 2025 |
| [README original](archive/README_original.md) | Organización, funciones y descripción de datos de la versión inicial |

Se revisó el texto completo del enunciado y se inspeccionaron sus dos páginas. Se extrajo el contenido del informe Word, incluidos sus casos de estudio. No se validó su maquetación: el renderizador no encontró LibreOffice. Ninguno de los originales fue reescrito.

## Qué pide el enunciado

El trabajo solicita explorar NMF, SVM y un enfoque basado en perfil de usuario, describir datos y decisiones, separar entrenamiento y test y evaluar mediante RMSE. Pide al menos dos casos de estudio, perfiles e ítems preferidos y las tres mejores recomendaciones para comparar los métodos.

Las restricciones de la entrega académica, como extensión del informe o duración de la presentación, corresponden a su contexto original. El portafolio necesita además instrucciones de reproducción, evidencia trazable y una interpretación correcta de las métricas.

El enunciado propone una base provista por el curso o una base del lugar de trabajo; el informe atribuye sus datos a Kaggle. Los archivos revisados no explican cómo se acordó esa elección. La documentación del portafolio mantiene la procedencia declarada y no infiere una autorización académica.

## Afirmaciones del informe que requieren actualizarse

| Tema | Informe original | Lectura respaldada por la revisión |
| --- | --- | --- |
| Volumen de datos | Menciona más de 84.000 recetas y 226.000 reseñas | Los Parquet locales contienen 522.517 recetas y 1.401.982 reseñas; falta identificar si se trata de la misma versión o de subconjuntos diferentes |
| Componentes NMF | Presenta 70 como mejor resultado | La búsqueda guardada obtiene menor RMSE con 10; 70 es la selección histórica utilizada |
| Calidad del SVM | Concluye mejor desempeño y personalización | El clasificador usa atributos de receta, y el test guardado predice solo positivos; no se demuestra superioridad ni personalización aprendida |
| Similitud por receta | Presenta rankings como recetas similares | La función SVM ordena por margen global y excluye la referencia; no calcula semejanza con esa receta |
| Consulta por ingredientes | Presenta recomendaciones para una consulta textual | La implementación sustituye el texto de los candidatos por la consulta; no mide similitud con sus ingredientes reales |
| Evaluación del perfil | Describe revisión manual de ejemplos | Los ejemplos apoyan una revisión cualitativa; no equivalen a una métrica de precisión reproducible |
| Comparación entre métodos | Reúne error NMF, clasificación SVM y casos manuales | Son tareas y protocolos distintos; hace falta una evaluación común de ranking para compararlos |

Los valores y ejemplos del informe se consideran históricos. No se trasladan al portafolio como resultados regenerados sin el protocolo y los artefactos que permitan reproducirlos.

## Cómo aprovechar estas referencias

El informe permite recuperar la motivación, decisiones y casos de estudio originales. Para la siguiente versión, conviene repetir dos casos bajo el mismo conjunto de candidatos, conservar IDs originales, mostrar top-3 por método y explicar por qué se recomendaron.

La comparación debe complementar los ejemplos con métricas apropiadas y baselines. El [análisis de evaluación](evaluacion.md) desarrolla los límites actuales; el [plan de mejoras](mejoras.md) define el trabajo pendiente.
