# Guía de notebooks

Los nombres describen la tarea de cada etapa. La numeración identifica el flujo de preparación; los enfoques de recomendación se ejecutan por separado una vez generados los datos procesados.

## Recorrido de ejecución

| Notebook | Pregunta que aborda | Entradas | Salidas previstas |
| --- | --- | --- | --- |
| [00_configuracion_entorno.ipynb](../notebooks/00_configuracion_entorno.ipynb) | ¿Está preparado el Python activo para ejecutar el proyecto? | `requirements.txt` y Python del kernel | Instalación si hace falta, diagnóstico JSON y versiones exactas en `reports/entorno/` |
| [01_preparacion_datos.ipynb](../notebooks/01_preparacion_datos.ipynb) | ¿Cómo estandarizar los nombres de columnas y el texto? | `data/raw/recipes.parquet`, `data/raw/reviews.parquet` | Dos Parquet limpios en `data/intermediate/` |
| [02_analisis_exploratorio.ipynb](../notebooks/02_analisis_exploratorio.ipynb) | ¿Qué calidad, sesgos y esparsidad presentan los datos? | Parquet de `data/intermediate/` | Dos Parquet filtrados en `data/processed/`, reportes y figuras en `reports/` |
| [03_baseline_perfil_usuario.ipynb](../notebooks/03_baseline_perfil_usuario.ipynb) | ¿Qué recomendar mediante categoría habitual y cercanía calórica? | Parquet de `data/processed/` | Ejemplo de recomendaciones mostrado en el notebook; sin exportación ni evaluación cuantitativa |
| [04_filtrado_colaborativo_nmf.ipynb](../notebooks/04_filtrado_colaborativo_nmf.ipynb) | ¿Qué patrones latentes y vecinos se obtienen de los ratings? | Parquet de `data/processed/` | Búsqueda de componentes, métricas y ejemplos; factores y predicciones en `models/` |
| [05_clasificacion_ranking_svm.ipynb](../notebooks/05_clasificacion_ranking_svm.ipynb) | ¿Puede un clasificador global distinguir valoraciones positivas? | Parquet de `data/processed/` | Reporte de clasificación, matriz de confusión, rankings y `data/output/recomendaciones_svm.csv` |
| [06_ejecucion_completa.ipynb](../notebooks/06_ejecucion_completa.ipynb) | ¿Cómo ejecutar 01–05 en orden desde un solo notebook? | Entorno preparado con 00 y Parquet raw | Notebooks 01–05 con salidas nuevas, artefactos de cada etapa y `reports/ejecucion/resumen.json` |

## Ejecución desde el maestro

Ejecuta primero 00 en el Python elegido. Guarda y cierra los notebooks 01–05, abre 06 con ese mismo Python y ejecuta sus celdas. El maestro utiliza `scripts/execute_notebooks.py` y nbclient para ejecutar 01–05 secuencialmente, cada uno con un kernel nuevo. No ejecuta 00 ni se llama a sí mismo. El parámetro `TIMEOUT_POR_CELDA` tiene un valor inicial de 900 segundos.

Una etapa satisfactoria actualiza las salidas de su notebook original. Si una celda falla o excede el timeout, la secuencia se detiene y conserva una copia parcial en `reports/runs/fallos/`, excluida del versionado. El resumen en `reports/ejecucion/resumen.json` identifica el Python, los tiempos y el estado; se reemplaza en cada nueva ejecución. Puedes ejecutar la última celda del maestro para consultar el resumen después de un fallo. Los notebooks posteriores al fallo no se ejecutan.

El maestro genera los mismos datos, modelos y reportes que las celdas habituales; no limpia automáticamente `reports/`. No ejecutes otros notebooks simultáneamente sobre esos archivos. Las advertencias o los errores que las funciones capturan e imprimen no detienen necesariamente la secuencia: revisa los diagnósticos y las tablas de alertas antes de publicar. Una interrupción solicitada durante una etapa se registra y se cierra su kernel mediante nbclient; una terminación forzada del proceso puede impedir esa limpieza.

## Cómo comprobar una ejecución

### Presentación de salidas y avisos

Los notebooks 00–05 llaman a `smartfood.entorno_notebook.configurar_notebook()` después de resolver las rutas. Esta base registra los warnings para mostrarlos agrupados en la tabla final, en lugar de repetir los mensajes entre las salidas. No requiere cargar scikit-learn, por lo que también puede usarse en 00 antes de instalar dependencias. Sustituye el filtro general que ocultaba todos los warnings en 02.

La sección final **Alertas de la ejecución** presenta tipo, cantidad de apariciones, significado genérico, acción sugerida y detalle original desplegable con sus ubicaciones. Agrupa por categoría y mensaje exacto; mensajes con valores diferentes pueden ocupar filas diferentes. Incluye explicaciones para convergencia, métricas indefinidas, conversiones de datos, operaciones numéricas y cambios futuros de bibliotecas. Las categorías desconocidas reciben una descripción genérica. Las descripciones no determinan por sí mismas la gravedad del caso.

