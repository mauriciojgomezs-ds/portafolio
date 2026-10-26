# Inventario de datasets

Revisión del 7 de octubre de 2026. Este inventario registra archivos disponibles y su alcance. Los nueve proyectos temáticos ya tienen notebooks implementados; el estado de la comprobación inicial se registra en [ejecuciones_proyectos.json](ejecuciones_proyectos.json). Los tamaños y SHA-256 de los archivos revisados están en [inventario_datasets.json](inventario_datasets.json).

## Archivos disponibles

| Fuente local | Contenido comprobado | Proyecto posible |
| --- | --- | --- |
| `back/Netflix Movies and TV Shows.zip` | `netflix_titles.csv`: títulos, tipo, reparto, países, año, clasificación, duración, categorías y descripción | Recomendación por contenido; clasificación multietiqueta desde la sinopsis |
| `back/Spotify Tracks Dataset.zip` | `dataset.csv`: canciones, artistas, género y características musicales, como energía, tempo y valence | Recomendación de canciones similares; segmentación musical; clasificación de géneros |
| `back/movieLens.zip` | MovieLens 32M: películas, valoraciones, etiquetas y enlaces de identificadores | Recomendación colaborativa e híbrida con evaluación por usuario |
| `back/OnlineRetailUCI.zip` | `Online Retail.xlsx` | Segmentación de clientes y pronóstico de ventas, con revisión inicial pendiente |
| `back/NAB.zip` | Repositorio NAB completo: 58 series CSV y etiquetas para 58 series en `labels/combined_windows.json` | Detección de anomalías en series temporales |
| `back/IMDb/train.parquet` | 25.000 reseñas; columnas `text`, `label` | Entrenamiento y validación de clasificación de sentimiento |
| `back/IMDb/test.parquet` | 25.000 reseñas; columnas `text`, `label` | Evaluación final de sentimiento |
| `back/OneDrive_1_6-10-2026.zip` | `recipes.parquet`, `reviews.parquet` | Archivo de recetas y reseñas; contrastar con las fuentes de SmartFood antes de reutilizarlo |

Se comprobó la integridad interna de todos los ZIP de `back/` y se leyeron los metadatos de ambos Parquet de IMDb. Esto acredita legibilidad, no limpieza ni ausencia de duplicados en los registros. Los originales se conservan en `back/`; cada proyecto tiene una copia de las entradas que necesita en su propio `data/raw/`, con huellas e instrucciones en `docs/fuentes.json` y `docs/fuentes.md`. Ningún proyecto necesita leer `back` para ejecutarse.

## Fuentes y descargas

