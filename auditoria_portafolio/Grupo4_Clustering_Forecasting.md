# Auditoría Grupo 4 — Clustering (CustomerSegmentation, SpotifySegmentation) y Forecasting (CallCenterStaffing, RetailSalesForecasting)

## Resumen

Los cuatro proyectos están construidos sobre un mismo framework interno (`common.py`, `alerts.py`, `execution.py`, `informe.py`, notebooks 00–06 como envoltorios finos que llaman a `run_stage`). La lógica real vive en `src/<paquete>/*.py`, no en el `.ipynb` (las celdas de código solo invocan funciones). Por eso la auditoría de "notebooks" se hizo leyendo ese código, que es el que realmente determina splits, semillas, escalado y conclusiones.

Hallazgo principal: el código ya cumple, de forma consistente en los 4 proyectos, casi todos los puntos críticos pedidos:
- **Semillas**: `seed=42` propagada a `KMeans(random_state=seed)`, `silhouette_score(..., random_state=seed)`, segunda semilla `seed+1` para el ARI de estabilidad, `PCA(random_state=42)`, `Ridge`/`HistGradientBoostingRegressor(random_state=42)`, splits estratificados con `random_state=seed`.
- **Escalado antes de clusterizar**: en `clusters.py` (Customer/Spotify, código idéntico) se ajusta `StandardScaler` y luego `KMeans` sobre los datos transformados; el baseline de cuantiles también se evalúa en el espacio escalado.
- **Split temporal sin fuga**: `RetailSalesForecasting/temporal.py` y `CallCenterStaffing/analysis.py` parten train/valid/test por **orden cronológico** (`iloc`/corte por fecha), nunca con `train_test_split` aleatorio; los rezagos (`lag_1..4`, `media_4`) se calculan con `shift()` antes del split, y el modelo se evalúa desde un origen fijo sin actualizarse con datos de validación/test (look-ahead controlado).
- **Conclusiones automatizadas**: todos los `.md` de `reports/*/*.md` y el informe integral se generan con f-strings que interpolan las métricas reales (silhouette, ARI, MAE/RMSE, % bajo SLA, etc.), no hay texto fijo de conclusiones.
- **Rutas no hardcodeadas**: cada notebook resuelve `PROJECT_ROOT` dinámicamente (`_buscar_proyecto`) y usa rutas relativas al proyecto; no se encontraron rutas absolutas tipo `C:\...` o `D:\...` en el código fuente.

No se encontraron bugs de fuga de datos ni de inicialización no determinista en ninguno de los 4 proyectos.

## Hallazgos (tabla)

| Ruta | Archivo | Línea | Original | Propuesta |
| --- | --- | --- | --- | --- |
| `Forecasting/CallCenterStaffing/docs` | (carpeta) | — | Solo tiene `estructura.md`, `fuentes.md`, `informe_final.md`, `metodologia.md`, `resultados_iniciales.md` | Añadir `ejecucion.md`/`ejecuciones.md` como en `RetailSalesForecasting`, `CustomerSegmentation` y `SpotifySegmentation`, para que las 4 instrucciones de ejecución tengan la misma estructura de documentación (hoy CallCenterStaffing mezcla esas instrucciones dentro del propio `README.md`) |
| `Forecasting/CallCenterStaffing/src/call_center_staffing/analysis.py` | analysis.py | 72–143 | Estilo de una sola línea muy densa (`def regression(y,pred):return {...}`, múltiples statements por línea con `;`) | Reformatear a estilo multilínea estándar (PEP8), igual al usado en `retail_sales_forecasting/temporal.py` y en los paquetes de Clustering, para que el estilo de código sea uniforme entre los proyectos hermanos de Forecasting |
| `Forecasting/RetailSalesForecasting` vs `CallCenterStaffing` | README.md | — | Estructuras de README distintas: Retail usa secciones "Método y alcance / Cómo ejecutar / Evidencia / Estructura local / Independencia / Informe integral"; CallCenter usa "Ejecutar (con tabla de notebooks) / Resultados y documentación / Estructura e independencia" | Unificar el esqueleto de secciones del README entre los dos proyectos de Forecasting (o documentar explícitamente que CallCenterStaffing sigue una plantilla distinta por tener descarga Kaggle automática) |
| `Clustering/*/docs/estructura.md`, `Forecasting/RetailSalesForecasting/docs/estructura.md` | estructura.md | 3 | "Este proyecto utiliza la organización de SmartFood" | Referencia a un proyecto externo ("SmartFood") no documentado dentro del grupo auditado; aclarar en una línea qué es SmartFood o enlazar su definición, para que el lector no se quede sin contexto |
| Todos los `src/<paquete>/{alerts,common,execution,informe}.py` | — | — | Código boilerplate duplicado byte a byte en los 4 proyectos (105/95/98/221 líneas idénticas) | Es duplicación **intencional**: cada proyecto declara explícitamente su independencia ("se puede copiar o renombrar... no utiliza otros proyectos"). No se refactorizó a un paquete común para no romper esa independencia; se deja documentado como decisión de diseño, no como defecto |

## Cambios de código/automatización aplicados en notebooks

No se aplicaron cambios de código en esta pasada: la revisión confirmó que `random_state`/semilla, el orden de escalado-antes-de-clustering, el split cronológico sin fuga de datos (look-ahead) y la generación automática de conclusiones desde métricas reales ya estaban correctamente implementados y eran consistentes entre los proyectos hermanos (Clustering entre sí y Forecasting entre sí). Los únicos cambios recomendados son documentales (tabla de hallazgos arriba): nivelar la carpeta `docs/` y el estilo de código de `CallCenterStaffing` con el resto del grupo. No se modificó código fuente para no introducir riesgo sin una necesidad real detectada (evitando "gold-plating").
