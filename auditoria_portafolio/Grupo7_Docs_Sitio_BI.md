# Auditoría Grupo 7 — Documentación raíz, docs/, BusinessIntelligence, SitioWeb y back/IMDb

## Resumen

Se revisaron 20 archivos `.md`: `README.md` raíz, `Analisis/README.md`, los 8 archivos de `docs/`, `BusinessIntelligence/README.md`, `BusinessIntelligence/SalesAccess/README.md` y `SalesAccess/docs/manual_dashboard_salesaccess.md`, `SitioWeb/README.md` y 2 archivos de `SitioWeb/docs/` (`diseno.md`, `perfil_profesional.md`), y `back/IMDb/README_fuente.md`.

**Hallazgo principal: el "índice" del portafolio (`README.md` y `Analisis/README.md`) es coherente con la estructura real en disco.** Se verificó con `find`/`ls` cada uno de los 24 proyectos y los 13 temas de `Analisis/` (AnomalyDetection ×2, BusinessIntelligence ×1, CausalInference ×1, Clustering ×2, ComputerVision ×2, Forecasting ×2, GraphAnalysis ×1, NLP ×2, Optimization ×1, Recommenders ×4, Regression ×1, SurvivalAnalysis ×1, churn ×4 = 24), y los 5 proyectos de `IAG/` (knowledge_base_mvp, MeetingCopilot, DataCopilot, DocumentAnalyzer, PortfolioDemo): todos están mencionados con el nombre y la ruta correctos. No falta ningún subproyecto y no hay ninguno mencionado que no exista.

Se comprobó la existencia real de **todos los enlaces internos** citados en los 20 archivos (READMEs de tema, READMEs de proyecto, `reports/informe_final/informe_final.md` de los 24 proyectos, JSON de verificación, `docs/*.md`, `SitioWeb/docs/*`, scripts citados): **ningún enlace roto**.

Se verificaron cifras cruzadas entre documentos (reproducibles con los JSON/MD de cada proyecto):
- Conteo de notebooks "168" (README raíz, `Analisis/README.md`, `docs/organizacion_portafolio.md`): coincide exactamente con el conteo real de `*.ipynb` dentro de carpetas `notebooks/` de los 24 proyectos (168), excluyendo `.venv`, checkpoints y copias de fallos en `reports/runs/fallos/` (4 adicionales, correctamente no contadas como notebooks del proyecto).
- Progresión histórica 19→22→24 proyectos y 133→154→168 notebooks entre `organizacion_portafolio.md`, `ampliacion_analisis.md` y `ampliacion_analisis_oct08.md`: consistente.
- `TelecomChurn`: "original detecta 28 de 95" (README raíz) coincide con la matriz de confusión real en `evaluacion_test.json` (TP=28, soporte clase 1=95).
- `PowerPlantRegression`: MAE 2,47 MW y cobertura 88,35% coinciden con `informe_final.md`.
- `IndustrialAnomalyDetection`: recall 5,88% y F1 0,0851 coinciden con `informe_final.md`.
- `FashionMNISTClassification`: accuracy 85,18% coincide con `evaluacion.md`.
- `CustomerReturnSurvival`: C-index 0,562 coincide entre README raíz y `ampliacion_analisis_oct08.md`.
- `SalesAccess`: 40 agentes / 44 cuentas / 55 pruebas consistentes entre `README.md`, `docs/manual_dashboard_salesaccess.md` y el README raíz ("40 agentes").

**Único hallazgo material (no corregido, requiere decisión del usuario):** existe una carpeta huérfana `Recommenders/SmartFood/notebooks` en la **raíz** del portafolio (fuera de `Analisis/`), que parece un resto de la reorganización histórica documentada en `docs/organizacion_portafolio.md` (el proyecto real y activo es `Analisis/Recommenders/SmartFood`). Ningún documento la referencia, por lo que no rompe ningún enlace, pero es ruido en el árbol de carpetas que el README raíz describe como limpio. Se registra sin eliminar la carpeta, por ser una decisión de limpieza de repositorio y no un error de documentación.

