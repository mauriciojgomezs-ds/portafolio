# Estructura local

```text
FashionMNISTClassification/
├── config.json, pyproject.toml, requirements.txt
├── src/fashion_mnist_classification/
├── scripts/
├── tests/
├── notebooks/00–06
├── data/raw, intermediate, processed, output
├── models/
├── reports/
│   ├── entorno/
│   ├── preparacion/
│   ├── eda/
│   ├── baseline/
│   ├── modelado/
│   ├── evaluacion/
│   ├── alertas/
│   ├── ejecucion/
│   └── informe_final/
└── docs/
```

EDA guarda ejemplos y promedios por clase. Evaluación guarda métricas, predicciones de test, matriz y errores visuales. El [informe integral](../reports/informe_final/informe_final.md) reúne etapas y evidencia, con un [JSON de trazabilidad](../reports/informe_final/informe_final.json).

Cada carpeta operativa pertenece a este proyecto; no hay imports de otros proyectos. Las entradas, NPZ y modelos están excluidos del versionado, mientras que los reportes vigentes y notebooks guardan evidencia reproducible.
