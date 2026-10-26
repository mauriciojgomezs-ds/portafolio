# Metodología: Recomendación de títulos de Netflix

## Pregunta

Encontrar películas y series similares por descripción y metadatos.

## Preparación y protocolo

TF-IDF de descripción, categorías, reparto y director; vecinos por coseno. Baseline por año de estreno.

La fuente se conserva intacta. Se registra SHA-256 y los tamaños realmente preparados. La semilla es 42; los límites de muestra y otros parámetros están en `config.json`. Los artefactos de una etapa son leídos por la siguiente con un kernel independiente.

## Interpretación

Diagnóstico descriptivo del catálogo. La coincidencia de categorías es circular como evidencia de calidad porque esas categorías son entradas.

Los comentarios de EDA, baseline, modelado y evaluación se producen desde las cifras calculadas. Comparaciones favorables, empates o ausencia de mejora cambian el texto; cifras no disponibles no se presentan como resultados exitosos. Las correlaciones usan cortes descriptivos |r| >= 0,3 (moderada) y >= 0,7 (alta), sin inferir causalidad o significancia.

## Estado y próximos experimentos

Este es un recorrido inicial reproducible. La evidencia vigente se consulta en `reports/`; ejecutar sin errores no valida por sí solo el problema, la procedencia o la calidad del modelo. Mejoras elegidas tras observar test requieren contemplar esa observación en la evaluación posterior. No se ajustan decisiones de modelado con test dentro de este recorrido.

Consulta la [guía de ejecución local](ejecucion.md).
