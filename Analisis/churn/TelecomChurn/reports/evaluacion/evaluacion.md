# Evaluación final

Casos de test: **667**. El modelo **supera** el baseline en accuracy.

```text
          accuracy  average_precision   roc_auc
baseline  0.857571           0.142429  0.500000
modelo    0.859070           0.421966  0.811704
```

Las métricas describen esta partición. Revisar recall por clase y matriz de confusión en el JSON; no ajustar parámetros ni thresholds con este test. La definición del churn y la disponibilidad temporal de las features deben confirmarse en la fuente.

## Probabilidades y decisiones

Brier sigmoid **0.1012**, menor que sin calibrar **0.1048**. Brier y log loss combinan calibración y discriminación; ECE depende de los bins. Las tablas de fiabilidad incluyen soporte y omiten bins vacíos. Con umbral fijado en validación **0.17**, se priorizan **186 de 667 casos**: recall **66.32%**, precisión **33.87%**, coste de error **0.424 unidades por caso**. FN=5.0, FP=1.0 son supuestos ilustrativos, no importes reales ni ahorro de retención. Se muestran todas las políticas sin elegir una nueva con test. Sin ID de cliente: no se puede comprobar independencia por persona.
