# Metodología: Pronóstico semanal de compras

## Pregunta

Predecir el importe de compras positivas de la próxima semana.

## Preparación y protocolo

Solo semanas lunes-domingo completas en el rango observado. Rezagos 1–4 y media desplazada; split temporal 60/20/20 de semanas con features; Ridge y baseline de última semana.

La fuente se conserva intacta. Se registra SHA-256 y los tamaños realmente preparados. La semilla es 42; los límites de muestra y otros parámetros están en `config.json`. Los artefactos de una etapa son leídos por la siguiente con un kernel independiente.

## Interpretación

MAE y RMSE a un paso. Cada semana posterior usa observaciones reales previas; no es pronóstico multisemana desde un origen. No mide ventas netas ni beneficios; histórico corto para estacionalidad anual.

Los comentarios de EDA, baseline, modelado y evaluación se producen desde las cifras calculadas. Comparaciones favorables, empates o ausencia de mejora cambian el texto; cifras no disponibles no se presentan como resultados exitosos. Las correlaciones usan cortes descriptivos |r| >= 0,3 (moderada) y >= 0,7 (alta), sin inferir causalidad o significancia.

## Estado y próximos experimentos

Este es un recorrido inicial reproducible. La evidencia vigente se consulta en `reports/`; ejecutar sin errores no valida por sí solo el problema, la procedencia o la calidad del modelo. Mejoras elegidas tras observar test requieren contemplar esa observación en la evaluación posterior. No se ajustan decisiones de modelado con test dentro de este recorrido.

Consulta la [guía de ejecución local](ejecucion.md).
