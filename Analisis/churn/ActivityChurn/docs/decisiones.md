# Calibración y umbrales de decisión

04 conserva la comparación original y ajusta un **modelo adicional** para decisiones: reserva calibración dentro de train, entrena candidatos solo en el resto y selecciona por AP de validación. Calibración sigmoid está fijada; utiliza `CalibratedClassifierCV(FrozenEstimator(...))`, con scikit-learn >=1.6. El estimador congelado no vuelve a entrenarse con calibración.

Con ID, ajuste y calibración se separan por cliente; sin ID se estratifican filas y no se acredita independencia por persona. En el proyecto temporal se reserva la última fecha de train para calibración y se ajusta solo con fechas anteriores; los clientes pueden reaparecer entre periodos, como en el protocolo original. Las limitaciones de definición temporal del target y disponibilidad de variables siguen vigentes.

Validación selecciona candidato y umbral, por lo que su rendimiento es optimista. El umbral usa una grilla de 0 a 1 en pasos de 0,01 y un valor superior a 1 para priorizar a nadie; los empates prefieren menos casos priorizados. Coste = FN × 5 + FP × 1 por defecto, configurable en `decision_costs`. Son penalizaciones ilustrativas de errores de clasificación; no son costes reales de campaña, eficacia de una intervención ni ahorro comercial.

05 evalúa sin modificar decisiones: probabilidades sin calibrar y sigmoid (Brier, log loss, ECE de 10 bins), y políticas sin calibrar 0,5; sigmoid 0,5; umbral de validación; todos; ninguno. Se muestran todas las políticas de test, sin seleccionar la mejor usando sus resultados. Brier y log loss combinan calibración y discriminación; ECE depende de bins. La fiabilidad informa soporte por bin y omite bins vacíos.

El modelo adicional usa menos filas para ajuste que el original. Su comparación antes/después de calibración mantiene fijo el mismo estimador base; sus cifras no se presentan como un cambio debido únicamente al umbral respecto al modelo original.

## Evidencia

- `reports/modelado/particion_calibracion.csv`: índices de train y rol.
- `reports/modelado/umbrales_validacion.csv`: grilla completa, errores y costes.
- `reports/evaluacion/calibracion_test.csv` y `fiabilidad_bins.csv`: probabilidades y soporte.
- `reports/evaluacion/politicas_test.csv`: políticas fijadas y costes ilustrativos.
- `reports/informe_final/informe_final.md`: reúne la evidencia automáticamente.

Las fuentes y particiones externas originales se conservan. Ejecuta 04 y 05 en orden o las tres celdas de 06 para actualizar todas las etapas. [Referencia de calibración](https://scikit-learn.org/stable/modules/calibration.html).
