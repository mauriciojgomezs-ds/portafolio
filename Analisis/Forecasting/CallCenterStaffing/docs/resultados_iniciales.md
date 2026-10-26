# Primera ejecución verificada

2026-10-07T16:25:44.878916+00:00 (UTC). Resultados de la fuente y configuración registradas en [verificacion.json](verificacion.json).

# Demanda y dotación de call center: evaluacion

En **360 intervalos de test**, MAE **1.612**, frente a **1.607** del baseline: el modelo **no mejora** ese error. Erlang C estima hasta **3 agentes programables por intervalo**, y **5** bajo +20 % de volumen. El **12.22%** de intervalos queda bajo el objetivo teórico al sustituir el volumen por el observado. Eso es un diagnóstico del modelo de colas, **no un SLA medido**. AHT fijo, horario y shrinkage son supuestos; no se optimizan turnos, descansos ni rutas por habilidad. Erlang C no incluye abandono, aunque el archivo contiene llamadas no atendidas.


Esta ficha conserva la primera revisión; los resultados vigentes se consultan en el [informe integral](../reports/informe_final/informe_final.md).
