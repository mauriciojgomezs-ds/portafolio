# Informe integral · Recomendación colaborativa de películas

Generado: 2026-10-07T16:39:25.803294+00:00 (UTC).

Estado del informe: **Resultados actualizados por etapas**. Estado del último maestro: **completado**.

Este documento reúne los archivos guardados; no ejecuta modelos ni certifica su utilidad. Las fechas y huellas del manifiesto permiten revisar su procedencia.

Hay archivos de resultados o notebooks actualizados después de la última ejecución completa del maestro. Los resultados corresponden a actualizaciones por etapa; ejecuta 06 para cerrar una nueva pasada completa.

## Objetivo y configuración

Ordenar películas para usuarios existentes de una muestra de MovieLens 32M.

| Indicador | Valor |
| --- | --- |
| title | Recomendación colaborativa de películas |
| kind | collaborative |
| source | data/raw/movieLens.zip |
| seed | 42 |
| top_n | 10 |
| max_users | 800 |
| source_base | project |

## Datos y preparación

Indicadores de [preparacion.json](../../reports/preparacion/preparacion.json):

| Indicador | Valor |
| --- | --- |
| fuente | movieLens.zip |
| semilla | 42 |
| filas_originales_usuarios | 200948 |
| usuarios_muestreados | 800 |
| ratings_muestra | 128845 |
| protocolo | Últimas dos valoraciones por usuario para valid/test; positivos rating >= 4. No es un corte temporal global. |
| filas_preparadas | 87585 |
| particiones / train / filas | 127245 |
| particiones / valid / filas | 800 |
| particiones / test / filas | 800 |

### Recomendación colaborativa de películas: preparacion

Se prepararon **87,585 registros**. La fuente y sus huellas se registran en el JSON. Se persistieron train, validación y test según el protocolo documentado.

[Reporte de la etapa](../../reports/preparacion/preparacion.md).

## Hallazgos exploratorios

Indicadores de [eda.json](../../reports/eda/eda.json):

| Indicador | Valor |
| --- | --- |
| poblacion | train |
| filas | 127245 |
| columnas | 4 |
| nulos / userId | 0 |
| nulos / movieId | 0 |
| nulos / rating | 0 |
| nulos / timestamp | 0 |

### Recomendación colaborativa de películas: eda

El análisis utiliza **127,245 registros de train**, con **0 valores ausentes**. La muestra de usuarios limita el alcance. Las valoraciones posteriores no participan en el ajuste.

[Reporte de la etapa](../../reports/eda/eda.md).

![Figura de eda](../../reports/eda/eda.png)

## Baseline

Indicadores de [baseline.json](../../reports/baseline/baseline.json):

| Indicador | Valor |
| --- | --- |
| usuarios_con_objetivo_positivo | 482 |
| objetivos_sin_historial_item | 10 |
| hit_rate_at_k | 0.060166 |
| ndcg_at_k | 0.0349688 |
| recomendaciones_promedio | 10 |
| cobertura_items_train | 0.0083319 |
| k | 10 |

### Recomendación colaborativa de películas: baseline

El baseline recomienda películas con más valoraciones positivas de train, excluyendo las ya valoradas por cada usuario. La evaluación cuenta un único objetivo positivo retenido por usuario; los objetivos sin historial también cuentan como fallos.

[Reporte de la etapa](../../reports/baseline/baseline.md).

## Modelo y selección

Indicadores de [modelado.json](../../reports/modelado/modelado.json):

| Indicador | Valor |
| --- | --- |
| criterio | ndcg_validacion |
| vecinos_elegidos | 30 |

### Recomendación colaborativa de películas: modelado

Se eligieron **30 vecinos** por NDCG@10 en validación. La similitud usa únicamente valoraciones positivas de train; se excluyen todas las películas ya valoradas en train, incluso las negativas. No se reentrena con validación.

[Reporte de la etapa](../../reports/modelado/modelado.md).

## Evaluación y conclusiones

Indicadores de [evaluacion.json](../../reports/evaluacion/evaluacion.json):

