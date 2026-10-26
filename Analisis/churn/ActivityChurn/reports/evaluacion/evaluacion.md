# Evaluación final

Casos de test: **303**. El modelo **supera** el baseline en accuracy.

```text
          accuracy  average_precision   roc_auc
baseline  0.495050           0.504950  0.500000
modelo    0.772277           0.821799  0.837407
```

Las métricas describen esta partición. Revisar recall por clase y matriz de confusión en el JSON; no ajustar parámetros ni thresholds con este test. La definición del churn y la disponibilidad temporal de las features deben confirmarse en la fuente.

## Probabilidades y decisiones

Brier sigmoid **0.1678**, mayor que sin calibrar **0.1643**. Brier y log loss combinan calibración y discriminación; ECE depende de los bins. Las tablas de fiabilidad incluyen soporte y omiten bins vacíos. Con umbral fijado en validación **0.32**, se priorizan **227 de 303 casos**: recall **95.42%**, precisión **64.32%**, coste de error **0.383 unidades por caso**. FN=5.0, FP=1.0 son supuestos ilustrativos, no importes reales ni ahorro de retención. Se muestran todas las políticas sin elegir una nueva con test. ActivityChurn registra 185 IDs compartidos entre train y test; la independencia por persona sigue pendiente de confirmar.
