# Metodología: Recomendación colaborativa de películas

## Pregunta

Ordenar películas para usuarios existentes de una muestra de MovieLens 32M.

## Preparación y protocolo

800 usuarios muestreados con semilla 42. Últimas dos valoraciones por usuario para valid/test; positivos >=4; vecinos de usuarios y baseline de popularidad.

La fuente se conserva intacta. Se registra SHA-256 y los tamaños realmente preparados. La semilla es 42; los límites de muestra y otros parámetros están en `config.json`. Los artefactos de una etapa son leídos por la siguiente con un kernel independiente.

## Interpretación

Hit rate y NDCG@10 sobre un objetivo positivo retenido por usuario. Los objetivos de ítems sin historial cuentan como fallos. Corte por usuario, sin corte global; no evalúa nuevos usuarios.

Los comentarios de EDA, baseline, modelado y evaluación se producen desde las cifras calculadas. Comparaciones favorables, empates o ausencia de mejora cambian el texto; cifras no disponibles no se presentan como resultados exitosos. Las correlaciones usan cortes descriptivos |r| >= 0,3 (moderada) y >= 0,7 (alta), sin inferir causalidad o significancia.

## Estado y próximos experimentos

Este es un recorrido inicial reproducible. La evidencia vigente se consulta en `reports/`; ejecutar sin errores no valida por sí solo el problema, la procedencia o la calidad del modelo. Mejoras elegidas tras observar test requieren contemplar esa observación en la evaluación posterior. No se ajustan decisiones de modelado con test dentro de este recorrido.

Consulta la [guía de ejecución local](ejecucion.md).
