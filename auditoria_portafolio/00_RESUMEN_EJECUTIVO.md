# Auditoría del portafolio — Resumen ejecutivo

Fecha: 2026-10-26
Alcance: todos los `.md` y `.ipynb` del repo (excluyendo `.venv`, `.local`, `.git`, caches, binarios), ~550 archivos, 24 proyectos en `Analisis/`, 5 apps en `IAG/`, docs raíz, `SitioWeb/`, `BusinessIntelligence/`.

Se auditó en 8 grupos paralelos. Cada grupo generó su propia tabla de hallazgos (`ruta | archivo | línea | original | propuesta`) y, cuando el hallazgo era un error real y no ambiguo, se corrigió directamente en disco (es un repo git: usa `git diff` / `git status` para revisar todo antes de confirmar que te gustan los cambios).

## Diagnóstico general

El portafolio está, en general, en muy buen estado: la mayoría de los 24 proyectos de `Analisis/` comparten un framework maduro (notebooks como wrappers finos de `src/<paquete>/*.py`, `random_state` propagado, splits temporales correctos sin fuga de datos, y — el punto que más te importaba — las conclusiones de los `.md`/notebooks ya se generan dinámicamente con f-strings desde los resultados reales, no como texto fijo). La mayoría de los hallazgos fueron de consistencia editorial (tildes, enlaces faltantes, estructura de README distinta entre proyectos hermanos), no de lógica.

Dicho esto, se encontraron y corrigieron **3 bugs reales de código**, no solo de redacción:

1. **Churn (Grupo 2) — bug de copia-pega entre proyectos**: `BankChurn`, `SubscriptionChurn` y `TelecomChurn` mostraban en su sección "Probabilidades y decisiones" una conclusión hardcodeada con el nombre y protocolo temporal de **ActivityChurn**, por código compartido mal parametrizado en `src/*/decisiones.py`. Corregido para generar la nota dinámicamente por proyecto. También había una sección duplicada en los 4 informes integrales (`informe.py`), corregida.
2. **SmartFood (Grupo 1) — muestreo con reemplazo que podía duplicar IDs**: `05_clasificacion_ranking_svm.ipynb` usaba `recipes.sample(5000, random_state=42, replace=True)`, lo que podía romper una búsqueda posterior por clave única. Cambiado a `replace=False`.
3. **DigitsRecognition (Grupo 3) — semilla hardcodeada en vez de leer config**: `analysis.py` tenía `random_state=42` fijo en dos `train_test_split`, en vez de leer `config(project)['seed']` como los otros 3 proyectos de CV/NLP.

## ⚠️ Acción pendiente de tu parte

Varios cambios de código **no se pudieron verificar ejecutando los notebooks**, porque esta sesión de auditoría no tiene los entornos `.venv` de Windows con scikit-learn/lifelines/networkx instalados. Se validó solo la sintaxis (`py_compile`/`ast.parse`) y revisión manual cuidadosa. Antes de confiar en los resultados, re-ejecuta y regenera los reportes de:
- `Analisis/churn/*` (los 4 proyectos) — sincronización manual de `decisiones.md`/`evaluacion.md`/`informe_final.md` tras el fix del bug de copia-pega.
- `Analisis/Regression/PowerPlantRegression` — se agregó cálculo de VIF y diagnóstico de residuos, sin regenerar el JSON/imágenes.
- `Analisis/GraphAnalysis/EmailCommunityAnalysis` — se documentaron métricas, sin regenerar outputs.
- `Analisis/Recommenders/SmartFood` — 6 notebooks editados (validados solo con `nbformat`, no ejecutados).
- `Analisis/ComputerVision/DigitsRecognition` — fix de semilla en `analysis.py`.

## Resultado por grupo

| # | Grupo | Hallazgos | Cambios reales de código | Reporte |
|---|---|---|---|---|
| 1 | Recommenders (MovieLens, Netflix, SmartFood, Spotify) | 17 | Sí (SmartFood: bug de muestreo, código muerto, headers) | `Grupo1_Recommenders.md` |
| 2 | Churn (Activity, Bank, Subscription, Telecom) | 15 | Sí (bug cross-proyecto, sección duplicada) | `Grupo2_Churn.md` |
| 3 | ComputerVision + NLP (Digits, FashionMNIST, IMDb, NetflixGenre) | — | Sí (seed hardcodeada, enlaces README) | `Grupo3_CV_NLP.md` |
| 4 | Clustering + Forecasting (CustomerSeg, SpotifySeg, CallCenter, RetailSales) | — | No (ya cumplía todo; solo hallazgos documentales) | `Grupo4_Clustering_Forecasting.md` |
| 5 | AnomalyDetection + Optimization (Industrial, NAB, WorkforceScheduling) | — | Mínimo (tabla de README añadida) | `Grupo5_Anomaly_Optimization.md` |
| 6 | BI/Survival/Regression/Graph/Causal | — | Sí (VIF, residuos, conclusión de supervivencia condicional, glosario de métricas de grafos) | `Grupo6_BI_Survival_Regression_Graph_Causal.md` |
| 7 | Docs raíz, SitioWeb, BusinessIntelligence top | 3 | No (índice del portafolio ya coincide 100% con lo que existe en disco) | `Grupo7_Docs_Sitio_BI.md` |
| 8 | IAG (5 apps) | 5 | Mínimo (título de PortfolioDemo) | `Grupo8_IAG.md` |

