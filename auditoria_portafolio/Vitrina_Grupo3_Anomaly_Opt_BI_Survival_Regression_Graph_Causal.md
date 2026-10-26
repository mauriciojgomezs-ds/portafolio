# Vitrina — Grupo 3: Anomaly, Optimization, BI, Survival, Regression, Graph, Causal

## Resumen

Se mejoró la presentación visual del `README.md` principal de los 8 proyectos listados, sin alterar cifras, afirmaciones ni contenido textual existente. En cada proyecto se agregó:

1. Una línea de **badges** (shields.io) justo debajo del título (`# Nombre`), con un **solo salto de línea** (sin línea en blanco) para que título + badges formen un único párrafo markdown. Esto es crítico porque `src/<paquete>/informe.py` extrae el "objetivo" del proyecto tomando el primer párrafo (separado por doble salto de línea) que no empiece con `#`, `|`, ``` ``` ``` ni `**`; si los badges quedaran como párrafo independiente, serían tomados erróneamente como el objetivo.
2. Una **imagen incrustada** (`![alt](reports/eda/eda.png)`) con una descripción breve en español, en un punto razonable del README (tras la tabla de notebooks/etapas), para los 8 proyectos — los 8 cuentan con un PNG real en `reports/eda/eda.png`. (RetailKPIAnalysis también tiene un `dashboard.html`, pero además tiene un PNG real de EDA, por lo que también se incrustó.)
3. Ninguno de los 8 README superó ~60 líneas con 5+ encabezados `##` simultáneamente (todos quedaron entre 38 y 56 líneas tras los cambios), por lo que **no se agregó tabla de contenidos** en ningún caso, conforme a la regla del encargo.

