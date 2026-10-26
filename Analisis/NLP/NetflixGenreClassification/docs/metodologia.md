# Metodología: Categorías de películas desde su sinopsis

## Pregunta

Predecir varias categorías de catálogo para una película desde su sinopsis.

## Preparación y protocolo

Solo películas con descripción. Textos deduplicados y particiones 60/20/20 agrupadas por título normalizado. TF-IDF y clasificación multietiqueta; categorías del target fuera de las entradas.

La fuente se conserva intacta. Se registra SHA-256 y los tamaños realmente preparados. La semilla es 42; los límites de muestra y otros parámetros están en `config.json`. Los artefactos de una etapa son leídos por la siguiente con un kernel independiente.

## Interpretación

F1 macro/micro y coincidencia exacta sobre categorías conocidas de train. Las asignaciones de categorías desconocidas se cuentan por separado. No todas las categorías de catálogo son géneros estrictos.

Los comentarios de EDA, baseline, modelado y evaluación se producen desde las cifras calculadas. Comparaciones favorables, empates o ausencia de mejora cambian el texto; cifras no disponibles no se presentan como resultados exitosos. Las correlaciones usan cortes descriptivos |r| >= 0,3 (moderada) y >= 0,7 (alta), sin inferir causalidad o significancia.

## Estado y próximos experimentos

Este es un recorrido inicial reproducible. La evidencia vigente se consulta en `reports/`; ejecutar sin errores no valida por sí solo el problema, la procedencia o la calidad del modelo. Mejoras elegidas tras observar test requieren contemplar esa observación en la evaluación posterior. No se ajustan decisiones de modelado con test dentro de este recorrido.

Consulta la [guía de ejecución local](ejecucion.md).
