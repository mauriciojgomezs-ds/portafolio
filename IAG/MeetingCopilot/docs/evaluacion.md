# Cumplimiento de agenda y evaluación de calidad

## Rúbrica previa

Cada objetivo tiene un peso positivo y criterios de aceptación. La cobertura responde si hubo tratamiento sustantivo; el cumplimiento responde si se alcanzó el resultado esperado. Una mención aislada o el anuncio de un tema no acredita cobertura.

| Cobertura | Interpretación |
| --- | --- |
| `discussed` | Existe contenido sustantivo sobre el tema. |
| `not_discussed` | No hay contenido sustantivo en una transcripción suficientemente completa para ese tema. |
| `unknown` | Una laguna o información insuficiente impide determinarlo. |

| Cumplimiento | Valor | Interpretación |
| --- | --- | --- |
| `fulfilled` | 1 | Se satisface el criterio esperado. |
| `partial` | 0,5 | Se satisface el criterio parcial definido de antemano. |
| `not_fulfilled` | 0 | No se alcanza el objetivo, aunque el tema pueda haberse discutido. |
| `not_evaluable` | Sin valor | La evidencia no permite asignar un resultado. |

No convertir automáticamente temas discutidos en objetivos cumplidos. Los casos no evaluables conservan su peso y se informan aparte; no se les asigna cero ni se les oculta.

## Fórmulas

**Cumplimiento ponderado evaluable:** 100 × suma de peso × valor para objetivos evaluables / suma de pesos evaluables.

**Cobertura ponderada conocida:** 100 × pesos de temas discutidos / pesos de temas con cobertura conocida. Informar también la cobertura por número de temas; pueden diferir porque los pesos son distintos.

**Proporción evaluable:** pesos evaluables / peso total. Mostrarla junto al cumplimiento para que no parezca una evaluación de toda la agenda cuando faltan datos.

**Intervalo por evidencia faltante:** como escenario de sensibilidad, calcular cumplimiento sobre el peso total suponiendo primero valor 0 y después valor 1 para todos los objetivos no evaluables. No es un intervalo estadístico ni una predicción del contenido faltante.

Si el denominador es cero, el indicador es `null` y se muestra como no calculable. Los pesos se fijan antes de observar el resultado y una edición posterior debe quedar registrada.

## Referencia del caso sintético

Los cinco objetivos tienen pesos 30, 25, 20, 15 y 10. La revisión asigna cumplido, parcial, cumplido, no cumplido y no evaluable, respectivamente. La suma de puntos evaluables es 62,5 y el peso evaluable es 90.

- Cumplimiento ponderado de los objetivos evaluables: **69,44 %**.
- Peso evaluable de la agenda: **90 %**.
- Cobertura ponderada de los temas conocidos: **83,33 %**.
- Cobertura por cantidad de temas conocidos: **75 %** (3 de 4).
- Escenario de cumplimiento sobre toda la agenda con el fragmento faltante: **62,5–72,5 %**.

Son resultados calculados desde una anotación escrita para esta prueba. No son precisión, confianza ni desempeño de IA. El guion incluye una corrección de presupuesto, una fecha tentativa, un cambio de responsable, un tema omitido y una sección faltante.

## Evaluar el futuro modelo

Preparar reuniones adicionales anotadas por personas, con partición de desarrollo y evaluación final. No usar el caso sintético actual como única evidencia ni incluir las respuestas de referencia en el contexto entregado al modelo.

Medir extracción de acuerdos y tareas, exactitud de nombres/cifras/fechas, respaldo de respuestas, recuperación de fragmentos, abstención y concordancia de cobertura/cumplimiento con revisores. Comparar el error del porcentaje final, pero revisar también cada objetivo: errores opuestos podrían cancelarse en el total.

Al incorporar audio, medir errores de transcripción y separación de hablantes, además de errores en entidades críticas. Reportar latencia y costo por separado para transcripción y análisis. Conservar citas, predicciones y correcciones para poder explicar cada resultado.
