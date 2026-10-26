# Documentación de SmartFood

SmartFood explora recomendaciones de recetas mediante perfiles de usuario, NMF y clasificación con SVM. Esta carpeta reúne las instrucciones de reproducción, la descripción de datos, el análisis de los modelos y la evidencia de ejecución.

## Por dónde empezar

| Necesidad | Documento |
| --- | --- |
| Preparar Python e instalar dependencias | [Configuración del entorno](entorno.md) |
| Entender el orden de ejecución | [Guía de notebooks](notebooks.md) |
| Conocer entradas, transformaciones y artefactos | [Datos y reproducción](datos.md) |
| Consultar columnas y tipos observados | [Diccionario de datos](diccionario_datos.md) |
| Interpretar las métricas y sus limitaciones | [Evaluación](evaluacion.md) |
| Revisar las conclusiones del análisis exploratorio | [Revisión del EDA](revision_eda.md) |
| Ver qué se ejecutó y qué falta verificar | [Registro de ejecución](ejecuciones.md) |
| Regenerar reportes y publicar una sola versión | [Reportes y publicación](publicacion.md) |
| Priorizar el siguiente trabajo | [Plan de mejoras](mejoras.md) |
| Entender la reorganización del proyecto | [Registro de revisión](revision.md) |
| Contrastar el trabajo académico con el código | [Referencias académicas](referencias.md) |

Para una visión general, consulta el [README del proyecto](../README.md).

## Estado verificado al 6 de octubre de 2026

La ejecución completa de 01–05 terminó el 6 de octubre de 2026, entre las 22:08:58 y 22:10:50 de America/Santiago, mediante el notebook maestro y Python 3.14.4. Se actualizaron las salidas, datos procesados, modelos, inspecciones, comentarios y tablas de alertas. El [resumen de ejecución](../reports/ejecucion/resumen.json) registra el estado y los tiempos.

El SVM obtiene aproximadamente 93,80 % de accuracy y predice todos los casos como positivos: iguala al baseline mayoritario. NMF obtiene su menor RMSE con 10 componentes (≈ 4,1996), aunque mantiene 70 para entrenar. La [evaluación](evaluacion.md) conserva la revisión del 6 de octubre; el [informe integral](../reports/informe_final/informe_final.md) reúne los resultados vigentes.

El subconjunto contiene 190 recetas y 10.343 reseñas de 617 usuarios. El EDA todavía imprime fallos de cardinalidad por listas; las tablas vacías de warnings no contradicen esos fallos. El informe de entorno de 00 se regeneró el 7 de octubre de 2026 en `reports/entorno/`. Consulta el [registro](ejecuciones.md) y la [guía de publicación](publicacion.md) para cerrar la evidencia del entorno.

## Criterio de documentación

Las guías describen cómo funciona el proyecto; el registro de ejecución contiene hechos fechados; el plan de mejoras describe trabajo pendiente. Los tipos del diccionario se verificaron contra los metadatos locales de Parquet. Las unidades y el significado de los campos provienen de la documentación heredada y no sustituyen una validación de sus valores.

Los documentos de `references/` y el README de `archive/` se mantienen como fuentes originales. Sus afirmaciones y rutas históricas deben leerse junto con la revisión actual.
