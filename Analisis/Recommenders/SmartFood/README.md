# SmartFood
![Python](https://img.shields.io/badge/python-3.10%2B-blue) ![scikit--learn](https://img.shields.io/badge/scikit--learn-1.3%2B-orange) ![estado](https://img.shields.io/badge/estado-completado-brightgreen)

### De un catálogo de recetas a tres enfoques de recomendación

**Preparación de datos · Análisis exploratorio · Recomendación personalizada · NMF · TF-IDF y SVM**

SmartFood es un proyecto de ciencia de datos que explora cómo recomendar recetas a partir del historial de usuarios y del contenido del catálogo. Compara un baseline interpretable por perfil, un enfoque colaborativo con factores latentes y un clasificador de valoraciones positivas utilizado para ranking.

El valor del proyecto está en recorrer el proceso completo: preparar datos, reconocer sus limitaciones, construir modelos y evaluar críticamente qué permiten afirmar sus resultados.

**Estado:** los notebooks 01–05 completaron una ejecución secuencial el 7 de octubre de 2026. Es un prototipo exploratorio de origen académico, con resultados reproducidos y mejoras de evaluación pendientes. [Ver evidencia de ejecución](reports/ejecucion/resumen.json).

[Recorrido de notebooks](docs/notebooks.md) · [Resultados y evaluación](docs/evaluacion.md) · [Documentación completa](docs/README.md)

**Contenido:** [Pregunta](#la-pregunta-del-proyecto) · [Datos](#datos-y-principales-hallazgos) · [Resultados](#resultados-de-la-ejecución-actual) · [Ejecutar](#ejecutar-el-proyecto) · [Informe integral](#informe-integral)

## La pregunta del proyecto

¿Cómo recomendar recetas que un usuario todavía no ha evaluado, utilizando sus interacciones y atributos como ingredientes, categoría y calorías?

Se exploran tres aproximaciones con alcances distintos:

| Enfoque | Cómo funciona | Qué permite explorar |
| --- | --- | --- |
| **Perfil de usuario** | Calcula la categoría más frecuente y las calorías medias del historial; ordena recetas no vistas por distancia calórica | Personalización mediante reglas fáciles de explicar |
| **NMF y vecinos** | Factoriza la matriz usuario–receta y utiliza similitud entre factores para generar recomendaciones | Patrones colaborativos y representación latente |
| **SVM y ranking** | Combina TF-IDF de ingredientes, calorías, categoría y rating agregado para clasificar `rating >= 4` | Clasificación global y ordenamiento por margen del modelo |

El SVM utiliza atributos de receta; el usuario interviene al excluir recetas vistas. Sus funciones de ranking no demuestran similitud con una receta de referencia ni relevancia frente a una consulta. La similitud de ingredientes tiene una implementación separada con TF-IDF y coseno.

## Datos y principales hallazgos

El dataset está atribuido en la documentación académica a Food.com Recipes and Reviews. La [guía de datos](docs/datos.md) contiene la fuente y los archivos necesarios.

| Medida | Datos iniciales | Subconjunto de modelado |
| --- | ---: | ---: |
| Recetas del catálogo | 522.517 | 190 |
| Reseñas | 1.401.982 | 10.343 |
| Usuarios con interacciones | 271.907 | 617 |
| Esparsidad sobre usuarios y recetas evaluadas | 99,9981 % | 91,1772 % |
| Valoraciones iguales a 5 | 72,19 % | 77,43 % |

El umbral de 270 se aplica antes de intersectar usuarios y recetas. **No garantiza 270 interacciones por entidad en el resultado:** los mínimos finales son uno. La reducción permite prototipar, pero conserva una fracción pequeña del catálogo y no acredita representatividad.

El EDA identifica además 19 pares registrados cuya receta no aparece en el catálogo original; el subconjunto filtrado no presenta ese desajuste. Los [comentarios generados](reports/eda/conclusiones_eda.md) y las [métricas del EDA](reports/eda/metricas_eda.json) detallan las cifras actuales.

![Matriz de correlación del subconjunto de recetas filtrado](reports/eda/recipes_filtrado/recipes_filtrado_correlacion.png)

## Resultados de la ejecución actual

| Experimento | Resultado | Lectura del resultado |
| --- | --- | --- |
| Baseline por perfil | Ejemplo del usuario 198: 5 recetas para un top-5 | Genera recomendaciones explicables; todavía no mide relevancia top-K |
| NMF, 10 componentes | RMSE ≈ 4,1996 sobre 2.035 interacciones ocultas | Menor error del grid evaluado |
| NMF, 70 componentes | RMSE ≈ 4,4884 | Configuración conservada para el entrenamiento; no minimiza el error del grid |
| SVM, 2.065 casos de test | Accuracy ≈ 93,80 %; recall de clase negativa = 0 | Predice siempre positivo e iguala al baseline mayoritario en accuracy |

Estas métricas describen tareas diferentes: **accuracy y RMSE no permiten comparar directamente la calidad de los recomendadores**. Falta evaluar ranking con relevancia y candidatos definidos, comparar con baselines y reservar un test independiente para ajustar los modelos. También debe revisarse la disponibilidad temporal de `aggregatedrating` para evitar fuga de información.

La [evaluación](docs/evaluacion.md) explica el protocolo y sus límites. Completar una ejecución no certifica que todos los diagnósticos hayan pasado: los controles de cardinalidad del EDA aún fallan sobre columnas con listas.

## Qué muestra este proyecto en un portafolio

- Preparación de más de un millón de interacciones y uso de Parquet para organizar las etapas.
- Análisis de calidad, dispersión, sesgo de ratings y coste de cobertura del filtrado.
- Construcción de un baseline, factorización matricial y pipelines con variables numéricas, categóricas y textuales.
- Interpretación crítica: detectar un clasificador que no supera una regla mayoritaria y una selección de componentes que no minimiza el error.
- Reproducción mediante un notebook maestro, comentarios calculados y alertas documentadas.

## Ejecutar el proyecto

Requiere **Python 3.10 o posterior**. La pasada actual se ejecutó con **Python 3.14.4**; los cinco notebooks tardaron aproximadamente **117 segundos** en el equipo utilizado. Ese tiempo no incluye 00 y no es una estimación para otros equipos.

Desde `Analisis/Recommenders/SmartFood`, en PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m ipykernel install --user --name smartfood --display-name "Python (SmartFood)"
.\.venv\Scripts\python.exe -m jupyterlab
```

1. Selecciona **Python (SmartFood)** y ejecuta [00 · Configuración del entorno](notebooks/00_configuracion_entorno.ipynb). Si instala dependencias, reinicia el kernel y repite la comprobación. La pasada reciente de 01–05 no incluye 00; su reporte vigente todavía debe regenerarse.
2. Coloca `recipes.parquet` y `reviews.parquet` en `data/raw/`. Si partes de CSV, consulta [datos y reproducción](docs/datos.md) y ejecuta `scripts/prepare_data.py`.
3. Guarda y cierra los notebooks individuales. Abre [06 · Ejecución completa](notebooks/06_ejecucion_completa.ipynb) con el mismo Python y pulsa **Ejecutar todo**.
4. Revisa el resumen, los diagnósticos y las tablas de alertas. Guarda los notebooks y comprueba los reportes antes de publicar.

El maestro tiene tres celdas de código: configuración, ejecución de 01–05 y resumen. Inicia un kernel independiente por etapa, actualiza las salidas de los notebooks completados y se detiene si una celda falla. El límite inicial es de 900 segundos por celda. También puedes ejecutar 01–05 manualmente en ese orden, cada uno desde un kernel reiniciado.

La preparación y el EDA completos pueden consumir bastante memoria. No se ha medido un requisito mínimo de hardware. Consulta la [guía de entorno](docs/entorno.md) ante problemas de imports o de kernel.

## Comentarios, alertas y reportes

Las cifras del EDA se calculan con los datos de la ejecución. Las interpretaciones cambian ante correlaciones positivas o negativas, variables constantes, pocas recomendaciones, configuraciones de NMF con mayor error o predicciones de una sola clase. Las reglas de correlación son descriptivas y configurables; no implican causalidad ni significancia estadística.

Cada notebook 00–05 incorpora una tabla de warnings con descripción, acción sugerida y detalle original. Los mensajes impresos por los diagnósticos no se capturan automáticamente en esa tabla. En la pasada actual no se registraron warnings, aunque el EDA imprimió controles fallidos de listas.

Los reportes utilizan nombres estables para conservar una versión vigente por etapa:

- `reports/ejecucion/resumen.json`: estado, Python y tiempos de la secuencia.
- `reports/eda/`: métricas y comentarios regenerados.
- `reports/eda/<dataset>/`: inspecciones y figuras.
- `reports/alertas/`: avisos de cada notebook.
- `reports/entorno/`: diagnóstico y versiones exactas de 00, comprobado el 7 de octubre de 2026.

Los reportes vigentes pueden versionarse. Los datos, modelos, exportaciones de recomendaciones, pruebas de ejecución y respaldos locales permanecen excluidos. Consulta la [guía de publicación](docs/publicacion.md).

## Organización

```text
SmartFood/
├── notebooks/             # 00: entorno; 01–05: análisis; 06: maestro
├── src/smartfood/          # Preparación, modelos, anotaciones y alertas
├── scripts/               # Conversión CSV y ejecución secuencial
├── tests/                 # Pruebas de reglas, texto, alertas y orquestación
├── data/
│   ├── raw/               # Entradas originales
│   ├── intermediate/      # Datos normalizados
│   ├── processed/         # Subconjunto para modelado
│   └── output/            # Recomendaciones exportadas
├── models/                # Factores y predicciones de NMF
├── reports/               # Evidencia vigente de cada etapa
├── docs/                  # Guías, evaluación y referencias académicas
├── pyproject.toml         # Paquete y dependencias
└── requirements.txt       # Instalación del proyecto y notebooks
```

## Siguiente iteración

Las prioridades son conservar los mapeos de IDs, resolver los controles de listas y las referencias fuera del catálogo, definir el significado de rating cero y mejorar el protocolo de evaluación. Después se podrán comparar popularidad, medias y los modelos con Precision@K, Recall@K, NDCG@K y cobertura.

El [plan de mejoras](docs/mejoras.md) distingue lo implementado de lo pendiente. El proyecto todavía no dispone de una aplicación desplegada ni de una medición de impacto en usuarios.

## Documentación y referencias

Empieza por el [índice de documentación](docs/README.md). Allí encontrarás el diccionario de datos, la configuración del entorno, la guía de notebooks, el registro de ejecución, la evaluación y el procedimiento de publicación.

Los documentos académicos originales se conservan en `docs/references/` y el README original en `docs/archive/`. Sus resultados históricos se distinguen de esta ejecución. La licencia del código queda pendiente de decisión del autor; las condiciones de distribución de los datos deben revisarse en su fuente.

Los reportes están agrupados por etapa. Consulta su [distribución y archivos vigentes](docs/estructura.md#organización-de-reportes).

## Informe integral

Consulta el [informe integral](reports/informe_final/informe_final.md). Se actualiza con 06 y reúne cifras, conclusiones, limitaciones y próximos pasos. Para regenerarlo con resultados existentes usa `python scripts/generate_report.py`. Consulta la [guía del informe](docs/informe_final.md).
