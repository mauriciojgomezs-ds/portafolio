# Metodología: Segmentación de clientes con RFM

## Pregunta

Describir grupos de clientes a partir de recencia, frecuencia e importe de sus compras.

## Preparación y protocolo

Compras positivas con cliente identificado; excluye cancelaciones, devoluciones, precios no positivos y duplicados exactos. RFM con fecha de referencia derivada del histórico, log1p y estandarización; KMeans k=3/4/5.

La fuente se conserva intacta. Se registra SHA-256 y los tamaños realmente preparados. La semilla es 42; los límites de muestra y otros parámetros están en `config.json`. Los artefactos de una etapa son leídos por la siguiente con un kernel independiente.

## Interpretación

Silhouette, estabilidad entre dos semillas (ARI) y perfiles en unidades originales. Análisis descriptivo, sin validación predictiva ni nombres de negocio inventados.

Los comentarios de EDA, baseline, modelado y evaluación se producen desde las cifras calculadas. Comparaciones favorables, empates o ausencia de mejora cambian el texto; cifras no disponibles no se presentan como resultados exitosos. Las correlaciones usan cortes descriptivos |r| >= 0,3 (moderada) y >= 0,7 (alta), sin inferir causalidad o significancia.

## Estado y próximos experimentos

Este es un recorrido inicial reproducible. La evidencia vigente se consulta en `reports/`; ejecutar sin errores no valida por sí solo el problema, la procedencia o la calidad del modelo. Mejoras elegidas tras observar test requieren contemplar esa observación en la evaluación posterior. No se ajustan decisiones de modelado con test dentro de este recorrido.

Consulta la [guía de ejecución local](ejecucion.md).
