# Guía de proyectos por tema

Los veinticuatro proyectos por notebooks utilizan una organización local basada en SmartFood. Cada proyecto contiene su propio paquete en `src`, requisitos, scripts, tests, datos y reportes. Los proyectos se encuentran en `Analisis/<tema>/<proyecto>`. Las carpetas contenedoras organizan el portafolio; no constituyen dependencias. SalesAccess y Knowledge Base MVP siguen sus propias guías de aplicación.

```text
Analisis/Tema/Proyecto/
├── pyproject.toml
├── requirements.txt
├── config.json
├── src/<paquete>/
├── scripts/execute_notebooks.py
├── tests/
├── notebooks/00–06
├── data/raw, intermediate, processed, output
├── models/
├── reports/
│   ├── entorno/
│   ├── preparacion/
│   ├── eda/
│   ├── baseline/
│   ├── modelado/
│   ├── evaluacion/
│   ├── alertas/
│   ├── ejecucion/
│   └── informe_final/
└── docs/
```

`src` contiene las funciones que importan los notebooks. `scripts` contiene comandos de ejecución, no una copia alternativa de las funciones. Los notebooks resuelven su proyecto por su paquete y agregan exclusivamente su `src` al contexto de imports. Las fuentes de los proyectos se resuelven desde su propio `data/raw`; los originales conservados en `back` no participan en la ejecución.

Cada proyecto contiene instrucciones de ejecución, fuentes y registros propios en `docs`. La documentación global organiza el portafolio; no es un requisito para ejecutar ningún proyecto. Se puede copiar o renombrar una carpeta de proyecto sin copiar la carpeta temática ni otros proyectos. Dado que `data/raw` no se versiona, una copia nueva obtenida desde Git debe recuperar las entradas siguiendo su `docs/fuentes.md`.

| Tema | Proyectos por notebooks | Evidencia principal |
| --- | --- | --- |
| churn | BankChurn, SubscriptionChurn, ActivityChurn, TelecomChurn | Clasificación y evaluación de abandono |
| Recommenders | SmartFood, SpotifyRecommender, NetflixRecommender, MovieLensRecommender | Similitud descriptiva o ranking sobre valoraciones retenidas |
| NLP | IMDbSentiment, NetflixGenreClassification | Clasificación de sentimiento o categorías múltiples |
| Clustering | CustomerSegmentation, SpotifySegmentation | Separación, estabilidad y perfiles de grupos |
| Forecasting | RetailSalesForecasting, CallCenterStaffing | Pronóstico semanal y demanda/dotación por intervalo |
| AnomalyDetection | NABAnomalyDetection, IndustrialAnomalyDetection | Anomalías temporales y de sensores sintéticos |
| ComputerVision | FashionMNISTClassification, DigitsRecognition | Prendas y dígitos, métricas por clase y errores visuales |
| BusinessIntelligence | RetailKPIAnalysis | Indicadores descriptivos y reconciliación de facturación |
| CausalInference | TrainingProgramImpact | Diferencia de medias, ajuste Lin, HC3 y bootstrap |
| Regression | PowerPlantRegression | Regresión tabular e intervalos conformales |
| Optimization | WorkforceScheduling | Programación entera, pausas y auditoría de restricciones |
| GraphAnalysis | EmailCommunityAnalysis | Louvain, PageRank, ARI, NMI y estabilidad |
| SurvivalAnalysis | CustomerReturnSurvival | Kaplan–Meier, Cox penalizado y bootstrap |

## Ejecutar un proyecto

Desde la carpeta del proyecto, `python -m pip install -r requirements.txt` instala su paquete y dependencias de notebooks. Puedes usar un entorno independiente por proyecto. Para recorrer 01–05 desde terminal, utiliza `python scripts/execute_notebooks.py`; para comprobar los tests locales, `python -m unittest discover -s tests -v`.

1. Selecciona el Python de trabajo en `00_configuracion_entorno.ipynb` y ejecuta sus tres celdas. Si instala librerías, reinicia el kernel y repite 00.
2. Guarda y cierra los notebooks 01–05 que tengas abiertos.
3. Ejecuta las tres celdas de `06_ejecucion_completa.ipynb`. Revisa el resumen y las alertas. El maestro solo ejecuta su propio proyecto.