| Indicador | Valor |
| --- | --- |
| baseline / usuarios_con_objetivo_positivo | 469 |
| baseline / objetivos_sin_historial_item | 19 |
| baseline / hit_rate_at_k | 0.0469083 |
| baseline / ndcg_at_k | 0.0252547 |
| baseline / recomendaciones_promedio | 10 |
| baseline / cobertura_items_train | 0.00910496 |
| baseline / k | 10 |
| modelo / usuarios_con_objetivo_positivo | 469 |
| modelo / objetivos_sin_historial_item | 19 |
| modelo / hit_rate_at_k | 0.0852878 |
| modelo / ndcg_at_k | 0.0448476 |
| modelo / recomendaciones_promedio | 10 |
| modelo / cobertura_items_train | 0.0259406 |
| modelo / k | 10 |
| ejemplo / usuario | 983 |

### Recomendación colaborativa de películas: evaluacion

El modelo supera el baseline por NDCG@10: **0.0448** frente a **0.0253**, en **469 objetivos positivos**. Hay **19 objetivos sin historial del ítem** en train.

Se evalúa una muestra de usuarios existentes con un objetivo retenido por usuario; no mide satisfacción real ni usuarios nuevos. Los cortes son temporales por usuario, no un corte global: las interacciones de otros usuarios pueden ser posteriores al objetivo de un usuario. Un top solicitado puede quedar incompleto si no hay suficientes candidatos con señal positiva.

[Reporte de la etapa](../../reports/evaluacion/evaluacion.md).

### Comparación automática

- `hit_rate_at_k`: baseline **0.0469083**, modelo **0.0852878**; el modelo **mejora** este indicador en la evaluación guardada.
- `ndcg_at_k`: baseline **0.0252547**, modelo **0.0448476**; el modelo **mejora** este indicador en la evaluación guardada.

## Alertas y estado de ejecución

| Notebook | Tipos de aviso registrados |
| --- | --- |
| 00_configuracion_entorno | 0 |
| 01_preparacion_datos | 0 |
| 02_analisis_exploratorio | 0 |
| 03_baseline | 0 |
| 04_modelado | 0 |
| 05_evaluacion | 0 |
| 06_ejecucion_completa | 1 |

| Notebook | Tipo | Apariciones | Significado | Acción sugerida |
| --- | --- | --- | --- | --- |
| 06_ejecucion_completa | DeprecationWarning | 5 | Se está utilizando una función o comportamiento en retirada. | Consultar la alternativa indicada antes de actualizar dependencias. |

Una tabla vacía de warnings no demuestra ausencia de errores o validez del modelo. Consulta [alertas](../alertas/) y [resumen del maestro](../ejecucion/resumen.json).

| Notebook | Celdas ejecutadas guardadas | Última ejecución UTC | Errores guardados |
| --- | --- | --- | --- |
| 01_preparacion_datos.ipynb | 0/3 | No disponible | 0 |
| 02_analisis_exploratorio.ipynb | 2/3 | 2026-10-07T14:22:58.132694Z | 0 |
| 03_baseline.ipynb | 0/3 | No disponible | 0 |
| 04_modelado.ipynb | 0/3 | No disponible | 0 |
| 05_evaluacion.ipynb | 2/3 | 2026-10-07T14:23:01.354934Z | 0 |

## Limitaciones y próximos pasos

La muestra y el corte por usuario limitan el alcance. No equivale a una simulación temporal global ni a resultados de una plataforma real.

- Comprobar procedencia, condiciones de uso y disponibilidad temporal de las variables.
- Completar una pasada de 06 y revisar las alertas antes de publicar el informe.
- Definir relevancia y candidatos, y evaluar ranking con usuarios o interacciones independientes.

## Evidencia y reproducción

Desde la carpeta de este proyecto, ejecuta `python scripts/generate_report.py` para reunir los resultados guardados, o 06 para ejecutar los análisis y actualizar el informe.

Consulta el [README](../../README.md), la [guía del informe](../../docs/informe_final.md) y el [manifiesto con datos y huellas](informe_final.json). El informe conserva una versión vigente por proyecto.
