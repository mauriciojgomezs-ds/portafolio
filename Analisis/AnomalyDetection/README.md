# Detección de anomalías

[NABAnomalyDetection](NABAnomalyDetection/README.md) utiliza una serie de temperatura de máquina con etiquetas de ventanas anómalas. El score móvil consulta solo observaciones anteriores; los umbrales se seleccionan en validación.

Se informan métricas por punto y falsas alertas. Este recorrido inicial no implementa la puntuación oficial NAB ni una evaluación por evento. Consulta la [guía compartida](../../docs/proyectos_tematicos.md).

[IndustrialAnomalyDetection](IndustrialAnomalyDetection/README.md) incorpora anomalías tabulares en sensores del benchmark **sintético AI4I**. Compara z-scores e Isolation Forest, con ajuste en normales de train y umbral seleccionado en validación. Incluye precision, recall, F1 y ranking; no acredita anticipación de averías reales.