No se encontraron: enlaces rotos, nombres de proyectos inexistentes, temas de `Analisis/` faltantes en el índice, duplicación problemática de contenido entre `docs/organizacion_portafolio.md` y `Analisis/README.md` (son complementarios: uno es narrativa histórica de la migración, el otro es índice operativo vigente), ni errores de redacción relevantes en español. `back/IMDb/README_fuente.md` es la ficha original de Hugging Face en inglés (con placeholders "More Information Needed" propios de la plantilla de origen); se mantiene intacta como fuente externa citada, tal como indica `docs/inventario_datasets.md`.

No se aplicaron cambios de código ni de contenido en esta pasada: la revisión confirmó que los 20 documentos del alcance ya son coherentes entre sí y con el estado real del repositorio. El único cambio sugerido (retirar o documentar la carpeta huérfana `Recommenders/SmartFood/notebooks` en la raíz) se deja como decisión pendiente del usuario, no como corrección aplicada.

## Hallazgos (tabla)

| Ruta | Archivo | Línea | Original | Propuesta |
| --- | --- | --- | --- | --- |
| `/` (raíz del portafolio) | `Recommenders/SmartFood/notebooks/` (carpeta) | — | Carpeta `Recommenders/SmartFood/notebooks` existe en la raíz del portafolio, fuera de `Analisis/`, sin README ni mención en ningún documento; el proyecto activo y documentado es `Analisis/Recommenders/SmartFood` | Hallazgo registrado sin corregir: confirmar con el usuario si es un resto de la reorganización (`back/.local/homologacion_20261007/` es el lugar documentado para respaldos) y, de ser así, eliminarla o moverla a `back/`, para que la raíz coincida exactamente con el diagrama de `README.md` ("Organización de carpetas") |
| `docs/inventario_datasets.md` | inventario_datasets.md | 1 | "Revisión del 7 de octubre de 2026" | Fecha histórica correcta (coherente con `ampliacion_analisis.md`, previo a la ampliación del 8 de octubre); no requiere cambio, se registra solo para confirmar que no se confunde con una fecha desactualizada |
| `SitioWeb/README.md` y `docs/sitio_web.md` | README.md / sitio_web.md | 96–97 / 27–28 | Línea en blanco duplicada entre párrafos | Cosmético, no afecta el renderizado de Markdown; no se modificó por no ser un error funcional |

## Verificación de enlaces y rutas (método)

Para cada archivo se extrajeron las rutas y enlaces relativos citados y se comprobó su existencia con `find`/`ls`/tests `-e` directamente sobre `$HOME/mnt/portafolio` (ver comandos ejecutados en la sesión de auditoría). Se comprobaron en particular:
- Los 24 `Analisis/<tema>/<proyecto>/README.md` y sus `reports/informe_final/informe_final.md`.
- Los 13 `Analisis/<tema>/README.md`.
- Los README y docs de `IAG/` (`knowledge_base_mvp`, `MeetingCopilot`, `DataCopilot`, `DocumentAnalyzer`, `PortfolioDemo`, incluidos `docs/portafolio.md` y `docs/demostracion.md`).
- Los 8 archivos de `docs/` y los JSON que enlazan (`ejecuciones_proyectos.json`, `inventario_datasets.json`, `verificacion_*.json`).
- `SitioWeb/docs/*` (`diseno.md`, `perfil_profesional.md`, `verificacion.json`, `portada.jpg`) y los scripts citados (`build_site.py`, `check_site.py`, `serve.py`, `test_site.py`).
- `BusinessIntelligence/SalesAccess/reports/*.json`, `requirements.lock.txt`, `data/agentes_demo.csv` (excluyendo `.venv`, `.local`, `.pytest_cache` según alcance indicado).

No se encontró ninguna ruta o enlace inexistente en los 20 documentos revisados.
