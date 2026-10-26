# Metodología y límites

Cuenta llamadas ofrecidas, atendidas o no, en intervalos de 30 minutos. Asume cobertura de todos los días 09:00–19:00; rellena con cero los intervalos vacíos. Horario y cobertura son supuestos que deben verificarse con datos operativos. No se interpreta ausencia de registros como cierre. La zona horaria no está declarada por la fuente.

Divide días cronológicamente 60/20/20. Baseline: promedio de train por día de semana y franja. Modelo: HistGradientBoosting con pérdida Poisson y atributos de calendario conocidos a futuro; hojas elegidas por MAE de validación. La evaluación usa un origen fijo y no actualiza el modelo con volúmenes observados de validación/test. Estima AHT con conversación de llamadas atendidas de train más 30 segundos supuestos de trabajo posterior; no usa duraciones futuras.

Erlang C calcula agentes netos por intervalo para 80 % de llamadas en 20 segundos, ocupación máxima de 85 % y 30 % de shrinkage (tiempo no disponible). Los parámetros están en config.json. También genera un escenario con +20 % de volumen, que no constituye un intervalo de confianza. La dotación programable es ceil(netos / (1 − shrinkage)); no diseña turnos ni descansos. El volumen observado permite un diagnóstico teórico del servicio, no medir el SLA real.

El modelo de colas asume llegadas Poisson, tiempos exponenciales, agentes homogéneos, régimen estacionario y ausencia de abandono; esas condiciones no están comprobadas. El archivo incluye llamadas no atendidas, pero no permite identificar abandono frente a otras causas. No se segmenta por habilidades. Con carga baja, el redondeo a agentes enteros influye mucho. [Referencia de colas de W. Whitt](https://www.columbia.edu/~ww2040/tutorial.pdf).