**Verificación de la regla de seguridad (párrafo "objetivo"):** para cada uno de los 8 proyectos se ejecutó una simulación exacta de la lógica de `informe.py` (`split('\n\n')[1:]`, tomar el primer fragmento que no empiece con `#`, `|`, ``` ``` ``` o `**`) contra el README ya modificado. En los 8 casos el resultado fue el párrafo descriptivo original del proyecto (ej. "Detectar observaciones de sensores...", "Asignar turnos y pausas...", "Estimar el efecto de la asignación..."), **nunca** la línea de badges. Confirmado programáticamente, no solo por inspección visual.

No se modificó ningún número, afirmación, limitación o enlace existente. No se tocó ningún otro archivo del repositorio (notebooks, scripts, docs, reports).

| Ruta | Archivo | Línea | Original | Propuesta |
| --- | --- | --- | --- | --- |
| Analisis/AnomalyDetection/IndustrialAnomalyDetection | README.md | 2 (nueva) | *(no existía)* | `![Python](https://img.shields.io/badge/python-3.10%2B-blue) ![scikit--learn](https://img.shields.io/badge/scikit--learn-1.3%2B-orange) ![estado](https://img.shields.io/badge/estado-completado-brightgreen)` |
| Analisis/AnomalyDetection/IndustrialAnomalyDetection | README.md | tras tabla de notebooks (nueva) | *(no existía)* | `![Distribución de variables de sensores y alertas detectadas en el EDA](reports/eda/eda.png)` |
| Analisis/AnomalyDetection/NABAnomalyDetection | README.md | 2 (nueva) | *(no existía)* | `![Python](https://img.shields.io/badge/python-3.10%2B-blue) ![scikit--learn](https://img.shields.io/badge/scikit--learn-1.3%2B-orange) ![estado](https://img.shields.io/badge/estado-completado-brightgreen)` |
| Analisis/AnomalyDetection/NABAnomalyDetection | README.md | tras tabla de notebooks (nueva) | *(no existía)* | `![Serie de temperatura con umbral de alerta y tramo de validación](reports/eda/eda.png)` |
| Analisis/Optimization/WorkforceScheduling | README.md | 2 (nueva) | *(no existía)* | `![Python](https://img.shields.io/badge/python-3.10%2B-blue) ![scipy](https://img.shields.io/badge/scipy-1.10%2B-orange) ![estado](https://img.shields.io/badge/estado-completado-brightgreen)` |
| Analisis/Optimization/WorkforceScheduling | README.md | tras tabla de notebooks (nueva) | *(no existía)* | `![Distribución de demanda y disponibilidad analizada en el EDA](reports/eda/eda.png)` |
| Analisis/BusinessIntelligence/RetailKPIAnalysis | README.md | 2 (nueva) | *(no existía)* | `![Python](https://img.shields.io/badge/python-3.10%2B-blue) ![scikit--learn](https://img.shields.io/badge/scikit--learn-1.3%2B-orange) ![estado](https://img.shields.io/badge/estado-completado-brightgreen)` |
| Analisis/BusinessIntelligence/RetailKPIAnalysis | README.md | tras tabla de notebooks (nueva) | *(no existía)* | `![Distribución de importes y ajustes analizados en el EDA](reports/eda/eda.png)` |
| Analisis/SurvivalAnalysis/CustomerReturnSurvival | README.md | 2 (nueva) | *(no existía)* | `![Python](https://img.shields.io/badge/python-3.11%2B-blue) ![lifelines](https://img.shields.io/badge/lifelines-0.30%2B-orange) ![estado](https://img.shields.io/badge/estado-completado-brightgreen)` |
| Analisis/SurvivalAnalysis/CustomerReturnSurvival | README.md | tras tabla de etapas (nueva) | *(no existía)* | `![Curvas de supervivencia y distribución del tiempo hasta la segunda compra](reports/eda/eda.png)` |
| Analisis/Regression/PowerPlantRegression | README.md | 2 (nueva) | *(no existía)* | `![Python](https://img.shields.io/badge/python-3.10%2B-blue) ![scikit--learn](https://img.shields.io/badge/scikit--learn-1.3%2B-orange) ![estado](https://img.shields.io/badge/estado-completado-brightgreen)` |
| Analisis/Regression/PowerPlantRegression | README.md | tras tabla de notebooks (nueva) | *(no existía)* | `![Distribuciones de condiciones de planta analizadas en el EDA](reports/eda/eda.png)` |
| Analisis/GraphAnalysis/EmailCommunityAnalysis | README.md | 2 (nueva) | *(no existía)* | `![Python](https://img.shields.io/badge/python-3.11%2B-blue) ![networkx](https://img.shields.io/badge/networkx-3.2%2B-orange) ![estado](https://img.shields.io/badge/estado-completado-brightgreen)` |
| Analisis/GraphAnalysis/EmailCommunityAnalysis | README.md | tras tabla de etapas (nueva) | *(no existía)* | `![Distribución de grados y estructura de la red de comunicación en el EDA](reports/eda/eda.png)` |
| Analisis/CausalInference/TrainingProgramImpact | README.md | 2 (nueva) | *(no existía)* | `![Python](https://img.shields.io/badge/python-3.10%2B-blue) ![scipy](https://img.shields.io/badge/scipy-1.10%2B-orange) ![estado](https://img.shields.io/badge/estado-completado-brightgreen)` |
| Analisis/CausalInference/TrainingProgramImpact | README.md | tras tabla de notebooks (nueva) | *(no existía)* | `![Distribución de ingresos y covariables analizadas en el EDA](reports/eda/eda.png)` |

## Criterio de elección de dependencias para los badges

- **IndustrialAnomalyDetection** / **NABAnomalyDetection** / **PowerPlantRegression** / **RetailKPIAnalysis**: `scikit-learn>=1.3` confirmado por uso real (`sklearn`/`IsolationForest`) en `src/*/analysis.py` o `common.py`.
- **WorkforceScheduling**: se verificó que el proyecto usa `scipy.optimize.milp` (MILP) en `src/workforce_scheduling/analysis.py` y `balance.py`, no scikit-learn ni PuLP/OR-Tools. Badge con `scipy>=1.10`.
- **CustomerReturnSurvival**: `lifelines>=0.30.3` (Kaplan-Meier, Cox), única dependencia de supervivencia del `pyproject.toml`; `requires-python>=3.11`.
- **EmailCommunityAnalysis**: `networkx>=3.2` confirmado por uso real; `requires-python>=3.11`.
- **TrainingProgramImpact**: `scipy.stats` (t de Student) confirmado en `src/training_program_impact/analysis.py`; badge con `scipy>=1.10`.

Todos los proyectos recibieron además `![estado](...-completado-brightgreen)` porque `reports/ejecucion/resumen.json` reporta `"estado": "completado"` en los 8 casos.