Los proyectos temáticos nuevos tienen tres celdas de ejecución por notebook individual: contexto y alertas, análisis y comentarios, tabla final de alertas. Churn y SmartFood conservan sus pasos de análisis; los maestros de los trece proyectos reorganizados tienen tres celdas. Las implementaciones se pueden inspeccionar y ampliar dentro del `src` de cada proyecto. La documentación `docs/estructura.md` de cada proyecto identifica su paquete.

El maestro ejecuta cada etapa con un kernel nuevo del Python activo, detiene la secuencia ante errores, actualiza las salidas de cada notebook completado y guarda el estado en `reports/ejecucion/resumen.json`. Ante fallo guarda la copia parcial en `reports/runs/fallos/`. No se borran reportes anteriores automáticamente: un resumen fallido impide interpretar los archivos como una pasada completa coherente.

## Artefactos

- `reports/entorno/environment.json`: intérprete, versiones y diagnóstico de dependencias.
- `reports/preparacion/preparacion.json` y `.md`: fuentes, huellas y población preparada; particiones cuando corresponden.
- `reports/eda/eda.json`, `.md`, `.png`: cifras descriptivas y figura.
- `reports/baseline/baseline.json` y `.md`: referencia simple de la tarea.
- `reports/modelado/modelado.json` y `.md`: configuración o selección del modelo.
- `reports/evaluacion/evaluacion.json` y `.md`: resultados y conclusiones automáticas.
- En churn, `baseline/baseline_validacion.json`, `modelado/modelos_validacion.json` y `evaluacion/evaluacion_test.json` conservan sus nombres; el comentario final está en `evaluacion/evaluacion.md`.
- `reports/alertas/*.json`: avisos agrupados con significado genérico y acción sugerida.
- `reports/evaluacion/perfiles_clusters.csv` y `clusters.png`: perfiles y proyección de las segmentaciones.
- `reports/evaluacion/predicciones_test.csv`: predicciones temporales de pronóstico o anomalías.

Los reportes conservan un nombre estable y se reemplazan al ejecutar su etapa. Datos preparados y modelos viven en `data/processed` y `models`; están excluidos del versionado junto con ZIPs y copias de fallo. No se necesitan descargas ni APIs durante el entrenamiento: las fuentes son los archivos locales registrados en el inventario.

## Comentarios y métricas

El texto visible se calcula junto con los resultados: tamaños, comparación con el baseline, correlación, estabilidad o presencia de categorías no aprendidas. No se certifica éxito por ausencia de warnings. No se ocultan excepciones ni se silencian todas las categorías de avisos. En clasificación, `zero_division=0` define la convención para métricas indefinidas; las matrices y los soportes permiten detectar clases sin predicción.

No hay una métrica única para todos los temas. Los recomendadores de contenido no disponen de una verdad de relevancia personal: cobertura y coincidencia de categorías son diagnósticos descriptivos. MovieLens evalúa ranking sobre valoraciones. Clustering utiliza una población descriptiva, mientras que NLP, pronóstico y anomalías tienen sus protocolos de validación y test.

## Reproducibilidad y límites

Las semillas y límites se declaran en cada `config.json`; las fuentes se identifican por SHA-256. MovieLens limita la muestra a 800 usuarios y SpotifySegmentation a 20.000 canciones para una primera ejecución manejable. Cambiar esos límites cambia el experimento.

Se conserva el test oficial de IMDb después de deduplicarlo; su coincidencia textual con train se retira de train. NetflixGenreClassification agrupa por título normalizado y deduplica sinopsis. Las categorías no conocidas en train se registran, y sus métricas solo cubren el vocabulario conocido.

RetailSalesForecasting usa semanas completas de compras positivas, con las devoluciones excluidas, y evalúa un paso adelante con datos previos reales. CallCenterStaffing agrega llamadas por intervalo y evalúa un pronóstico desde un origen fijo, con atributos de calendario y escenarios de dotación sujetos a supuestos. NAB utiliza una única serie y ventanas oficiales para métricas por punto; no implementa la puntuación oficial del benchmark.

