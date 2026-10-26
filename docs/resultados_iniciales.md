# Primera revisión de los proyectos temáticos

El 7 de octubre de 2026 se ejecutaron 00 y 06 de los nueve proyectos nuevos. Los maestros completaron preparación, EDA, baseline, modelado y evaluación. Después se comprobaron nuevamente las etapas con mejoras de tablas, figuras y comentarios, sin modificar las particiones ni los criterios de selección. El [registro JSON](ejecuciones_proyectos.json) conserva ambas comprobaciones y los avisos por notebook.

| Proyecto | Evidencia inicial | Lectura |
| --- | --- | --- |
| [SpotifyRecommender](../Analisis/Recommenders/SpotifyRecommender/reports/evaluacion/evaluacion.md) | Catálogo de 89.741 IDs únicos; 30 consultas top 10 | Similitud de contenido; no hay interacciones para medir satisfacción |
| [NetflixRecommender](../Analisis/Recommenders/NetflixRecommender/reports/evaluacion/evaluacion.md) | Vecinos TF-IDF y baseline por año | Coincidencia de categorías descriptiva; las categorías también son entradas |
| [MovieLensRecommender](../Analisis/Recommenders/MovieLensRecommender/reports/evaluacion/evaluacion.md) | NDCG@10: 0,0448 modelo / 0,0253 baseline; 469 objetivos positivos | Mejora inicial en una muestra de 800 usuarios; ranking todavía limitado |
| [IMDbSentiment](../Analisis/NLP/IMDbSentiment/reports/evaluacion/evaluacion.md) | F1 macro: 0,8800 modelo / 0,3340 baseline; 24.799 textos de test | Resultado inicial favorable para sentimiento de reseñas en inglés |
| [NetflixGenreClassification](../Analisis/NLP/NetflixGenreClassification/reports/evaluacion/evaluacion.md) | F1 macro: 0,1716; ocho categorías presentes en test con recall cero | Supera un baseline sin detección de categorías, pero requiere mejoras |
| [CustomerSegmentation](../Analisis/Clustering/CustomerSegmentation/reports/evaluacion/evaluacion.md) | k=4; silhouette 0,3329; ARI entre semillas 0,9988 | Grupos estables en esta población; utilidad de negocio por validar |
| [SpotifySegmentation](../Analisis/Clustering/SpotifySegmentation/reports/evaluacion/evaluacion.md) | k=5; silhouette 0,1711; ARI entre semillas 1,0000 | Estabilidad no equivale a buena separación ni a géneros reales |
| [RetailSalesForecasting](../Analisis/Forecasting/RetailSalesForecasting/reports/evaluacion/evaluacion.md) | MAE: 220.296,11 modelo / 59.811,14 baseline en diez semanas | Ridge no supera la referencia simple |
| [NABAnomalyDetection](../Analisis/AnomalyDetection/NABAnomalyDetection/reports/evaluacion/evaluacion.md) | F1 por punto 0,0398; 15 de 567 puntos anómalos detectados y 171 falsas alertas | Detección baja; no implementa la puntuación oficial NAB |

Las métricas proceden de los reportes locales de esta pasada. Pueden cambiar cuando se repitan los experimentos o cambien las fuentes; los reportes de cada proyecto son la evidencia vigente y este documento registra la primera revisión. F1, NDCG, silhouette y MAE no forman una clasificación única de calidad.

## Entorno y controles

Pasaron los siete tests de separación de textos, agrupación de títulos, exclusión de elementos vistos, política de compras y causalidad de rezagos y scores. Se comprobaron estructura y sintaxis de los 63 notebooks nuevos, enlaces locales y ejecución con los archivos reales.

Los nueve maestros registraron un `DeprecationWarning` relacionado con el argumento `kernel_protocol_version` de la especificación del kernel y traitlets. El detalle permanece en sus tablas y JSON de alertas; no se ocultó. También aparecieron mensajes nativos de libzmq durante cambios de kernel en la pasada inicial, sin salidas de error de celda ni interrupción de las secuencias. La compatibilidad del entorno de Jupyter merece revisión; el éxito de los notebooks no certifica ausencia de mensajes externos a Python warnings.

