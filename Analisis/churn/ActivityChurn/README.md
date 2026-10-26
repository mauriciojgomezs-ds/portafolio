# ActivityChurn
![Python](https://img.shields.io/badge/python-3.10%2B-blue) ![scikit--learn](https://img.shields.io/badge/scikit--learn-1.6%2B-orange) ![estado](https://img.shields.io/badge/estado-completado-brightgreen)

**Contenido:** [Datos](#datos-y-particiones) · [Resultados](#modelo-y-resultados-iniciales) · [Reproducción](#reproducción) · [Informe integral](#informe-integral)

## Clasificación de abandono a partir de actividad de usuarios

Proyecto de clasificación binaria sobre una tabla de actividad con transacciones, puntos, frecuencia y recencia. Explora si estas variables permiten distinguir el objetivo `flagChurn` y superar una regla mayoritaria bajo una partición temporal.

**Estado:** 00 pasó su comprobación de entorno y el maestro completó 01–05 el 6 de octubre de 2026. La primera evaluación temporal supera al baseline; la procedencia, definición del churn y disponibilidad temporal de atributos siguen pendientes de confirmar.

[Resultados](reports/evaluacion/evaluacion.md) · [Resumen de ejecución](reports/ejecucion/resumen.json) · [Metodología](docs/metodologia.md) · [Registro](docs/ejecuciones.md)

## Datos y particiones

El CSV contiene 5.496 filas, 43 columnas, 2.251 usuarios y 14 fechas. El ZIP menciona SaaS, pero sus variables de puntos y actividad requieren confirmar el dominio en la fuente.

| Partición | Periodo | Registros | Casos positivos |
| --- | --- | ---: | ---: |
| Entrenamiento | Marzo de 2024 a febrero de 2025 | 4.742 | 2.173 |
| Validación | Marzo de 2025 | 451 | 262 |
| Test | Abril de 2025 | 303 | 153 |

Se excluyen `idUsuario`, `dtRef` y `qtdeChurn` de las features. Hay 185 usuarios de entrenamiento presentes también en test: el protocolo evalúa meses futuros de una población con usuarios conocidos, no exclusivamente usuarios nuevos. La partición temporal por sí sola no acredita que todos los atributos estuvieran disponibles antes del churn.

## Modelo y resultados iniciales

Se compararon dos regresiones logísticas: sin ponderar y con `class_weight="balanced"`. La versión sin ponderar obtuvo la mayor average precision en validación: 0,8571 frente a 0,8562. La selección se realizó antes de evaluar test; esa diferencia pequeña no demuestra una superioridad general de una variante.

| Métrica en test | Baseline mayoritario | Regresión logística |
| --- | ---: | ---: |
| Accuracy | 49,50 % | 77,23 % |
| Average precision | 0,5050 | 0,8218 |
| ROC-AUC | 0,5000 | 0,8374 |
| Recall de churn | 0,00 % | 79,08 % |
| F1 macro | 0,3311 | 0,7721 |

El modelo mejora la accuracy en **27,72 puntos porcentuales** sobre el baseline y predice ambas clases. Detecta 121 de los 153 casos positivos; omite 32 y marca como positivos 37 casos negativos. La precisión de churn es 76,58 %.

El baseline predice siempre la clase 0, mayoritaria en entrenamiento. En test la clase positiva alcanza 50,50 %, por lo que su accuracy baja a 49,50 %. Este cambio de proporciones forma parte de la lectura temporal del experimento.

Las métricas corresponden a 303 registros de un solo mes. Son un resultado inicial favorable sobre esta partición; todavía no acreditan impacto de negocio, estabilidad en otros periodos ni ausencia de fuga de información. No se ajustó el threshold utilizando test.

![Matriz de decisiones del modelo sobre test](reports/evaluacion/decisiones.png)

## Reproducción

1. Selecciona el Python del proyecto y ejecuta [00](notebooks/00_configuracion_entorno.ipynb).
2. Guarda y cierra los notebooks individuales.
3. Ejecuta [06](notebooks/06_ejecucion_completa.ipynb), o recorre 01–05 manualmente.
4. Revisa los reportes y las alertas antes de interpretar los resultados.

El maestro utiliza un kernel nuevo por etapa, registra el avance y se detiene ante errores. Los reportes tienen nombres estables. La pasada actual duró unos 16 segundos, sin incluir 00, en Python 3.14.4. No se registraron warnings en 00–05.

## Siguiente revisión

Confirmar fuente y licencia, significado y horizonte de `flagChurn` y momento de disponibilidad de cada atributo. Después, evaluar estabilidad con varias ventanas temporales y explicar los coeficientes del modelo. Si se ajustan thresholds o costes de errores, deben seleccionarse en validación, conservando un test independiente.

## Estructura local

Consulta la [estructura y comandos del proyecto](docs/estructura.md). Las funciones se importan desde su propio `src/`; los requisitos se instalan desde esta carpeta. Los datos de entrada están en `data/raw` y sus rutas se declaran en `config.json`.

## Independencia

El proyecto incluye su código, requisitos, datos de entrada e instrucciones. Se puede copiar o renombrar conservando esta carpeta completa; la ejecución no utiliza otros proyectos ni una carpeta temática. Los datos están excluidos del versionado: consulta las [fuentes](docs/fuentes.md) para preparar una copia nueva.

Los reportes están agrupados por etapa. Consulta su [distribución y archivos vigentes](docs/estructura.md#organización-de-reportes).

## Informe integral

Consulta el [informe integral](reports/informe_final/informe_final.md). Se actualiza con 06 y reúne cifras, conclusiones, limitaciones y próximos pasos. Para regenerarlo con resultados existentes usa `python scripts/generate_report.py`. Consulta la [guía del informe](docs/informe_final.md).

## Probabilidades y decisiones

04 incorpora un modelo adicional con calibración independiente del ajuste y umbral elegido en validación. 05 muestra fiabilidad, soporte y costes ilustrativos de varias políticas sobre test, sin reajustarlos. Consulta [protocolo y evidencia](docs/decisiones.md).
