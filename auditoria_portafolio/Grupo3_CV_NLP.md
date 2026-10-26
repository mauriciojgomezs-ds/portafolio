# Auditoría de consistencia — Grupo 3 (Computer Vision y NLP)

Proyectos auditados:
- `Analisis/ComputerVision/DigitsRecognition`
- `Analisis/ComputerVision/FashionMNISTClassification`
- `Analisis/NLP/IMDbSentiment`
- `Analisis/NLP/NetflixGenreClassification`

Archivos revisados: los 4 `README.md`, 28 archivos en `docs/*.md` (más sus JSON de soporte), 28 notebooks (extraídos celda a celda con `nbformat`, sin volcar JSON crudo) y el código real que ejecutan esos notebooks en `src/<paquete>/*.py` (los notebooks son wrappers finos que llaman a `run_stage`/`generar_informe`; la lógica de preparación, modelado y redacción de conclusiones vive en `src`, así que ahí es donde se verificaron semillas, fugas de datos, normalización y texto estático vs. dinámico). Se usó un script de verificación de enlaces Markdown sobre los ~62 `.md` de los 4 proyectos.

## Resumen

El portafolio de estos 4 proyectos está en un estado notablemente maduro:

- **Conclusiones automatizadas**: ya están resueltas como prioridad del usuario. Los 4 paquetes (`digits_recognition`, `fashion_mnist_classification`, `imdb_sentiment`, `netflix_genre_classification`) generan sus comentarios de EDA/baseline/modelado/evaluación con **f-strings que leen las métricas reales** (`accuracy`, `f1_macro`, matriz de confusión, iteraciones, etc.), incluyendo lógica condicional real (p. ej. `relation = 'supera' if delta>0 else 'queda por debajo de' if delta<0 else 'iguala'` en `imdb_sentiment/text.py` y `fashion_mnist_classification/vision.py`). No se encontró texto de conclusión estático que debiera reemplazarse.
- **Semillas/`random_state`**: presentes en todos los `train_test_split`/modelos de los 4 proyectos. Se encontró **una excepción real**: `digits_recognition/analysis.py` usaba `random_state=42` *hardcodeado* dos veces en `prepare()`, en vez de leer `config(project)['seed']` (que también vale 42) como hacen los otros 3 proyectos. Corregido.
- **Rutas hardcodeadas**: no se encontraron en notebooks ni en `src` de estos 4 proyectos (todas usan `Path`/`config(project)` o resolución dinámica del proyecto); las únicas apariciones de rutas estilo `C:\` o `D:\` son texto descriptivo en Markdown (ruta del interprete de Python, carpeta de fuentes), no código.
- **APIs deprecadas**: no se encontraron (`predict_classes`, `plot_confusion_matrix`, `np.float`, etc. ausentes).
- **Fuga de datos / normalización**: verificado manualmente en `data.py`/`text.py`/`vision.py`/`analysis.py`: `StandardScaler`/TF-IDF/escalas se ajustan solo con train; deduplicación por contenido retira coincidencias con test antes de entrenar; test se mantiene íntegro.
- **Terminología "accuracy" vs "exactitud"**: no hay mezcla; los 4 proyectos usan consistentemente "accuracy" en inglés. Hallazgo del enunciado no confirmado en este grupo.
- **Enlaces rotos en Markdown**: ninguno (0 de ~62 archivos, incluyendo notebooks, README, docs y reports).
- **Inconsistencia real de documentación**: `DigitsRecognition` usa una generación de documentación más antigua/liviana que los otros 3 (sin `docs/README.md` índice, sin `docs/ejecucion.md`/`ejecuciones.md`, con `docs/resultados_iniciales.md` en su lugar) y su `README.md` no enlazaba `docs/estructura.md` ni `docs/resultados_iniciales.md` aunque ambos archivos existen. Corregido añadiendo los enlaces. `IMDbSentiment/docs/README_fuente.md` (ficha HuggingFace en inglés, descargada automáticamente) no estaba referenciada desde ningún doc; se añadió una línea de contexto en `docs/fuentes.md`.
- **Divergencia de arquitectura** (solo reportada, no corregida por riesgo/beneficio): `DigitsRecognition` concentra toda la lógica en `analysis.py` + `execution.py`, mientras los otros 3 proyectos separan `data.py` + `flow.py`/`vision.py`/`text.py`/`explore.py`/`presentation.py`. Renombrar implicaría tocar `scripts/`, `tests/` e `informe.py` sin beneficio funcional, así que se deja documentado como deuda técnica, no como corrección forzada.

**Totales**: 1 notebook-relevante corregido a nivel de código (vía `src`, que es lo que ejecutan los notebooks), 2 archivos Markdown corregidos, 0 enlaces rotos, 0 APIs deprecadas, 0 fugas de datos detectadas, 0 mezclas de terminología.

## Cambios de código/automatización aplicados en notebooks

Los notebooks de estos 4 proyectos no contienen lógica de modelado inline (son wrappers que llaman a `run_stage(project, etapa)` del paquete `src/<paquete>`); por eso la corrección de la semilla faltante se aplicó en el módulo que el notebook `04_modelado`/`01_preparacion_datos` ejecuta realmente:

- **`Analisis/ComputerVision/DigitsRecognition/src/digits_recognition/analysis.py`**, función `prepare()` (la que ejecuta el notebook `01_preparacion_datos.ipynb`, celda 2, vía `run_stage(PROJECT_ROOT, "preparacion")`): se sustituyó `random_state=42` hardcodeado en los dos `train_test_split` por `seed = config(project)['seed']` y `random_state=seed`, alineándolo con `fashion_mnist_classification/data.py`, `imdb_sentiment/data.py` y `netflix_genre_classification/data.py`, que ya leían la semilla desde `config.json`. El valor numérico no cambia (`config.json` también define `"seed": 42`), pero ahora el split respeta la configuración declarada en vez de duplicarla en el código, evitando que una futura reproducción con otra semilla quede inconsistente con lo documentado.

El resto de lo pedido por el usuario (reemplazar conclusiones estáticas por f-strings calculadas, validar shapes/vocabulario/normalización, evitar fuga de datos, usar semillas) ya estaba implementado correctamente en el código que los notebooks invocan; se verificó explícitamente en `digits_recognition/analysis.py`, `fashion_mnist_classification/{data,vision}.py` e `imdb_sentiment/netflix_genre_classification` `{data,text}.py`, sin necesidad de refactor adicional.

## Tabla de hallazgos

| Ruta | Archivo | Línea/Celda | Original | Propuesta |
| --- | --- | --- | --- | --- |
| Analisis/ComputerVision/DigitsRecognition/src/digits_recognition | analysis.py | líneas 34–35 (ejecutadas por notebook `01_preparacion_datos.ipynb`, celda 2) | `train,hold=train_test_split(ids,...,random_state=42)` / `valid,test=train_test_split(hold,...,random_state=42)` | `seed=config(project)['seed']` y usar `random_state=seed` en ambas llamadas, igual que en los otros 3 proyectos. **Aplicado.** |
| Analisis/ComputerVision/DigitsRecognition | README.md | sección "Resultados y documentación" | No enlazaba `docs/estructura.md` ni `docs/resultados_iniciales.md` (sí existentes) | Se agregaron ambos enlaces, igual que hacen los README de FashionMNIST/IMDb/Netflix con `docs/estructura.md`. **Aplicado.** |
| Analisis/NLP/IMDbSentiment/docs | fuentes.md | párrafo de huellas SHA-256 | No mencionaba `docs/README_fuente.md` (archivo huérfano, sin referencias) | Se agregó una frase indicando que es la ficha original de HuggingFace descargada por el notebook de entorno, en inglés, no una metodología propia. **Aplicado.** |
| Analisis/ComputerVision/DigitsRecognition vs. Fashion/IMDb/Netflix | `src/<paquete>/` (estructura de módulos) | n/a | `digits_recognition` usa `analysis.py`+`execution.py`; los otros 3 separan `data.py`+`flow.py`/`vision.py`/`text.py`/`explore.py`/`presentation.py` | Documentado como deuda técnica de arquitectura; no se renombra para no romper `scripts/`, `tests/` e `informe.py` sin beneficio funcional. **No aplicado** (solo reportado). |
| Los 4 proyectos | README / docs / reports | n/a | — | Verificado: cifras citadas en README (p. ej. accuracy 85.18 %/81.01 % en FashionMNIST, 98.33 %/31.11 % en Digits) coinciden exactamente con `reports/evaluacion/evaluacion.json` vigente. Sin corrección necesaria. |
| Los 4 proyectos | notebooks + docs + reports (~62 .md) | n/a | — | Verificado con script de enlaces relativos: 0 enlaces rotos. Sin corrección necesaria. |
| Los 4 proyectos | `src/<paquete>/{data,text,vision,analysis}.py` | n/a | — | Verificado: sin APIs deprecadas, sin `random_state` faltante (tras la corrección anterior), TF-IDF/StandardScaler ajustados solo en train, deduplicación retira solapamiento con test antes de entrenar. Sin corrección necesaria. |