## Próximas iteraciones

La clasificación de Netflix necesita estudiar el desequilibrio por categoría y el criterio de decisión en validación. Pronóstico requiere más cortes temporales y una selección que conserve al baseline como candidato. NAB requiere estudiar el comportamiento por evento y considerar un score menos sensible a adaptarse dentro de una anomalía. Estos son nuevos experimentos: no se ajustarán parámetros usando el test vigente como si aún fuera independiente.

La [guía compartida](proyectos_tematicos.md) y las metodologías de cada proyecto describen los supuestos. La procedencia exacta y las condiciones de publicación de cada descarga local deben completarse antes de distribuir fuentes.

## Ampliación: cuatro proyectos adicionales

Primera revisión de la ampliación: 2026-10-07T16:27:14.452940+00:00 (UTC). Los cuatro ejecutaron 00 y 06, con 01–05 completos, 23 tests aprobados y controles de independencia en copias renombradas. [Registro de verificación](verificacion_nuevos_proyectos.json).

| Proyecto | Resultado inicial | Interpretación |
| --- | --- | --- |
| [IndustrialAnomalyDetection](../Analisis/AnomalyDetection/IndustrialAnomalyDetection/reports/informe_final/informe_final.md) | F1 0.0851; recall 5.88% | Supera F1 del baseline, pero detecta pocos fallos; fuente sintética |
| [RetailKPIAnalysis](../Analisis/BusinessIntelligence/RetailKPIAnalysis/reports/informe_final/informe_final.md) | Neta 9,748,131.07 GBP; ajustes 8.40% | Agregados reconciliados; BI descriptivo, sin medir rentabilidad |
| [DigitsRecognition](../Analisis/ComputerVision/DigitsRecognition/reports/informe_final/informe_final.md) | Accuracy 98.33%; desplazamiento 1 px 31.11% | Buen resultado del benchmark y alta sensibilidad a la perturbación |
| [CallCenterStaffing](../Analisis/Forecasting/CallCenterStaffing/reports/informe_final/informe_final.md) | MAE 1.612 frente a 1.607 baseline | No mejora MAE; agentes de Erlang C son escenarios sujetos a supuestos |

Las alertas del maestro conservan el aviso de compatibilidad de traitlets y la especificación del kernel. Durante algunas ejecuciones aparecieron mensajes nativos de libzmq al cerrar kernels, sin errores de celda ni interrupción de la pasada final. Estos mensajes no son capturados por el registro de warnings de Python. La compatibilidad del entorno merece revisión por separado.

## Causalidad, regresión y optimización — 7 de octubre de 2026

- **TrainingProgramImpact:** diferencia de medias de 1.794,34 USD y efecto ajustado de 1.621,58 USD (IC HC3 95 %: 212,54–3.030,62). Corresponde a asignación en una submuestra experimental histórica; no al efecto de completar capacitación ni a programas actuales.
- **PowerPlantRegression:** MAE de test 2,47 MW frente a 14,81 MW de la referencia; R² 0,963. Intervalos nominales del 90 % con cobertura observada 88,35 %. Calibración separada del test; sin fechas para afirmar capacidad de pronóstico temporal.
- **WorkforceScheduling:** 53 turnos, 424 horas pagadas y coste 5.904 unidades, cubriendo las 140 franjas del escenario sintético. Gap del solver 0; auditoría de cobertura y restricciones aprobada. El baseline deja déficit y no permite afirmar ahorro comparable. Mantener el plan con requisitos +20 % deja 69 franjas insuficientes.

Estos son resultados iniciales; los [informes integrales](informes_integrales.md) contienen la evidencia vigente y sus limitaciones.

## Grafos, supervivencia y decisiones — 8 de octubre de 2026

Los [resultados de la ampliación](ampliacion_analisis_oct08.md) documentan ARI de comunidades, C-index e incertidumbre del retorno de clientes, comparación de horarios y calibración/umbrales de los cuatro churn. Los resultados incluyen empeoramientos de calibración y de coste en test. El total actual es 24 proyectos; las métricas de tareas y poblaciones diferentes no permiten ordenar su calidad.
