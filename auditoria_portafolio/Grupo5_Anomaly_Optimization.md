# Auditoría Grupo 5 — Detección de anomalías (IndustrialAnomalyDetection, NABAnomalyDetection) y Optimización (WorkforceScheduling)

## Resumen

Los tres proyectos siguen el mismo framework interno visto en auditorías anteriores del portafolio: notebooks 00–06 son envoltorios finos (`_buscar_proyecto` + `run_stage`), y toda la lógica real (splits, semilla, umbrales, modelo MILP, comentarios) vive en `src/<paquete>/*.py`. La auditoría de "notebooks" se hizo por tanto leyendo ese código fuente, que es el que determina resultados y texto.

Hallazgo principal: el código ya cumple, de forma consistente entre los tres proyectos, casi todos los puntos críticos pedidos:

- **Semilla/`random_state`**: `seed=42` en `config.json`, propagada a `train_test_split`, `IsolationForest(random_state=...)` y usada también en `WorkforceScheduling` (aunque el escenario no usa aleatoriedad: su generador es un perfil fijo, documentado así).
- **Umbral justificado, no mágico**: en ambos proyectos de anomalías el umbral se elige entre varios cuantiles de train por **F1 de validación** (`04_modelado` / `train()`), y se reporta el criterio (`criterio: f1_validacion`) y los candidatos evaluados; no hay un número fijo sin explicación.
- **Métricas con ground truth**: se reportan precision/recall/F1/average precision (Industrial) y precision/recall/F1 por punto (NAB) contra las etiquetas reales, en baseline y modelo.
- **Modelo MILP bien planteado** (`WorkforceScheduling/src/workforce_scheduling/analysis.py::solve`): función objetivo clara (coste total pagado), restricciones explícitas de cobertura por franja, disponibilidad, un turno por empleado/día, horas semanales máximas y días consecutivos máximos (ventana móvil). Tras resolver, `audit_plan()` **revalida la factibilidad fuera del solver** y la ejecución falla (`ValueError`) si la solución no supera esa auditoría independiente — exactamente lo pedido.
- **Conclusiones automatizadas**: todos los `.md` de `reports/*/*.md` y el informe integral se generan con f-strings que interpolan las métricas reales (F1, precision, recall, coste, gap del solver, déficit de cobertura, etc.); no hay texto fijo de conclusiones. `docs/resultados_iniciales.md` (Industrial) coincide cifra a cifra con `evaluacion.json`/`informe_final.md`, y `docs/equilibrio.md` (Workforce) coincide con `modelado.json`/`evaluacion.json` (gap 22,00 %, +8,56 % de coste, tope 10 %).
- **Rutas no hardcodeadas**: no se encontraron rutas absolutas (`C:\`, `D:\`, `/home/...`) ni APIs deprecadas (`iteritems`, `applymap`, `.ix`, `np.float`, etc.) en ninguno de los tres paquetes.

No se encontraron fugas de datos, umbrales sin justificar, ni restricciones faltantes en el modelo de optimización.

## Nota metodológica importante (falso positivo corregido)

Durante la auditoría se identificaron, en un primer paso, menciones a "SmartFood" (`NABAnomalyDetection/docs/estructura.md`) y a "CallCenterStaffing" (`WorkforceScheduling/docs/metodologia.md`) que parecían referencias rotas a proyectos inexistentes. Se verificó contra `Analisis/README.md` y el árbol real del portafolio: **ambos son proyectos hermanos reales** (`Analisis/Recommenders/SmartFood` y `Analisis/Forecasting/CallCenterStaffing`), y las frases son correctas ("este proyecto sigue la misma organización que SmartFood", "es independiente de CallCenterStaffing"). Se había aplicado una edición para "corregir" esto y se revirtió de inmediato al confirmar que eran referencias legítimas. Mismo patrón detectado y dejado sin tocar en la auditoría previa del Grupo 4.

## Hallazgos (tabla)

| Ruta | Archivo | Línea | Original | Propuesta |
| --- | --- | --- | --- | --- |
| `AnomalyDetection/NABAnomalyDetection` | `README.md` | sección "Cómo ejecutar" | No tenía tabla de notebooks → función, a diferencia de `IndustrialAnomalyDetection/README.md` que sí la tiene | **Aplicado**: se añadió tabla `Notebook / Función` (01–05) igual en formato a la de Industrial, para que los dos proyectos hermanos de anomalías documenten sus etapas de forma consistente |
| `NABAnomalyDetection/docs/estructura.md` | estructura.md | 3, 24 | Menciona "SmartFood" y `Analisis/churn/src/churn_portfolio` | **No aplicado** (falso positivo): son referencias correctas a proyectos reales del portafolio; se dejó el texto original tal cual, ver nota metodológica arriba |
| `WorkforceScheduling/docs/metodologia.md` | metodologia.md | 3 | Menciona "CallCenterStaffing" | **No aplicado** (falso positivo): `CallCenterStaffing` es un proyecto real de `Forecasting`; se dejó el texto original |
| `NABAnomalyDetection/src/nab_anomaly_detection/{data.py,explore.py,temporal.py}` | — | todo el archivo | `data.py`/`explore.py` implementan ramas para `kind` ajenos a este proyecto (`music_content`, `movie_content`, `cluster_customers`, `collaborative`, `forecast`...), pero `config.json` fija `"kind": "anomaly"` siempre; esas ramas son código muerto dentro de este proyecto concreto | **No aplicado**: es el mismo framework genérico multi-`kind` compartido por los ~24 proyectos del portafolio (igual patrón que `informe.py`, que también tiene ramas para clustering/recomendación/forecast). Eliminar las ramas no usadas reduciría claridad local pero **no se pudo probar** (no hay `.venv`/`sklearn` disponible en esta sesión para ejecutar los notebooks tras el cambio), así que se documenta como recomendación de limpieza futura en vez de aplicarse a ciegas sobre código de producción |
| `IndustrialAnomalyDetection`, `NABAnomalyDetection`, `WorkforceScheduling` | `src/*/{alerts,common,execution,informe}.py` | — | Código boilerplate casi idéntico entre los tres proyectos | Duplicación **intencional** y ya documentada en los README ("se puede copiar o renombrar... no requiere otros proyectos"); no se refactorizó a un paquete común para no romper esa independencia declarada — mismo criterio que la auditoría del Grupo 4 |
| `WorkforceScheduling/reports/runs/fallos/*.ipynb` | — | — | Copias parciales de notebooks de una ejecución fallida anterior | No se modificaron: son evidencia histórica documentada explícitamente en `docs/estructura.md`/`README.md` ("`runs/fallos/`: copias parciales, solo si una ejecución falla"); editarlas falsearía el registro |

## Cambios de código/automatización aplicados en notebooks

No fue necesario modificar la lógica de `src/` de ningún proyecto: `random_state`/semilla, la selección de umbral por F1 de validación (no mágica), el reporte de precision/recall/F1 con ground truth, el planteamiento completo del MILP (objetivo + restricciones) y su auditoría de factibilidad post-solver, y la generación automática de comentarios/conclusiones desde métricas reales ya estaban correctamente implementados y eran consistentes entre `IndustrialAnomalyDetection` y `NABAnomalyDetection` entre sí.

El único cambio aplicado fue documental: se añadió la tabla "Notebook / Función" al `README.md` de `NABAnomalyDetection/` para igualar su estructura a la de `IndustrialAnomalyDetection/README.md` (ambos proyectos de anomalías). No se tocó código fuente de `src/` porque no había forma de verificar en esta sesión (sin `.venv` con `scikit-learn`/`scipy` instalado) que una refactorización de las ramas multi-`kind` no rompiera la ejecución real; se deja como recomendación en la tabla de hallazgos en vez de aplicarse sin poder probarla.
