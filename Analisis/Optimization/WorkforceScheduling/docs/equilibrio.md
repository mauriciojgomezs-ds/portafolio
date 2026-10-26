# Escenario de equilibrio y preferencias

El escenario original minimiza coste. La alternativa conserva cobertura, disponibilidad, un turno diario, 40 horas máximas y cuatro días consecutivos; añade un tope de coste = plan de referencia × 1,10. Ese tope usa el coste factible observado; si el solver original tiene gap positivo no equivale a 10 % respecto a un óptimo exacto.

Objetivo alternativo = rango de horas pagadas entre todos los empleados × `balance_hours_weight` + turnos fuera del inicio preferido × `preference_miss_weight`. Valores predeterminados 1 y 0,25. Son pesos didácticos que expresan un intercambio entre criterios; la puntuación no es dinero. Dos variables continuas delimitan horas mínimas y máximas; la plantilla completa incluye empleados sin turnos. Se verifica el objetivo usando el plan fuera del solver.

`preferences.csv` declara un inicio preferido por empleado. Para el escenario sintético identificado, se genera como índice del empleado módulo 5; no proviene de preferencias observadas. Las fuentes existentes se conservan. Para una aplicación real, aporta preferencias documentadas y reglas compatibles.

04 exporta `models/balanced_plan.csv` y `models/balance.json`, con gap del objetivo alternativo y SHA-256 de preferencias. 05 audita ambos planes y produce `reports/evaluacion/comparacion_equilibrio.csv`, `horas_comparadas.csv` y `equilibrio.png`. Los costes corresponden a turnos pagados incluyendo pausas. El reporte de turnos original continúa referido al escenario de coste mínimo; el calendario alternativo se consulta en `models/balanced_plan.csv`.

No se garantiza equidad en sentido general: se mide rango y dispersión de horas y cumplimiento de un único inicio preferido. No hay preferencias de días, competencias, vacaciones, rotación entre semanas, legislación laboral ni satisfacción medida. El gap alternativo corresponde a la puntuación de equilibrio y preferencias, no a certificar mínimo coste.

El escenario alternativo alcanzó el límite de tiempo en la ejecución inicial, con gap del 22 %; el plan es factible y auditado, con optimalidad no certificada. Los comentarios actuales y la alerta `SolverLimitWarning` se generan según el estado real del solver.
