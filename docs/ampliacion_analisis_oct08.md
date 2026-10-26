# Grafos, supervivencia y complementos — 8 de octubre de 2026

## Nuevas preguntas

| Proyecto | Pregunta y aporte | Evidencia |
| --- | --- | --- |
| [EmailCommunityAnalysis](../Analisis/GraphAnalysis/EmailCommunityAnalysis/README.md) | Comunidades y centralidad de una red de comunicación; evaluación descriptiva con departamentos y estabilidad | [Informe](../Analisis/GraphAnalysis/EmailCommunityAnalysis/reports/informe_final/informe_final.md) |
| [CustomerReturnSurvival](../Analisis/SurvivalAnalysis/CustomerReturnSurvival/README.md) | Tiempo hasta segunda compra positiva en 90 días, incorporando censura; aporta duración y no define churn | [Informe](../Analisis/SurvivalAnalysis/CustomerReturnSurvival/reports/informe_final/informe_final.md) |

Los proyectos conservan 00–06, paquete local, requisitos, fuentes propias, scripts, tests, alertas tabuladas y comentarios calculados. Stanford proporciona la red; UCI Online Retail aporta las transacciones. Supervivencia usa una copia local del original, sin importar funciones o resultados de retail o clustering.

## Complementos existentes

- [WorkforceScheduling](../Analisis/Optimization/WorkforceScheduling/README.md): compara coste mínimo con equilibrio de horas y preferencias sintéticas bajo un tope de coste. Ambos planes pasan auditoría independiente; los pesos y preferencias no representan acuerdos laborales reales.
- [Churn](../Analisis/churn/README.md): los cuatro proyectos incorporan un modelo adicional con reserva de calibración, sigmoid fijado y umbral elegido por costes ilustrativos en validación. Test informa Brier, log loss, fiabilidad con soporte y políticas sin reajustarlas. La comparación original se conserva y se distingue del modelo adicional.

Se mantiene la autonomía: turnos recibe sus requisitos exógenos y no depende de CallCenterStaffing; supervivencia no depende de RetailKPIAnalysis. Grafos no reutiliza agrupaciones de los proyectos de clustering.

## Resultados iniciales y límites

- Grafos: ARI 0,350 y NMI 0,595 frente a departamentos; ARI medio de estabilidad 0,646 frente a otras semillas. Son diagnósticos en la misma red; no accuracy de nuevos nodos ni productividad.
- Supervivencia: 868 clientes de test, 386 eventos; C-index 0,562 con IC bootstrap 95 % [0,529; 0,594]. Discriminación modesta; no demuestra calibración, predicción temporal ni efecto causal. Hay censura administrativa y una primera compra observada puede ser de un cliente preexistente.
- Turnos: rango de horas 40 → 8; preferencias incumplidas 39 → 18; coste 5.904 → 6.409,60 unidades (+8,56 %). Preferencias sintéticas y función objetivo explícita; equilibrar horas no certifica equidad general.
- Churn: sigmoid tiene Brier menor en BankChurn y TelecomChurn y mayor en SubscriptionChurn y ActivityChurn. En SubscriptionChurn, el umbral elegido en validación presenta coste de test mayor que la política sin calibrar a 0,5; se informa sin seleccionar otra política con test. Las diferencias entre archivos y límites temporales originales siguen abiertos.

## Comprobaciones

Los dos maestros nuevos y el de turnos ejecutaron 00 y 06; los cuatro churn ejecutaron sus secuencias 01–05 por la entrada de terminal. Se comprobaron salidas, sintaxis y 63 tests. Los nuevos proyectos repitieron las cinco etapas desde copias renombradas sin modelos ni datos procesados previos, con evaluación idéntica. Se comprobó el bootstrap desde cinco contextos. Se reutilizaron intérpretes existentes: no es una prueba de instalación limpia. [Registro de comprobaciones](verificacion_analisis_oct08.json).

Los informes vigentes se encuentran en `reports/informe_final/informe_final.md` dentro de cada proyecto; los resultados iniciales de este documento son un registro fechado. La documentación de las líneas IAG y aplicaciones BI sigue su flujo propio.

El escenario alternativo alcanzó el límite de tiempo en la ejecución inicial, con gap del 22 %; el plan es factible y auditado, con optimalidad no certificada. Los comentarios actuales y la alerta `SolverLimitWarning` se generan según el estado real del solver.
