# Informes integrales del portafolio

Cada proyecto tiene una entrada clara en `reports/informe_final/informe_final.md`. Su JSON complementario conserva las cifras disponibles, estado del maestro, fechas y huellas de los archivos utilizados. Los informes se generan con código local y reglas explícitas, sin depender de servicios de IA o de otros proyectos.

| Tema | Informe integral |
| --- | --- |
| Recommenders | [MovieLensRecommender](../Analisis/Recommenders/MovieLensRecommender/reports/informe_final/informe_final.md) |
| Recommenders | [NetflixRecommender](../Analisis/Recommenders/NetflixRecommender/reports/informe_final/informe_final.md) |
| Recommenders | [SmartFood](../Analisis/Recommenders/SmartFood/reports/informe_final/informe_final.md) |
| Recommenders | [SpotifyRecommender](../Analisis/Recommenders/SpotifyRecommender/reports/informe_final/informe_final.md) |
| churn | [ActivityChurn](../Analisis/churn/ActivityChurn/reports/informe_final/informe_final.md) |
| churn | [BankChurn](../Analisis/churn/BankChurn/reports/informe_final/informe_final.md) |
| churn | [SubscriptionChurn](../Analisis/churn/SubscriptionChurn/reports/informe_final/informe_final.md) |
| churn | [TelecomChurn](../Analisis/churn/TelecomChurn/reports/informe_final/informe_final.md) |
| NLP | [IMDbSentiment](../Analisis/NLP/IMDbSentiment/reports/informe_final/informe_final.md) |
| NLP | [NetflixGenreClassification](../Analisis/NLP/NetflixGenreClassification/reports/informe_final/informe_final.md) |
| Clustering | [CustomerSegmentation](../Analisis/Clustering/CustomerSegmentation/reports/informe_final/informe_final.md) |
| Clustering | [SpotifySegmentation](../Analisis/Clustering/SpotifySegmentation/reports/informe_final/informe_final.md) |
| Forecasting | [RetailSalesForecasting](../Analisis/Forecasting/RetailSalesForecasting/reports/informe_final/informe_final.md) |
| AnomalyDetection | [NABAnomalyDetection](../Analisis/AnomalyDetection/NABAnomalyDetection/reports/informe_final/informe_final.md) |
| ComputerVision | [FashionMNISTClassification](../Analisis/ComputerVision/FashionMNISTClassification/reports/informe_final/informe_final.md) |
| AnomalyDetection | [IndustrialAnomalyDetection](../Analisis/AnomalyDetection/IndustrialAnomalyDetection/reports/informe_final/informe_final.md) |
| BusinessIntelligence | [RetailKPIAnalysis](../Analisis/BusinessIntelligence/RetailKPIAnalysis/reports/informe_final/informe_final.md) |
| ComputerVision | [DigitsRecognition](../Analisis/ComputerVision/DigitsRecognition/reports/informe_final/informe_final.md) |
| Forecasting | [CallCenterStaffing](../Analisis/Forecasting/CallCenterStaffing/reports/informe_final/informe_final.md) |
| CausalInference | [TrainingProgramImpact](../Analisis/CausalInference/TrainingProgramImpact/reports/informe_final/informe_final.md) |
| Regression | [PowerPlantRegression](../Analisis/Regression/PowerPlantRegression/reports/informe_final/informe_final.md) |
| Optimization | [WorkforceScheduling](../Analisis/Optimization/WorkforceScheduling/reports/informe_final/informe_final.md) |
| GraphAnalysis | [EmailCommunityAnalysis](../Analisis/GraphAnalysis/EmailCommunityAnalysis/reports/informe_final/informe_final.md) |
| SurvivalAnalysis | [CustomerReturnSurvival](../Analisis/SurvivalAnalysis/CustomerReturnSurvival/reports/informe_final/informe_final.md) |

## Actualizar un informe

Ejecuta el maestro 06 del proyecto para recorrer 01–05 y actualizar el informe durante el avance, al terminar o ante un fallo. La celda final de cada notebook individual también lo actualiza con los reportes que existan. Para reunir resultados guardados sin volver a entrenar, utiliza `python scripts/generate_report.py` desde la carpeta del proyecto. El maestro conserva sus tres celdas de ejecución.

Los reportes se reemplazan con una única versión vigente. Un maestro incompleto, etapas sin reporte, errores guardados o actualizaciones posteriores a la última pasada completa se indican explícitamente. La ausencia de warnings no acredita validez del modelo; revisa protocolos, fechas y limitaciones antes de publicar.

En SmartFood, 01 y 03–05 exportan cifras y comentarios a sus carpetas de etapa; 02 mantiene sus conclusiones del EDA. La primera exportación de los modelos reutilizó comentarios calculados en salidas guardadas, identificando su procedencia. Al repetir los notebooks, se reemplazan con métricas calculadas directamente en las celdas.

Las guías `docs/informe_final.md` de cada proyecto explican contenido, actualización y criterios de interpretación. Las cifras de tareas diferentes no se comparan directamente entre proyectos.
