# Registro de revisión

Este documento explica los cambios de organización y documentación. El estado de los experimentos se registra en [ejecuciones](ejecuciones.md); las limitaciones de los modelos se analizan en [evaluación](evaluacion.md).

## Alcance de la revisión

Se revisaron los seis notebooks, los módulos Python, la documentación técnica, los informes JSON del entorno, los metadatos de los Parquet locales y el contenido de las referencias académicas. Esta revisión no ejecutó nuevos entrenamientos ni modificó los algoritmos.

Los documentos académicos originales se conservaron. El PDF se leyó y se inspeccionaron sus dos páginas. El texto del DOCX se revisó mediante su contenido XML; no pudo verificarse su maquetación porque el renderizador disponible requiere LibreOffice y no lo encontró.

## Organización del proyecto

| Organización anterior | Organización actual | Propósito |
| --- | --- | --- |
| Notebooks en la raíz | `notebooks/` | Concentrar el flujo de trabajo |
| `utils/` | `src/smartfood/` | Instalar y reutilizar el paquete |
| `data/input/` | `data/raw/` | Identificar entradas originales |
| `reportes/` | `reports/` | Guardar diagnósticos, informes y figuras |
| Factores NMF en `data/processed/` | `models/` | Separar datos preparados y artefactos del modelo |
| Referencias en `docs/` | `docs/references/` | Conservar fuentes académicas |
| README original | `docs/archive/README_original.md` | Mantener el contexto histórico |

Se actualizaron imports y rutas durante la reorganización. Las cabeceras identifican el alcance de los experimentos y las celdas iniciales resuelven la raíz del proyecto. El paquete utiliza carga diferida de exports para que importar limpieza no cargue todos los modelos.

## Nombres de notebooks

| Nombre anterior | Nombre actual |
| --- | --- |
| Sin etapa equivalente | [00_configuracion_entorno.ipynb](../notebooks/00_configuracion_entorno.ipynb) |
| `01_carga_y_limpieza.ipynb` | [01_preparacion_datos.ipynb](../notebooks/01_preparacion_datos.ipynb) |
| `02_inspeccion_analisis.ipynb` | [02_analisis_exploratorio.ipynb](../notebooks/02_analisis_exploratorio.ipynb) |
| `03_recomendaciones_base.ipynb` | [03_baseline_perfil_usuario.ipynb](../notebooks/03_baseline_perfil_usuario.ipynb) |
| `04_rs_nmf.ipynb` | [04_filtrado_colaborativo_nmf.ipynb](../notebooks/04_filtrado_colaborativo_nmf.ipynb) |
| `05_rs_svm.ipynb` | [05_clasificacion_ranking_svm.ipynb](../notebooks/05_clasificacion_ranking_svm.ipynb) |

00 comprueba e instala dependencias. El nombre de 05 describe un clasificador y ranking global; no acredita personalización aprendida.

## Cambios de documentación de esta revisión

- Se añadió un [índice](README.md) con rutas de lectura por necesidad.
- Se actualizaron los hechos de ejecución: el último diagnóstico pasa en Python 3.14, mientras los fallos anteriores se conservan como incidencias históricas.
- Se comprobó el diccionario contra los esquemas de raw e intermediate y se documentaron listas, fechas y diferencias de tipos.
- Se distinguieron los artefactos presentes de las salidas guardadas sin una ejecución reciente verificada.
- Se revisó el informe académico y se documentaron discrepancias con el código y los resultados.
- Se priorizó el trabajo pendiente sin atribuir mejoras de desempeño a cambios de estructura.

## Verificaciones y límites

Se comprobaron referencias locales, nombres de notebooks y correspondencia del diccionario con los metadatos. Las comprobaciones anteriores incluyeron sintaxis, conversión CSV a Parquet con datos sintéticos y ejecución del notebook 00; sus resultados se conservan en el registro de ejecución.

No se añadió una licencia ni se inició un repositorio Git. Esta revisión no demuestra una nueva ejecución completa de 01–05 ni resuelve los problemas de evaluación. Los archivos binarios de referencias y la captura de versiones inicial se conservan como fuentes históricas.