La tabla exporta `reports/alertas/<nombre_del_notebook>.json`, reemplazando el reporte anterior de ese notebook. El registro comienza vacío cada vez que se llama a la configuración inicial y reúne los avisos emitidos en ese proceso. Si una celda se detiene con un error, ejecuta la celda final de alertas para consultar y guardar lo registrado hasta entonces. `obtener_alertas()` permite consultar los registros sin mostrarlos; `restaurar_avisos()` recupera la presentación previa de warnings.

Se registran todas las apariciones de avisos de usuario, cálculo y deprecación para poder contarlas; otras categorías mantienen sus filtros habituales. Los errores que detienen una celda siguen mostrando su traceback. Los mensajes escritos con `print`, los logs y los avisos de subprocesos (como las comprobaciones de imports de 00) no se capturan en esta tabla. «Sin alertas» solo significa que no se registraron warnings en ese proceso; no certifica una ejecución completa ni que los diagnósticos impresos hayan pasado.

Los reportes de clasificación del notebook 05 y de la exploración de thresholds utilizan `zero_division=0`: cuando no existen predicciones para una clase, su precisión se representa como cero sin emitir `UndefinedMetricWarning`. Es una convención explícita de cálculo, no una corrección del comportamiento del modelo. La matriz de confusión y los comentarios automáticos siguen mostrando si solo se predice una clase.

Las configuraciones `.vscode/settings.json` del portafolio y de SmartFood activan salidas con desplazamiento y una altura de 60 líneas. VS Code usa el límite de líneas como altura al activar `notebook.output.scrolling`; no es un filtro de warnings de Python. La configuración se aplica según cuál de las dos carpetas se abra como proyecto. Si persiste el mensaje de truncado en una salida anterior, vuelve a ejecutar su celda y activa el desplazamiento de esa salida o recarga la ventana. Pueden mantenerse límites adicionales para salidas extremadamente grandes.