## Actualización (tras re-ejecutar churn y resolver pendientes)

- **Churn re-ejecutado y verificado**: los 4 proyectos (`Analisis/churn/*`) se re-ejecutaron en tu máquina. Confirmé que el fix del bug de copia-pega funciona: `ActivityChurn`, `BankChurn` y `SubscriptionChurn` ahora muestran su propia conclusión en `reports/evaluacion/decisiones.md` (ya no aparece "ActivityChurn" en los otros 3), `TelecomChurn` mantiene correctamente su rama sin ID de cliente, y `informe_final.md` ya no tiene la sección "Probabilidades y decisiones" duplicada en ninguno de los 4. Sin alertas/errores en los reportes de `reports/alertas/*.json`.
- **`TelecomChurn` unificado**: renombré los encabezados de su `README.md` ("Datos disponibles"→"Datos y particiones", "Ejecución"→"Reproducción", "Próximas mejoras"→"Siguiente revisión") para igualar el patrón de los otros 3 proyectos de churn, y reescribí `docs/metodologia.md` con el mismo formato ("# Metodología: Telecomunicaciones" + una sola sección "## Primera ejecución completa"), conservando todo el contenido factual.
- **Terminología de IAG resuelta**: en `MeetingCopilot/README.md` cambié "Resultado del caso sintético" → "Resultado de demostración", para que los 3 asistentes llamen igual al mismo artefacto (`reports/demo.md`). En `IAG/README.md` aclaré la frase del "Laboratorio de copilotos" para que mencione explícitamente que agrupa a DataCopilot, DocumentAnalyzer (como copiloto documental) y MeetingCopilot, resolviendo la ambigüedad de por qué DocumentAnalyzer está ahí sin tener "Copilot" en su nombre.

## Segunda actualización (re-ejecuciones de Regression/Graph/SmartFood + limpieza + CallCenterStaffing)

- **`PowerPlantRegression` re-ejecutado y verificado ✅**: el pipeline completo (00–06) corrió sin errores de lógica (solo un `DeprecationWarning` de `traitlets`, ajeno al código). El VIF y el diagnóstico de residuos agregados en la auditoría ya se calculan y reportan correctamente: `reports/eda/vif.csv` (VIF máximo 6,07 en AT, nivel moderado) y el nuevo texto en `evaluacion.md` ("correlación residuo absoluto–predicción 0.035, sin señal clara de heterocedasticidad; sesgo -0.228"), ambos generados dinámicamente desde los resultados reales.
- **`EmailCommunityAnalysis` revisado**: no requería re-ejecución (el cambio del Grupo 6 fue solo documental: el glosario de métricas en `docs/metodologia.md`). El contenido quedó claro y correcto (definiciones y rangos de densidad, reciprocidad, PageRank, modularidad, ARI y NMI).
- **`SmartFood` re-ejecutado y verificado ✅**: segunda pasada completa, 01–05 corrieron sin errores (22 s→ahora ~2 min por volumen real de datos: 522.517 recetas, 1.401.982 reseñas) y sin alertas nuevas. Confirmé el fix del muestreo: `data/output/recomendaciones_svm.csv` no tiene ninguna fila duplicada por `usuario+receta_id` (antes podía duplicarse por el `replace=True`). `informe_final.md` y los reportes de cada etapa se regeneraron con fecha de hoy.
- **Carpeta huérfana eliminada**: confirmado que `Recommenders/` (fuera de `Analisis/`) ya no existe en el repo.
- **`CallCenterStaffing` homologado**: se crearon `docs/ejecucion.md` (guía de ejecución local, igual que sus hermanos NAB/RetailSalesForecasting) y `docs/ejecuciones.md` (registro real de la pasada del 7 de octubre de 2026: 00 a las 13:24:57 America/Santiago, 01–05 completados en 22,07 s, MAE 1,612 vs. baseline 1,607, Erlang C hasta 3-5 agentes/intervalo), y se enlazaron ambos desde `README.md` y `docs/estructura.md`.

Ver cada `GrupoN_*.md` en esta misma carpeta para el detalle completo fila por fila (ruta | archivo | línea | original | propuesta).