La evaluación de MovieLens retiene las últimas dos valoraciones por usuario, sin un corte global: no representa una simulación completamente causal de una plataforma en una fecha común. No se usa la validación para reentrenar en esta primera versión. Los próximos experimentos deben contemplar que el test vigente ya se ha observado.

## Reorganización de la raíz

La raíz organiza los recorridos por notebooks en `Analisis`, las aplicaciones de dashboards en `BusinessIntelligence` y los asistentes/MVP en `IAG`, junto a documentación global, archivos en `back` y configuración del editor/versionado. Los antiguos paquetes y scripts globales están respaldados en `back/.local/homologacion_20261007/`; no participan en la ejecución actual. El [registro de estructura](verificacion_estructura.json) documenta las comprobaciones de rutas, apertura, comandos y notebooks 00/05. Las métricas y tiempos de los maestros anteriores mantienen su carácter histórico; esta reorganización no vuelve a seleccionar los modelos.

Todos los proyectos de análisis agrupan sus reportes por etapa. Los JSON, Markdown y figuras se guardan en `reports/entorno/`, `preparacion/`, `eda/`, `baseline/`, `modelado/` y `evaluacion/`, según los artefactos que produzca cada etapa. SmartFood agrupa sus inspecciones en `reports/eda/<dataset>/`. Alertas y resumen permanecen en `reports/alertas/` y `reports/ejecucion/`.

## Comprobación de la distribución de reportes

El [registro de comprobación](verificacion_reportes.json) reúne las verificaciones de rutas, notebooks afectados, pruebas locales y enlaces. Esta revisión utiliza los modelos existentes; el resumen de cada maestro conserva su última ejecución completa. Las carpetas por etapa aparecen cuando hay artefactos que guardar; la estructura no implica que todos los notebooks exporten los mismos tipos de reporte.

## Informes integrales

Cada proyecto dispone de `reports/informe_final/informe_final.md`, actualizado por el maestro y las celdas finales de sus análisis. Consulta el [índice de informes y su actualización](informes_integrales.md).

FashionMNISTClassification utiliza fuentes oficiales verificadas, archivos NPZ locales y una evaluación reservada sobre el test oficial. La primera versión compara modelos en CPU, con una MLP densa; las convoluciones se plantean como ampliación. Consulta su [metodología](../Analisis/ComputerVision/FashionMNISTClassification/docs/metodologia.md).

## Nuevas incorporaciones: alcance

IndustrialAnomalyDetection utiliza AI4I sintético; DigitsRecognition usa imágenes 8×8 de scikit-learn; RetailKPIAnalysis es BI descriptivo y su etapa 04 construye indicadores, sin entrenar un modelo; CallCenterStaffing utiliza 5.000 registros de Kaggle, con cobertura operativa asumida. Este último calcula escenarios de dotación por intervalo, sin optimizar turnos ni acreditar el SLA real. Cada proyecto documenta su fuente y metodología y genera su informe en la misma ruta `reports/informe_final/informe_final.md`.

## Separación entre análisis y aplicaciones

`Analisis` contiene los veinticuatro recorridos por notebooks. RetailKPIAnalysis se ubica en `Analisis/BusinessIntelligence`; SalesAccess, como aplicación Streamlit, está en `BusinessIntelligence/SalesAccess`. IAG agrupa asistentes y MVP, incluido `IAG/knowledge_base_mvp`. Knowledge Base MVP conserva su ejecución independiente de consola y documenta su integración generativa como propuesta.

Después del traslado, abre los notebooks desde sus rutas nuevas y reinicia sus kernels para que no conserven directorios o imports de la ubicación anterior. Los resultados guardados mantienen las fechas y rutas del entorno en que se calcularon; el registro del traslado distingue esta revisión de una nueva ejecución de modelos.

Causalidad, regresión y optimización añaden preguntas diferentes. Consulta la [ampliación y sus protocolos](ampliacion_analisis.md) para entender la distinción respecto a clasificación, pronóstico y dotación por intervalo.

[Grafos, supervivencia y complementos](ampliacion_analisis_oct08.md) describe los nuevos protocolos y su ejecución.