1. Crea el entorno y abre Jupyter siguiendo el [README](../README.md#ejecutar-el-proyecto). Selecciona el kernel **Python (SmartFood)**.
2. Ejecuta 00. Si se instalaron paquetes, reinicia el kernel y repite 00. Revisa el diagnóstico antes de continuar; puedes ejecutar preparación de datos si sus imports pasan aunque los modelos tengan una incidencia registrada.
3. Prepara los Parquet. Reinicia el kernel de cada notebook antes de ejecutar todas sus celdas. Esto evita depender de variables creadas manualmente o de ejecuciones fuera de orden.
4. Completa 01 y 02. Comprueba que los archivos intermedios y procesados se hayan generado y que los datos filtrados no estén vacíos.
5. Ejecuta cada enfoque con los mismos datos procesados. Registra versiones, parámetros y cualquier error o warning antes de interpretar los resultados.

El notebook [01_preparacion_datos.ipynb](../notebooks/01_preparacion_datos.ipynb) requiere Parquet y no realiza la descarga ni la conversión desde CSV. La celda inicial de cada notebook resuelve las rutas y crea carpetas; no comprueba todos los requisitos de datos. Las salidas de la tabla describen el flujo previsto; su disponibilidad actual se identifica en el [registro de ejecución](ejecuciones.md).

## Precauciones al reproducir

- Los notebooks pueden mezclar salidas históricas y comprobaciones recientes. Abrirlos o ver contadores de ejecución no prueba una ejecución completa. El [registro de ejecución](ejecuciones.md) identifica la evidencia disponible.
- La pasada vigente de 01–05 terminó sin errores de celda en Python 3.14.4. El antiguo error de PyArrow de 01 no aparece en esas salidas. El informe de entorno de 00 se regeneró el 7 de octubre de 2026 en `reports/entorno/`.
- Los Parquet contienen listas de ingredientes y otros campos. Hay que preparar su representación para cardinalidad, duplicados y TF-IDF; la limpieza actual no convierte esas listas a texto.
- Los ejemplos seleccionan posiciones fijas de usuarios y recetas. Un subconjunto más pequeño puede no contener esas posiciones; deben ajustarse antes de ejecutar con datos reducidos.
- El [04_filtrado_colaborativo_nmf.ipynb](../notebooks/04_filtrado_colaborativo_nmf.ipynb) conserva la elección de 70 componentes. El grid actual minimiza RMSE con 10. Revisa la [evaluación](evaluacion.md#nmf-reconstrucción-de-interacciones-ocultas) antes de considerarla una configuración recomendada.
- El [05_clasificacion_ranking_svm.ipynb](../notebooks/05_clasificacion_ranking_svm.ipynb) contiene dos exportaciones al mismo `recomendaciones_svm.csv`: la segunda reemplaza la primera. Usa nombres distintos si necesitas conservar ambos resultados.
- Un rating cero se usa como clase negativa en SVM y no como una entrada positiva observada en la evaluación NMF. Su significado necesita revisión.
- En 05, la carga convierte las listas o arreglos de `recipeingredientparts` a documentos de texto mediante `smartfood.texto.texto_ingredientes`, antes del merge y del split. Los ingredientes vacíos se consideran ausentes y se excluyen del entrenamiento mediante el filtro existente. Esta transformación se aplica en memoria; los Parquet originales conservan las listas. Si aparece `numpy.ndarray ... has no attribute lower`, reinicia el kernel y ejecuta desde la carga para reconstruir las variables del pipeline con texto.
- Una ejecución completa puede requerir bastante memoria por la exploración y las matrices densas. Los ejemplos reducidos deben registrar el muestreo utilizado.

## Presentación de los experimentos

### Cifras automáticas del notebook 02

Los ocho bloques de interpretación numérica se generan con `IPython.display.Markdown` desde `smartfood.anotaciones`. Se ven como texto Markdown debajo de sus celdas de código; Jupyter no interpola variables en las celdas Markdown estáticas. Ejecuta el notebook desde el principio para actualizar datos, métricas y comentarios en orden. Si editas el umbral de la selección final, vuelve a ejecutar desde esa selección hasta el final.

Los comentarios calculan tamaños, nulos de campos específicos, estadísticas de calorías y rating agregado, porcentajes de ratings, historiales, esparsidad y cobertura. La esparsidad utiliza pares usuario–receta únicos con IDs completos y cuenta ratings cero como observaciones. Los historiales también cuentan pares distintos; podrían diferir de los gráficos basados en filas si se incorporan pares repetidos. Los porcentajes de rating usan todas las reseñas como denominador; los nulos no cuentan como ratings positivos ni como ceros.

El resumen del filtro se calcula después de aplicar el umbral final, no con el último resultado del bucle exploratorio. Al terminar, se exportan `reports/eda/metricas_eda.json` y `reports/eda/conclusiones_eda.md`; cada ejecución reemplaza estos dos reportes. Las estadísticas no definidas se muestran como «no disponible» y se guardan como `null`.

Las explicaciones metodológicas siguen siendo textos revisados manualmente. Las plantillas no validan desempeño ni corrigen los diagnósticos de cardinalidad de listas. La [revisión del EDA](revision_eda.md) conserva una instantánea histórica y no se sobrescribe con estos reportes. Los gráficos y diagnósticos conservados requieren ejecutar nuevamente sus celdas para corresponder a datos nuevos.

### Interpretaciones condicionadas en los análisis

Las funciones de `src/smartfood/anotaciones.py` cambian su texto según los resultados y explicitan qué regla se utiliza:

- **02, correlaciones:** calcula Pearson y Spearman entre calorías y proteína del catálogo filtrado. Excluye pares incompletos, no numéricos e infinitos. Con menos de tres pares no interpreta; con una variable constante informa que el coeficiente no está definido. Clasifica el valor absoluto sin redondear con cortes configurables: por debajo de 0,10, muy débil; desde 0,10, débil; desde 0,30, moderada; desde 0,50, fuerte; desde 0,70, muy fuerte. La dirección se informa por separado. Son convenciones descriptivas del proyecto, no umbrales universales ni pruebas de significancia. Los comentarios también se incorporan al reporte Markdown del EDA.
- **03, cantidad de recomendaciones:** utiliza `top_n` y el resultado efectivamente devuelto. Distingue lista vacía, incompleta o completa. Cambia el usuario en la celda del ejemplo y `top_n` en la variable correspondiente; ejecuta esa celda y la interpretación siguiente.
- **04, grid NMF:** identifica el menor RMSE válido, informa empates y comprueba si `componentes_seleccionados` alcanza ese mínimo. También informa si la configuración seleccionada no tiene un resultado válido. Se conserva el valor histórico de 70 como parámetro; las anotaciones no cambian la elección automáticamente.
- **05, clasificación:** compara accuracy contra predecir la clase mayoritaria del entrenamiento, evaluada en el mismo test. Informa si la supera, iguala o queda por debajo, si se predice una sola clase y el recall de cada clase. Si una clase no aparece en test, su recall se muestra como no disponible.

Ejecuta los notebooks en orden interno para actualizar estas salidas. Las anotaciones no vuelven a entrenar modelos, no cambian el protocolo de evaluación ni certifican calidad de recomendaciones. La pasada actualizó las salidas de 01–05; consulta el [registro de ejecución](ejecuciones.md) para sus resultados.

Los notebooks describen entradas, operaciones y ejemplos; 02–05 incorporan interpretaciones calculadas. La pasada vigente regeneró sus resultados. La comparación cuantitativa con el baseline mayoritario está implementada para SVM; la evaluación de relevancia de ranking y los baselines de rating continúan pendientes.

No se debe presentar el SVM como un recomendador personalizado ni como búsqueda por similitud sin modificar y evaluar esas funciones. El nombre `05_clasificacion_ranking_svm.ipynb` refleja el alcance del código actual.

## Informe integral automático

01 y 03–05 exportan métricas y comentarios, y 02 mantiene sus reportes de EDA. La celda final de cada análisis y el maestro regeneran [reports/informe_final/informe_final.md](../reports/informe_final/informe_final.md). Consulta la [guía del informe](informe_final.md).
