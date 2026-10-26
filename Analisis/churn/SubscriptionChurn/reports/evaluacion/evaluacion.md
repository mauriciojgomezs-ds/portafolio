# Evaluación final

Casos de test: **64,374**. El modelo **supera** el baseline en accuracy.

```text
          accuracy  average_precision   roc_auc
baseline  0.473685           0.473685  0.500000
modelo    0.580995           0.638912  0.688741
```

Las métricas describen esta partición. Revisar recall por clase y matriz de confusión en el JSON; no ajustar parámetros ni thresholds con este test. La definición del churn y la disponibilidad temporal de las features deben confirmarse en la fuente.

## Probabilidades y decisiones

Brier sigmoid **0.3836**, mayor que sin calibrar **0.3748**. Brier y log loss combinan calibración y discriminación; ECE depende de los bins. Las tablas de fiabilidad incluyen soporte y omiten bins vacíos. Con umbral fijado en validación **0.18**, se priorizan **61193 de 64374 casos**: recall **99.85%**, precisión **49.75%**, coste de error **0.481 unidades por caso**. FN=5.0, FP=1.0 son supuestos ilustrativos, no importes reales ni ahorro de retención. Se muestran todas las políticas sin elegir una nueva con test. SubscriptionChurn registra 50320 IDs compartidos entre train y test; la independencia por persona sigue pendiente de confirmar.
