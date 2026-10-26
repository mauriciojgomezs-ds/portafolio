# Portafolio de ciencia de datos e inteligencia artificial

![Python](https://img.shields.io/badge/python-3.10%2B-blue) ![scikit--learn](https://img.shields.io/badge/scikit--learn-1.6%2B-orange) ![pandas](https://img.shields.io/badge/pandas-2.x-150458) ![Jupyter](https://img.shields.io/badge/Jupyter-notebooks-F37626) ![proyectos](https://img.shields.io/badge/proyectos_de_análisis-24-success) ![notebooks](https://img.shields.io/badge/notebooks-168-success) ![apps](https://img.shields.io/badge/apps_IA_%2F_BI-5%2B1-success)

Proyectos que muestran el recorrido desde los datos hasta una conclusión o una aplicación: el problema, las decisiones, la evidencia y los límites de cada solución.

El portafolio se organiza en tres líneas. Cada proyecto conserva su código, dependencias, datos y documentación propios.

## Resultados destacados

- **[PowerPlantRegression](Analisis/Regression/PowerPlantRegression/README.md)** — MAE 2,47 MW prediciendo potencia de una planta, con intervalos de predicción y diagnóstico de multicolinealidad (VIF) y residuos.
- **[IMDbSentiment](Analisis/NLP/IMDbSentiment/README.md)** — clasificación de sentimiento con F1 macro inicial 0,88 sobre reseñas de películas.
- **[FashionMNISTClassification](Analisis/ComputerVision/FashionMNISTClassification/README.md)** — 85,18 % de accuracy comparando un baseline lineal contra un MLP sobre imágenes.
- **[CustomerReturnSurvival](Analisis/SurvivalAnalysis/CustomerReturnSurvival/README.md)** — modelo de supervivencia (Kaplan–Meier + Cox penalizado) con C-index de test 0,562, censura y estacionalidad documentadas.
- **[SalesAccess](BusinessIntelligence/SalesAccess/README.md)** — dashboard Streamlit con autenticación local y acceso por rol/segmento sobre una demo sintética de 40 agentes.

Cada resultado está acompañado de sus límites y supuestos explícitos: el objetivo del portafolio es mostrar el razonamiento completo, no solo la métrica final.

| Línea | Contenido | Punto de entrada |
| --- | --- | --- |
| Análisis de ciencia de datos | 24 proyectos por notebooks en 13 temas, con reportes e informes automáticos | [Analisis](Analisis/README.md) |
| Business Intelligence | Aplicaciones de dashboards y acceso a información de negocio | [BusinessIntelligence](BusinessIntelligence/README.md) |
| IA generativa aplicada y MVP | Asistentes y prototipos; el grado de integración con IA se documenta por proyecto | [IAG](IAG/README.md) |

## Análisis de ciencia de datos

Los proyectos de [Analisis](Analisis/README.md) abordan abandono, recomendación, texto, segmentación, pronóstico, anomalías, visión, indicadores de negocio, inferencia causal, regresión, optimización, redes y supervivencia. Comparten una organización por etapas y producen comentarios a partir de sus resultados calculados.

| Área | Proyecto | Técnicas | Estado |
| --- | --- | --- | --- |
| Predicción de abandono | [BankChurn](Analisis/churn/BankChurn/README.md) | Regresión logística, calibración y umbrales | Ejecutado; comparación original y políticas de decisión documentadas |
| Predicción de abandono | [SubscriptionChurn](Analisis/churn/SubscriptionChurn/README.md) | Clasificación, calibración y revisión de distribuciones | Ejecutado; diferencias entre validación y test por investigar |
| Predicción de abandono | [ActivityChurn](Analisis/churn/ActivityChurn/README.md) | Evaluación temporal, calibración y umbrales | Ejecutado; definición temporal del objetivo por confirmar |
| Predicción de abandono | [TelecomChurn](Analisis/churn/TelecomChurn/README.md) | Clasificación, calibración y costes ilustrativos | Ejecutado; original detecta 28 de 95; políticas adicionales evaluadas |
| Sistemas de recomendación | [SmartFood](Analisis/Recommenders/SmartFood/README.md) | EDA, TF-IDF, NMF, SVM y pipelines de scikit-learn | Ejecutado; evaluación de ranking pendiente |
| Sistemas de recomendación | [SpotifyRecommender](Analisis/Recommenders/SpotifyRecommender/README.md) | Características musicales, escalamiento y vecinos por coseno | Ejecutado; evaluación descriptiva |
| Sistemas de recomendación | [NetflixRecommender](Analisis/Recommenders/NetflixRecommender/README.md) | TF-IDF y similitud de sinopsis y metadatos | Ejecutado; evaluación descriptiva |
| Sistemas de recomendación | [MovieLensRecommender](Analisis/Recommenders/MovieLensRecommender/README.md) | Vecinos de usuarios, popularidad y NDCG | Ejecutado; supera el baseline en la muestra |
| Procesamiento de texto | [IMDbSentiment](Analisis/NLP/IMDbSentiment/README.md) | TF-IDF y clasificación de sentimiento | Ejecutado; F1 macro inicial 0,88 |
| Procesamiento de texto | [NetflixGenreClassification](Analisis/NLP/NetflixGenreClassification/README.md) | Clasificación multietiqueta desde sinopsis | Ejecutado; detección limitada por categoría |
| Segmentación | [CustomerSegmentation](Analisis/Clustering/CustomerSegmentation/README.md) | RFM, KMeans y perfiles de clientes | Ejecutado; perfiles y estabilidad documentados |
| Segmentación | [SpotifySegmentation](Analisis/Clustering/SpotifySegmentation/README.md) | KMeans, PCA y estabilidad entre semillas | Ejecutado; perfiles y estabilidad documentados |
| Pronóstico | [RetailSalesForecasting](Analisis/Forecasting/RetailSalesForecasting/README.md) | Rezagos, Ridge y evaluación temporal a un paso | Ejecutado; no supera el baseline |
| Pronóstico | [CallCenterStaffing](Analisis/Forecasting/CallCenterStaffing/README.md) | Demanda por intervalo, Poisson y Erlang C | Ejecutado; no mejora MAE del baseline; dotación bajo supuestos |
| Detección de anomalías | [NABAnomalyDetection](Analisis/AnomalyDetection/NABAnomalyDetection/README.md) | Score causal móvil y umbrales de validación | Ejecutado; detección inicial baja |
| Detección de anomalías | [IndustrialAnomalyDetection](Analisis/AnomalyDetection/IndustrialAnomalyDetection/README.md) | Z-scores, Isolation Forest y umbrales de validación | Ejecutado; recall de fallos bajo en fuente sintética |
| Visión computacional | [FashionMNISTClassification](Analisis/ComputerVision/FashionMNISTClassification/README.md) | Imágenes, baseline lineal, MLP y análisis visual de errores | Ejecutado; accuracy 85.18%; convergencia pendiente de revisar |
| Visión computacional | [DigitsRecognition](Analisis/ComputerVision/DigitsRecognition/README.md) | Gradientes, SVM y prueba de desplazamiento | Ejecutado; sensibilidad al desplazamiento documentada |
| Business Intelligence | [RetailKPIAnalysis](Analisis/BusinessIntelligence/RetailKPIAnalysis/README.md) | Indicadores en GBP, reconciliación y dashboard local | Ejecutado; indicadores reconciliados y meses parciales señalados |
| Inferencia causal | [TrainingProgramImpact](Analisis/CausalInference/TrainingProgramImpact/README.md) | Diferencia de medias, ajuste Lin, HC3 y bootstrap | Ejecutado; efecto en muestra experimental histórica |
| Regresión | [PowerPlantRegression](Analisis/Regression/PowerPlantRegression/README.md) | Regresión tabular e intervalos conformales | Ejecutado; MAE 2,47 MW; cobertura observada 88,35 % |
| Optimización | [WorkforceScheduling](Analisis/Optimization/WorkforceScheduling/README.md) | Programación entera, pausas, equilibrio y preferencias sintéticas | Ejecutado; planes factibles y gap del solver documentados |
| Análisis de redes | [EmailCommunityAnalysis](Analisis/GraphAnalysis/EmailCommunityAnalysis/README.md) | Louvain, PageRank, ARI, NMI y estabilidad | Ejecutado; comparación descriptiva y variación entre semillas |
| Supervivencia | [CustomerReturnSurvival](Analisis/SurvivalAnalysis/CustomerReturnSurvival/README.md) | Kaplan–Meier, Cox penalizado y bootstrap | Ejecutado; C-index de test 0,562; censura y estacionalidad documentadas |

Los resultados corresponden a fuentes, poblaciones y protocolos distintos. Las métricas vigentes y sus limitaciones se consultan en los [informes integrales](docs/informes_integrales.md); completar una ejecución no acredita utilidad en producción.

## Aplicaciones y MVP

| Área | Proyecto | Técnicas | Estado |
| --- | --- | --- | --- |
| Business Intelligence | [SalesAccess](BusinessIntelligence/SalesAccess/README.md) | Streamlit, autenticación local y acceso por rol/segmento | Demo sintética con 40 agentes; adaptador opcional de Kaggle |
| Análisis documental | [Knowledge Base MVP](IAG/knowledge_base_mvp/README.md) | Scraping, SQLite FTS5/BM25 y ranking por reglas | MVP documental; integración con IA generativa pendiente |
| IA generativa aplicada | [MeetingCopilot](IAG/MeetingCopilot/README.md) | Recuperación léxica, conector LLM con citas y evaluación ponderada de agenda | Conector implementado; prueba con proveedor real pendiente |
| IA y análisis tabular | [DataCopilot](IAG/DataCopilot/README.md) | Perfil de calidad, preguntas y operaciones controladas | MVP local ejecutado; interpretación con IA pendiente de prueba real |
| Procesamiento documental | [DocumentAnalyzer](IAG/DocumentAnalyzer/README.md) | Conversión, campos con evidencia, validación y adaptador OCR | MVP de texto ejecutado; motores externos pendientes de prueba real |

[SalesAccess](BusinessIntelligence/SalesAccess/README.md) es una aplicación Streamlit con vistas y acceso por rol y segmento. [Knowledge Base MVP](IAG/knowledge_base_mvp/README.md) recupera documentación y construye respuestas mediante reglas; su evolución hacia IA generativa se describe en la [ficha de portafolio](IAG/knowledge_base_mvp/docs/portafolio.md). [MeetingCopilot](IAG/MeetingCopilot/README.md) incorpora búsqueda local y un conector de preguntas con IA y citas; su README distingue las pruebas simuladas de las llamadas reales pendientes.

Estar dentro de IAG identifica la línea del proyecto. El estado publicado indica qué capacidades están implementadas y cuáles siguen propuestas.

Puedes probar los tres copilotos desde el [Laboratorio local](IAG/PortfolioDemo/README.md) y consultar su [documentación con capturas de consultas reales](IAG/PortfolioDemo/docs/demostracion.md).

## Presentación web

La carpeta [SitioWeb](SitioWeb/README.md) contiene la página de presentación, el catálogo con filtros, los informes consultables y las demos de los MVP. Se genera desde la documentación guardada y puede publicarse junto con este repositorio en GitHub Pages. Consulta la [guía del sitio](docs/sitio_web.md) para personalizar el perfil, añadir videos y publicarlo.

## Organización de carpetas

```text
portafolio/
├── Analisis/
│   └── <tema>/<proyecto>/
├── BusinessIntelligence/
│   └── SalesAccess/
├── IAG/
│   ├── knowledge_base_mvp/
│   ├── MeetingCopilot/
│   ├── DataCopilot/
│   └── DocumentAnalyzer/
├── docs/
├── SitioWeb/
└── back/
```

RetailKPIAnalysis pertenece a `Analisis/BusinessIntelligence`: su dashboard HTML es un resultado del análisis. SalesAccess tiene un flujo de aplicación propio. Las carpetas contenedoras organizan el portafolio y no aportan dependencias compartidas.

## Ejecutar y consultar resultados

Para un análisis, abre la carpeta del proyecto, instala su `requirements.txt` y selecciona el Python correspondiente. Ejecuta 00 para comprobar el entorno y después las tres celdas de 06 para recorrer las cinco etapas. El maestro se detiene ante errores y registra el avance. Cada proyecto documenta sus nombres de notebooks, fuentes y parámetros.

El informe principal está en `Analisis/<tema>/<proyecto>/reports/informe_final/informe_final.md`. Los reportes detallados se agrupan por etapa; las alertas incluyen su mensaje original y una descripción genérica. También puedes reunir los reportes guardados con `python scripts/generate_report.py` desde el proyecto, sin volver a entrenar.

Las aplicaciones de BusinessIntelligence e IAG se ejecutan según su propio README. Knowledge Base MVP utiliza consola y SQLite; SalesAccess utiliza Streamlit; MeetingCopilot dispone de comandos de demostración y consulta. Sus flujos son independientes del maestro de notebooks.

Los análisis utilizan sus fuentes locales de `data/raw`; `back` conserva archivos originales y respaldos. Al copiar un proyecto, conserva sus datos o recupéralos siguiendo la guía local y crea un entorno para la máquina de destino.

## Documentación del portafolio

- [Organización y autonomía](docs/organizacion_portafolio.md).
- [Guía de los análisis por tema](docs/proyectos_tematicos.md).
- [Índice de informes integrales](docs/informes_integrales.md).
- [Inventario de datasets](docs/inventario_datasets.md).
- [Primera revisión de resultados](docs/resultados_iniciales.md): registro histórico; los informes locales conservan los resultados vigentes.
- [Grafos, supervivencia y complementos de evaluación](docs/ampliacion_analisis_oct08.md).
- [Comprobaciones de esta ampliación](docs/verificacion_analisis_oct08.json).
- [Nuevos análisis y diferencias de alcance](docs/ampliacion_analisis.md).
- [Verificación de los nuevos proyectos](docs/verificacion_analisis_incorporados.json).
- [Verificación del traslado de los análisis](docs/verificacion_organizacion_analisis.json): 19 proyectos y 133 notebooks comprobados, sin repetir entrenamiento.

Inferencia causal, regresión y optimización ya cuentan con proyectos ejecutados. Los proyectos de IA se desarrollan dentro de IAG con su alcance y evaluación propios.
