# Optimización de turnos y cobertura: evaluacion

El plan optimizado supera cobertura y restricciones estructurales en las **140 franjas**. El baseline no cubre toda la demanda; su menor coste, si lo hubiera, no demuestra ahorro comparable. Al mantener los turnos y aumentar los requisitos un 20 % (redondeo al entero superior), **69 franjas** quedan cortas, con **87 agente-intervalos** de déficit. El escenario de estrés no se reoptimiza ni es una garantía probabilística. Son reglas didácticas, no un calendario de una empresa, cumplimiento de legislación laboral ni SLA. No se modelan habilidades, vacaciones ni rotación entre semanas.

## Equilibrio y preferencias

Ambos planes cubren la demanda. El escenario alternativo reduce o intercambia rango de horas y preferencias bajo un tope de coste: rango **40 → 8 horas**, preferencias incumplidas **39 → 18**, coste **6,409.60 unidades** (**+8.56%** respecto al plan de coste mínimo). La función objetivo pondera rango de horas y turnos fuera del inicio preferido; su gap corresponde a esa puntuación, no a minimizar coste. Preferencias y reglas son sintéticas; equilibrar horas es una medida específica y no certifica equidad laboral.

El solver alternativo **alcanzó el límite de tiempo con una solución factible; no se certifica optimalidad**; gap de su objetivo **22.00%**.

