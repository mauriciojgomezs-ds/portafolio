# Verificación inicial

00 y 06 se ejecutaron el 07-10-2026 10:30:42 (America/Santiago). El maestro completó 01–05 con kernels independientes.

Duración de la verificación (incluye 00 y el maestro): 40.38 segundos. Las cifras y conclusiones están en la [evaluación](../reports/evaluacion/evaluacion.md); las versiones, en [environment.json](../reports/entorno/environment.json).

Las alertas por notebook están registradas en el [inventario de ejecución](ejecuciones_registro.json). La revisión de procedencia y las limitaciones descritas en metodología siguen vigentes; una pasada sin errores no demuestra calidad del modelo.

Se reejecutaron 03_baseline, 04_modelado, 05_evaluacion el 2026-10-07T10:35:45.339849-03:00 para comprobar tablas, figuras y comentarios finales. Se mantuvieron las particiones, parámetros y criterios de selección. El resumen del maestro conserva la pasada completa inicial; el inventario registra esta comprobación posterior.

## Comprobación después de homologar

El 7 de octubre de 2026 se comprobaron el paquete local, las rutas a back, la apertura desde raíz/proyecto/notebooks y el comando de ejecución. Se reejecutaron 00 y 05 con los modelos existentes; no se volvió a entrenar ni se cambió el criterio de selección. El resumen del maestro mantiene la pasada completa anterior. Consulta el [registro de estructura](verificacion_estructura.json).

## Independencia de la carpeta de proyecto

Las fuentes se localizaron en data/raw y las instrucciones y registros se copiaron a docs. La comprobación de copia y renombrado está en [verificacion_independencia.json](verificacion_independencia.json); no implica una nueva selección de modelos.

## Reportes agrupados por etapa

El 7 de octubre de 2026 se agruparon los reportes por etapa y se actualizaron las rutas de generación y lectura. Se reejecutaron 00, 02, 05 para comprobar las nuevas rutas; las pruebas locales y los enlaces se comprobaron correctamente. No se reentrenaron los modelos de 03 y 04. El resumen del maestro conserva la pasada completa anterior. Consulta la [verificación de reportes](verificacion_reportes.json).