- **Netflix:** [Netflix Movies and TV Shows en Kaggle](https://www.kaggle.com/datasets/shivamb/netflix-shows). Debe confirmarse que este enlace corresponde a la descarga local antes de registrar la procedencia como definitiva.
- **Spotify Tracks:** [Spotify Tracks Dataset en Kaggle](https://www.kaggle.com/datasets/maharshipandya/-spotify-tracks-dataset). El archivo local ya está disponible; la procedencia exacta y condiciones de uso deben confirmarse antes de publicación.
- **MovieLens:** [GroupLens](https://grouplens.org/datasets/movielens/). El ZIP local contiene `ml-32m/README.txt`, condiciones de uso y checksums. La versión completa es grande: su CSV de valoraciones ocupa aproximadamente 877 MB sin comprimir. Conviene procesar por partes o definir una muestra reproducible para la primera iteración.
- **Online Retail:** [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/352/online+retail). La correspondencia exacta de la descarga local queda por confirmar en la revisión del archivo.
- **NAB:** [repositorio oficial](https://github.com/numenta/NAB), [ZIP de la rama master](https://codeload.github.com/numenta/NAB/zip/refs/heads/master). Descargado como `back/NAB.zip`; incluye datos, etiquetas, documentación y licencia. Se necesita conservar las etiquetas para evaluar las detecciones. El SHA-256 identifica esta descarga, dado que master puede cambiar.
- **IMDb:** [ficha de Stanford NLP en Hugging Face](https://huggingface.co/datasets/stanfordnlp/imdb) y [archivos Parquet](https://huggingface.co/datasets/stanfordnlp/imdb/tree/main/plain_text). Descargados train y test, junto con la ficha en [README_fuente.md](../back/IMDb/README_fuente.md). No se descargó la partición adicional sin etiquetas, innecesaria para el primer experimento supervisado.

Los scripts de descarga propios de [NABAnomalyDetection](../Analisis/AnomalyDetection/NABAnomalyDetection/scripts/download_sources.py) e [IMDbSentiment](../Analisis/NLP/IMDbSentiment/scripts/download_sources.py) recuperan sus fuentes si faltan y conservan archivos existentes. Las rutas se leen desde el `config.json` de cada proyecto. Después de una descarga nueva deben comprobarse los archivos y actualizarse las huellas del inventario.

## Qué permite cada fuente

**Spotify Tracks** no incluye historial de escuchas ni playlists. Permite recomendar por similitud de características, pero no evaluar preferencias personales reales. Si se predice `track_genre`, esta columna queda fuera de las entradas; antes de partir datos se revisarán canciones repetidas y artistas compartidos. La columna inicial sin nombre del CSV también debe revisarse como posible índice exportado.

**Spotify Million Playlist Dataset** es otra fuente. La [página actual de AIcrowd](https://www.aicrowd.com/challenges/spotify-million-playlist-dataset-challenge) avisa que ya no está disponible para descarga y remite a Spotify Research para solicitar acceso. No se necesita para iniciar el proyecto con el ZIP disponible.

**Netflix** aporta metadatos de catálogo; no se encontró un archivo de valoraciones o interacciones de usuarios dentro del ZIP. La semántica de `rating` debe comprobarse: no se utilizará como puntuación de usuarios sin documentación. Para clasificación de géneros se usarían descripciones como entrada y las categorías como etiquetas, sin introducir las etiquetas en las features.

**MovieLens** aporta valoraciones de usuarios. Puede abordarse como proyecto independiente; compartir el dominio cinematográfico con Netflix no garantiza que ambos catálogos puedan cruzarse sin ambigüedades.

**IMDb** se utilizaría para sentimiento positivo/negativo de reseñas en inglés, no para clasificación de géneros. Se conservará el test oficial; la validación se obtendrá de train.

**NAB** permite evaluar detección de eventos anómalos con ventanas temporales. El protocolo deberá respetar el orden temporal y evitar ajustar umbrales usando las anomalías del test. Un conteo de puntos correctamente clasificados no equivale por sí solo a la puntuación oficial NAB.

## Recorrido propuesto

Los proyectos se distribuyen en Recommenders, NLP, Clustering, Forecasting y AnomalyDetection, junto a churn y SmartFood. Cada proyecto tiene entorno, preparación, EDA, baseline, modelado y evaluación, más un maestro de ejecución, reportes estables y alertas descritas. Consulta la [guía temática](proyectos_tematicos.md) y los reportes de cada proyecto para revisar resultados realmente ejecutados.

## Fashion-MNIST

Las cuatro fuentes oficiales gzip/IDX se guardan en `Analisis/ComputerVision/FashionMNISTClassification/data/raw/`. La descarga comprueba los MD5 publicados por [Zalando Research](https://github.com/zalandoresearch/fashion-mnist); el proyecto registra SHA-256 y conteos en [preparación](../Analisis/ComputerVision/FashionMNISTClassification/reports/preparacion/preparacion.json). El test oficial se conserva íntegro y la muestra de desarrollo se documenta en su [metodología](../Analisis/ComputerVision/FashionMNISTClassification/docs/metodologia.md).

## Nuevas fuentes: sensores, dígitos, retail y call center

| Proyecto | Fuente | Copia independiente |
| --- | --- | --- |
| IndustrialAnomalyDetection | [AI4I 2020, UCI](https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset), sintético | `Analisis/AnomalyDetection/IndustrialAnomalyDetection/data/raw/AI4I.zip` |
| RetailKPIAnalysis | [Online Retail, UCI](https://archive.ics.uci.edu/dataset/352/online+retail), GBP | `Analisis/BusinessIntelligence/RetailKPIAnalysis/data/raw/OnlineRetailUCI.zip` |
| DigitsRecognition | [load_digits, scikit-learn](https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_digits.html), 1.797 imágenes 8×8 | `Analisis/ComputerVision/DigitsRecognition/data/raw/digits.npz` |
| CallCenterStaffing | [Call Center Dataset, Kaggle](https://www.kaggle.com/datasets/akash1vishwakarma/call-center-dataset), 5.000 llamadas | `Analisis/Forecasting/CallCenterStaffing/data/raw/CallCenterKaggle.zip` |

Las fuentes permanecen dentro de cada proyecto y se recuperan con su script `download_sources.py`. El archivo de Kaggle no acredita origen operativo ni integridad; horario, cobertura y disponibilidad se asumen en el análisis. Las fuentes no se cruzan entre proyectos. Huellas y controles de las nuevas incorporaciones: [registro de verificación](verificacion_nuevos_proyectos.json).

## Fuentes de los nuevos análisis

| Proyecto | Fuente y ubicación propia | Alcance |
| --- | --- | --- |
| TrainingProgramImpact | [NSW experimental, selección Dehejia](https://users.nber.org/~rdehejia/data/.nswdata2.html); `Analisis/CausalInference/TrainingProgramImpact/data/raw` | 445 participantes; archivos tratados y controles RE74; ingresos históricos |
| PowerPlantRegression | [UCI Combined Cycle Power Plant](https://archive.ics.uci.edu/dataset/294/combined+cycle+power+plant); `Analisis/Regression/PowerPlantRegression/data/raw/CCPP.zip` | 9.568 filas originales; solo Sheet1, porque las otras hojas reordenan las mismas observaciones; CC BY 4.0 |
| WorkforceScheduling | `Analisis/Optimization/WorkforceScheduling/data/raw/demand.csv` y `employees.csv` | Escenario sintético explícito: siete días, 140 franjas y 14 empleados ficticios; origen guardado en JSON |

Las huellas y tamaños de estas fuentes están en el inventario JSON. Cada proyecto explica recuperación y preparación en su propia guía de fuentes.

## Grafos y supervivencia

- [Stanford email-Eu-core](https://snap.stanford.edu/data/email-Eu-core.html): aristas y etiquetas departamentales en `Analisis/GraphAnalysis/EmailCommunityAnalysis/data/raw`; GZ originales propios.
- [UCI Online Retail](https://archive.ics.uci.edu/dataset/352/online+retail): copia independiente `Analisis/SurvivalAnalysis/CustomerReturnSurvival/data/raw/OnlineRetailUCI.zip`; CC BY 4.0, Daqing Chen (2015). Se usa tiempo hasta segunda compra, no se reutilizan métricas de otros proyectos.
- Preferencias de turnos: `Analisis/Optimization/WorkforceScheduling/data/raw/preferences.csv`, inicios preferidos ficticios generados por índice de empleado módulo 5; no respuestas de trabajadores reales.
