# Pronóstico de series temporales

[RetailSalesForecasting](RetailSalesForecasting/README.md) predice el importe semanal de compras positivas a un paso. Compara la última semana con Ridge y rezagos, respetando el orden temporal. Excluye semanas incompletas y devoluciones; el objetivo no representa ingresos netos.

La evaluación no simula un pronóstico de varias semanas desde una fecha única. Consulta la [guía compartida](../../docs/proyectos_tematicos.md).

[CallCenterStaffing](CallCenterStaffing/README.md) usa llamadas de un dataset público de Kaggle para pronosticar volumen por media hora y calcular escenarios de agentes mediante Erlang C. Incluye baseline de calendario, split cronológico, AHT estimado en train y escenario de +20 % de demanda. La procedencia operativa y cobertura del archivo no están acreditadas; horario, servicio objetivo y disponibilidad son supuestos configurables.
