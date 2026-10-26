# Evaluación final

Casos de test: **2,000**. El modelo **supera** el baseline en accuracy.

```text
          accuracy  average_precision   roc_auc
baseline    0.7965            0.20350  0.500000
modelo      0.8100            0.48062  0.775208
```

Las métricas describen esta partición. Revisar recall por clase y matriz de confusión en el JSON; no ajustar parámetros ni thresholds con este test. La definición del churn y la disponibilidad temporal de las features deben confirmarse en la fuente.

## Probabilidades y decisiones

Brier sigmoid **0.1350**, menor que sin calibrar **0.1350**. Brier y log loss combinan calibración y discriminación; ECE depende de los bins. Las tablas de fiabilidad incluyen soporte y omiten bins vacíos. Con umbral fijado en validación **0.18**, se priorizan **849 de 2000 casos**: recall **75.68%**, precisión **36.28%**, coste de error **0.518 unidades por caso**. FN=5.0, FP=1.0 son supuestos ilustrativos, no importes reales ni ahorro de retención. Se muestran todas las políticas sin elegir una nueva con test. BankChurn no encontró IDs compartidos entre train y test; esto por sí solo no acredita independencia por persona.
