# Metodología: Anomalías en temperatura de una máquina

## Pregunta

Detectar desviaciones en una serie de temperatura de máquina del benchmark NAB.

## Preparación y protocolo

Serie realKnownCause/machine_temperature_system_failure.csv; split cronológico 60/20/20. Media y escala de 48 observaciones anteriores; umbrales candidatos por cuantiles de train, seleccionados por F1 de validación.

La fuente se conserva intacta. Se registra SHA-256 y los tamaños realmente preparados. La semilla es 42; los límites de muestra y otros parámetros están en `config.json`. Los artefactos de una etapa son leídos por la siguiente con un kernel independiente.

## Interpretación

Precisión, recall, F1 y matriz por punto usando las ventanas oficiales de etiquetas. No es la puntuación oficial NAB ni una evaluación de eventos independientes; una avería puede generar muchos puntos alertados.

Los comentarios de EDA, baseline, modelado y evaluación se producen desde las cifras calculadas. Comparaciones favorables, empates o ausencia de mejora cambian el texto; cifras no disponibles no se presentan como resultados exitosos. Las correlaciones usan cortes descriptivos |r| >= 0,3 (moderada) y >= 0,7 (alta), sin inferir causalidad o significancia.

## Estado y próximos experimentos

Este es un recorrido inicial reproducible. La evidencia vigente se consulta en `reports/`; ejecutar sin errores no valida por sí solo el problema, la procedencia o la calidad del modelo. Mejoras elegidas tras observar test requieren contemplar esa observación en la evaluación posterior. No se ajustan decisiones de modelado con test dentro de este recorrido.

Consulta la [guía de ejecución local](ejecucion.md).
