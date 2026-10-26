# Registro de ejecución

## Pasada vigente

El maestro `06_ejecucion_completa.ipynb` registró una ejecución satisfactoria de 01–05 el **6 de octubre de 2026, de 22:08:58 a 22:10:50**, en America/Santiago. Las fechas del [resumen original](../reports/ejecucion/resumen.json) están guardadas en UTC. La secuencia usó el Python local 3.14.4 y un límite de 900 segundos por celda.

| Etapa | Duración | Evidencia | Estado |
| --- | ---: | --- | --- |
| 01 · Preparación | 48,64 s | Notebook actualizado y Parquet intermedios | Completado sin errores de celda |
| 02 · Exploración | 49,00 s | Notebook, inspecciones, figuras y `reports/eda/` | Completado; cuatro mensajes de diagnóstico fallido por listas |
| 03 · Baseline | 1,23 s | Ejemplo del usuario 198 y comentario calculado | Completado; cinco recomendaciones para top-5 |
| 04 · NMF | 7,90 s | Grid, entrenamiento, ejemplos y artefactos de modelos | Completado; la selección de 70 componentes no minimiza RMSE |
| 05 · SVM | 4,88 s | Evaluación, rankings y exportaciones del notebook | Completado; predice siempre la clase positiva |

Tiempo transcurrido total: aproximadamente 111,66 segundos. No incluye el notebook 00. Las duraciones son observadas en este equipo, no un requisito ni una promesa de rendimiento.

Los notebooks 01–05 no contienen salidas de tipo `error` en esta pasada. Cada uno guarda una tabla de alertas vacía en `reports/alertas/`. Esto indica ausencia de warnings registrados, no ausencia de todos los problemas: los diagnósticos de cardinalidad del EDA capturan errores y los imprimen, por lo que no interrumpen la secuencia ni aparecen como warnings.

## Resultados comprobados en las salidas

- **EDA:** 522.517 recetas y 1.401.982 reseñas originales; subconjunto de 190 recetas, 617 usuarios y 10.343 reseñas. Umbral previo a la intersección: 270. Mínimos finales: una interacción por usuario y por receta observada.
- **Integridad:** 19 pares registrados referencian recetas ausentes del catálogo original; ninguno en el subconjunto filtrado. No hay pares repetidos ni nulos en usuario, receta y rating.
- **Correlación del subconjunto:** calorías y proteína, Pearson ≈ 0,713 y Spearman ≈ 0,797 sobre 190 pares. Las etiquetas automáticas son convenciones descriptivas del proyecto.
- **NMF:** el grid obtiene su menor RMSE con 10 componentes, ≈ 4,19964; con 70 obtiene ≈ 4,4884. Se entrenó la configuración seleccionada de 70. La evaluación oculta 2.035 interacciones positivas.
- **SVM:** 2.065 casos de test, 128 negativos y 1.937 positivos. Todos se predicen positivos; accuracy ≈ 93,8015 %, igual al baseline mayoritario del entrenamiento evaluado sobre ese mismo test.

Consulta la [evaluación](evaluacion.md) para interpretar las métricas y sus límites. Estas cifras proceden de la pasada registrada, no de un nuevo entrenamiento realizado durante la actualización documental.

## Entorno regenerado el 7 de octubre de 2026

El notebook 00 se ejecutó el 7 de octubre de 2026 y generó `reports/entorno/environment.json` y `environment.requirements.txt`, con versiones exactas, imports y `pip check` del Python activo. El maestro ejecuta exclusivamente 01–05.

El último diagnóstico anterior a la limpieza pasó en Python 3.14; no acredita que `.venv` funcione ni sustituye la nueva comprobación. El archivo `docs/requirements_ejecucion.txt` conserva el primer entorno observado y no debe presentarse como el entorno de esta pasada.

## Trazabilidad y publicación

Antes de esta pasada se vació `reports/` y se verificó un respaldo local de 61 archivos en `.local/backups/`, excluido del versionado. La nueva ejecución regeneró inspecciones, cifras y alertas. Los nombres estables evitan acumular versiones de cada reporte. Las salidas de los notebooks individuales también se actualizaron.

La evidencia previa de preparación y los diagnósticos fallidos de imports quedan en el respaldo; el antiguo `ArrowKeyError` de 01 no aparece en la pasada actual. No se atribuye su resolución a una causa específica.

Para cerrar la versión de publicación, conserva el diagnóstico de 00 y el resumen, y revisa los [pasos de publicación](publicacion.md). Procedencia, huellas de datos y mapeos a IDs originales todavía requieren trabajo.

## Reportes agrupados por etapa

El 7 de octubre de 2026 se agruparon los reportes por etapa y se actualizaron las rutas de generación y lectura. Se reejecutaron 00, 02 para comprobar las nuevas rutas; las pruebas locales y los enlaces se comprobaron correctamente. No se reentrenaron los modelos de 03 y 04. El resumen del maestro conserva la pasada completa anterior. Consulta la [verificación de reportes](verificacion_reportes.json).

## Informe integral automático

El 7 de octubre de 2026 se ejecutó 06 con la generación integral incorporada; 01–05 terminaron sin errores. Inicio UTC: 2026-10-07T14:45:16.906851+00:00; fin UTC: 2026-10-07T14:47:13.657068+00:00. Consulta el [informe integral](../reports/informe_final/informe_final.md) y su [guía](informe_final.md). El resumen del maestro registra esta nueva pasada.
