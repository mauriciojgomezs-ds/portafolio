# Reportes y versión para el portafolio

`reports/` contiene una única versión vigente de los resultados generados. Después de su limpieza del 6 de octubre de 2026, el maestro completó 01–05 y regeneró sus artefactos y salidas. El reporte de entorno de 00 se regeneró el 7 de octubre de 2026; el [registro de ejecución](ejecuciones.md) describe el estado comprobado.

## Regeneración

Puedes ejecutar primero 00 y después [06_ejecucion_completa.ipynb](../notebooks/06_ejecucion_completa.ipynb), que automatiza los pasos 01–05 con kernels independientes. Guarda y cierra los notebooks individuales antes de iniciar el maestro. La alternativa manual se detalla a continuación.

1. Ejecuta 00 en el Python que vas a utilizar. Si instala dependencias, reinicia el kernel y repite 00 hasta obtener un diagnóstico satisfactorio.
2. Ejecuta 01 y comprueba que termina sin errores y genera los dos Parquet intermedios.
3. Ejecuta 02 para regenerar el subconjunto, las inspecciones, las cifras y las conclusiones. Revisa los diagnósticos impresos de cardinalidad: no se convierten automáticamente en alertas tabuladas.
4. Ejecuta 03, 04 y 05 sobre ese mismo subconjunto, reiniciando sus kernels. Comprueba métricas, ejemplos y las tablas finales de alertas.
5. Guarda los notebooks y actualiza el registro de ejecución y la evaluación con resultados de esta nueva pasada. Una tabla de alertas vacía no prueba que todas las celdas hayan terminado correctamente.

## Artefactos vigentes

| Ubicación | Contenido | Comportamiento al repetir |
| --- | --- | --- |
| `reports/entorno/environment.json` | Diagnóstico del Python e imports, con fecha interna | Reemplaza el anterior |
| `reports/entorno/environment.requirements.txt` | Versiones exactas del entorno comprobado | Reemplaza el anterior |
| `reports/eda/<dataset>/inspeccion_<dataset>.md` | Inspección y enlaces a figuras | Reemplaza el anterior |
| `reports/eda/<dataset>/<dataset>_hist_*.png` y `<dataset>_correlacion.png` | Figuras de la inspección | Retira las figuras propias anteriores y genera las actuales |
| `reports/eda/metricas_eda.json` | Métricas originales, filtradas y umbral seleccionado | Reemplaza el anterior |
| `reports/eda/conclusiones_eda.md` | Comentarios y correlaciones calculados | Reemplaza el anterior |
| `reports/alertas/<notebook>.json` | Warnings registrados en el proceso de cada notebook | Reemplaza el anterior |
| `reports/ejecucion/resumen.json` | Estado y duración de las etapas iniciadas desde el maestro | Reemplaza el anterior |

Las interpretaciones condicionales están descritas en la [guía de notebooks](notebooks.md). 03–05 muestran y exportan sus interpretaciones en `reports/baseline/`, `reports/modelado/` y `reports/evaluacion/`. El maestro y las celdas finales de cada análisis reúnen esos resultados en `reports/informe_final/informe_final.md`. La exportación inicial reutiliza comentarios de las ejecuciones guardadas; al repetir 03–05, las cifras se guardan directamente desde sus variables.

## Publicación

El `.gitignore` permite versionar los reportes vigentes y excluye `reports/runs/`, usado para pruebas locales. Los datos, modelos y recomendaciones de `data/output/` conservan sus exclusiones anteriores. Antes de publicar, revisa que los reportes y los notebooks correspondan al mismo entorno y subconjunto; los informes de entorno y alertas pueden contener rutas locales.

Publica solo los archivos vigentes de `reports/`, los notebooks finales y la documentación actualizada. `reports/informe_final/informe_final.md` reúne la evidencia vigente; `docs/evaluacion.md` conserva la revisión del 6 de octubre; `revision_eda.md` conserva la revisión inicial y enlaza los reportes regenerados. Conserva el diagnóstico de 00 para incluir las versiones exactas del entorno. Repetir una etapa no garantiza que las demás se hayan vuelto a ejecutar: completa el recorrido antes de publicar.

## Respaldo local

Antes de vaciar `reports/` se guardó un ZIP comprobado en `.local/backups/`, excluido del versionado. Es una copia de recuperación, no un resultado para publicar. La limpieza no regeneró resultados; la ejecución posterior del maestro sí completó 01–05.
