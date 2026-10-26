# Metodología y límites

La pregunta es qué turnos asignar para cubrir requisitos por franja minimizando coste. Las entradas son demanda **exógena** en agentes y una plantilla ficticia: no se pronostican llamadas ni se ejecuta Erlang C. El proyecto es independiente de CallCenterStaffing y no importa sus resultados o funciones.

El escenario local es sintético: siete días, horario 09–19, veinte franjas de 30 minutos por día, catorce empleados ficticios y costes en unidades monetarias arbitrarias. Un perfil fijo genera demanda de 2–7 agentes, con pico miércoles y menor fin de semana. Cada empleado tiene un día no disponible. La fuente y generador se identifican en data/raw/scenario_origin.json; los CSV pueden reemplazarse juntos por un escenario documentado compatible.

Cada patrón de turno dura 8 horas pagadas e incluye dos pausas de 30 minutos que no aportan cobertura: comida a las 3–4,5 horas desde el inicio y descanso a las 1,5 o 5,5 horas. Los inicios posibles son 09, 09:30, 10, 10:30 y 11. Se paga todo el turno, incluidas pausas. No se aplica además un shrinkage general, que duplicaría esos descansos.

Restricciones: cobertura de cada franja; disponibilidad; máximo un turno por empleado y día; máximo 40 horas semanales; máximo cuatro días consecutivos, verificado con ventanas móviles de cinco días. Hay un único tipo de habilidad. La versión admite turnos de 8 h, franjas de 30 min y diez horas de apertura; cambiar esos parámetros exige adaptar patrones y validaciones.

03 construye una heurística secuencial: selecciona cobertura pendiente por coste respetando restricciones de cada empleado. Puede dejar demanda sin cubrir; su coste solo se compara como alternativa factible cuando cubre todo. 04 utiliza MILP con una variable binaria por empleado, día y patrón elegible. Objetivo: coste total pagado. scipy.optimize.milp devuelve estado, cota inferior y gap. Tolerancia relativa 1 % y límite 60 s configurables. Se admite una solución por límite de tiempo solo si es binaria y supera la auditoría; no se presenta como óptimo exacto.

05 vuelve a verificar todas las restricciones mediante una auditoría independiente del solver, exporta turnos y horas por empleado, y aumenta requisitos un 20 % redondeando arriba, sin reoptimizar. El estrés muestra déficits del plan existente; no es un intervalo probabilístico. No hay splits predictivos ni un SLA medido.

Son reglas didácticas: no garantizan legislación laboral, vacaciones, preferencias reales, contratación real, equidad de asignaciones, continuidad entre semanas ni disponibilidad efectiva. La optimalidad, cuando se certifica, se limita a los patrones y restricciones de este escenario.

## Referencia metodológica

[Documentación de scipy.optimize.milp](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.milp.html).

## Escenario alternativo

La ampliación incorpora equilibrio de horas y preferencias sintéticas bajo tope de coste. Su [protocolo específico](equilibrio.md) explica objetivo, pesos, gap y auditoría; es independiente de minimizar coste.
