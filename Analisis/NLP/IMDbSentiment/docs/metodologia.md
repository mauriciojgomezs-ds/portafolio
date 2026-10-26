# Metodología: Sentimiento de reseñas de películas

## Pregunta

Clasificar reseñas en inglés como positivas o negativas.

## Preparación y protocolo

Test oficial conservado, deduplicado por texto normalizado. Textos coincidentes con test se retiran de train; se reserva 20 % del train restante para validación estratificada. TF-IDF y regresión logística.

La fuente se conserva intacta. Se registra SHA-256 y los tamaños realmente preparados. La semilla es 42; los límites de muestra y otros parámetros están en `config.json`. Los artefactos de una etapa son leídos por la siguiente con un kernel independiente.

## Interpretación

F1 macro, accuracy y métricas por clase. El test deduplicado puede tener menos filas que el oficial; los conteos quedan en preparación.

Los comentarios de EDA, baseline, modelado y evaluación se producen desde las cifras calculadas. Comparaciones favorables, empates o ausencia de mejora cambian el texto; cifras no disponibles no se presentan como resultados exitosos. Las correlaciones usan cortes descriptivos |r| >= 0,3 (moderada) y >= 0,7 (alta), sin inferir causalidad o significancia.

## Estado y próximos experimentos

Este es un recorrido inicial reproducible. La evidencia vigente se consulta en `reports/`; ejecutar sin errores no valida por sí solo el problema, la procedencia o la calidad del modelo. Mejoras elegidas tras observar test requieren contemplar esa observación en la evaluación posterior. No se ajustan decisiones de modelado con test dentro de este recorrido.

Consulta la [guía de ejecución local](ejecucion.md).
