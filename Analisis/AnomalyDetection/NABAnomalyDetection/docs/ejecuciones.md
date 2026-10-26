# Verificación inicial

00 y 06 se ejecutaron el 07-10-2026 10:34:01 (America/Santiago). El maestro completó 01–05 con kernels independientes.

Duración de la verificación (incluye 00 y el maestro): 25.31 segundos. Las cifras y conclusiones están en la [evaluación](../reports/evaluacion/evaluacion.md); las versiones, en [environment.json](../reports/entorno/environment.json).

Las alertas por notebook están registradas en el [inventario de ejecución](ejecuciones_registro.json). La revisión de procedencia y las limitaciones descritas en metodología siguen vigentes; una pasada sin errores no demuestra calidad del modelo.

Se reejecutaron 05_evaluacion el 2026-10-07T10:36:11.003787-03:00 para comprobar tablas, figuras y comentarios finales. Se mantuvieron las particiones, parámetros y criterios de selección. El resumen del maestro conserva la pasada completa inicial; el inventario registra esta comprobación posterior.

Se reejecutaron 05_evaluacion el 2026-10-07T10:37:59.542911-03:00 para comprobar tablas, figuras y comentarios finales. Se mantuvieron las particiones, parámetros y criterios de selección. El resumen del maestro conserva la pasada completa inicial; el inventario registra esta comprobación posterior.

## Comprobación después de homologar

El 7 de octubre de 2026 se comprobaron el paquete local, las rutas a back, la apertura desde raíz/proyecto/notebooks y el comando de ejecución. Se reejecutaron 00 y 05 con los modelos existentes; no se volvió a entrenar ni se cambió el criterio de selección. El resumen del maestro mantiene la pasada completa anterior. Consulta el [registro de estructura](verificacion_estructura.json).

## Independencia de la carpeta de proyecto

Las fuentes se localizaron en data/raw y las instrucciones y registros se copiaron a docs. La comprobación de copia y renombrado está en [verificacion_independencia.json](verificacion_independencia.json); no implica una nueva selección de modelos.

## Reportes agrupados por etapa

El 7 de octubre de 2026 se reorganizaron los reportes por etapa y se actualizaron las rutas de escritura y visualización. Se ejecutaron 00 y 06; el maestro completó 01–05 sin errores y regeneró los resultados en sus nuevas carpetas. Se verificaron los enlaces locales y la prueba de causalidad temporal. Consulta la [verificación de reportes](verificacion_reportes.json) y el [resumen vigente del maestro](../reports/ejecucion/resumen.json).

## Informe integral automático

El 7 de octubre de 2026 se ejecutó 06 con la generación integral incorporada; 01–05 terminaron sin errores. Inicio UTC: 2026-10-07T14:44:28.976556+00:00; fin UTC: 2026-10-07T14:44:47.777845+00:00. Consulta el [informe integral](../reports/informe_final/informe_final.md) y su [guía](informe_final.md). El resumen del maestro registra esta nueva pasada.
