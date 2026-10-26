# Verificación inicial

00 se ejecutó el 07-10-2026 13:24:57 (America/Santiago). El maestro completó 01–05 entre las 13:25:00 y las 13:25:22, con kernels independientes por etapa.

Duración de 01–05: 22,07 segundos (6,18 + 3,28 + 3,09 + 6,14 + 3,38). Las versiones usadas están en [environment.json](../reports/entorno/environment.json); `pip check` no encontró requisitos rotos. Las cifras y conclusiones vigentes están en la [evaluación](../reports/evaluacion/evaluacion.md).

| Etapa | Duración | Estado |
| --- | ---: | --- |
| 01 · Preparación | 6,18 s | Completado |
| 02 · EDA | 3,28 s | Completado |
| 03 · Baseline | 3,09 s | Completado |
| 04 · Modelado | 6,14 s | Completado |
| 05 · Evaluación | 3,38 s | Completado |

No se encontraron salidas de error en 00–05; el único aviso registrado (`reports/alertas/06_ejecucion_completa.json`) es un `DeprecationWarning` de `traitlets` ajeno al código del proyecto. Una pasada sin errores no acredita por sí sola la calidad del modelo.

## Resultados y límites

La preparación agrega 5.000 registros de Kaggle en 1.800 intervalos de 30 minutos, con partición cronológica 60/20/20 por días. El AHT se estima únicamente en train: 256,8 segundos de conversación atendida más 30 segundos supuestos de trabajo posterior.

En los 360 intervalos de test, el modelo obtiene MAE 1,612 frente a 1,607 del baseline: **no mejora** ese error. Erlang C estima hasta 3 agentes programables por intervalo (5 bajo +20 % de volumen); el 12,22 % de los intervalos queda bajo el objetivo teórico al sustituir el volumen estimado por el observado. Esto es un diagnóstico del modelo de colas, no un SLA medido: AHT fijo, horario y shrinkage son supuestos, no se optimizan turnos, descansos ni rutas por habilidad, y Erlang C no incluye abandono aunque el archivo contiene llamadas no atendidas.
