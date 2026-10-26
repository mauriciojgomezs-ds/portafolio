# Nuevos análisis sin repetir objetivos

Se incorporan tres preguntas distintas, con datos, paquetes, requisitos y documentación locales. Cada proyecto contiene 00–06, alertas tabuladas, reportes por etapa e informe integral automático.

| Proyecto | Aporte | Diferencia respecto a lo existente |
| --- | --- | --- |
| [TrainingProgramImpact](../Analisis/CausalInference/TrainingProgramImpact/README.md) | Efecto de asignación a capacitación sobre ingresos; estimación e incertidumbre | No predice abandono ni atribuye causalidad a correlaciones observacionales |
| [PowerPlantRegression](../Analisis/Regression/PowerPlantRegression/README.md) | Predicción de potencia continua e intervalos calibrados | Usa condiciones contemporáneas; no repite pronóstico temporal |
| [WorkforceScheduling](../Analisis/Optimization/WorkforceScheduling/README.md) | Asignación de turnos con pausas, disponibilidad y restricciones | Recibe requisitos ya definidos; no repite pronóstico de llamadas ni Erlang C |

El ejemplo de turnos es sintético y sus reglas son didácticas. Causalidad utiliza una muestra experimental histórica seleccionada; no acredita impacto de programas actuales. Los intervalos de regresión dependen de intercambiabilidad y su cobertura observada se informa aunque resulte inferior a la nominal.

Los tres maestros se ejecutaron completos. También se repitieron las cinco etapas desde copias renombradas, sin datos procesados ni modelos previos y usando únicamente sus fuentes locales. Se reutilizó el intérprete disponible: esto no constituye una prueba de instalación en una máquina limpia. Consulta el [registro de comprobaciones](verificacion_analisis_incorporados.json).
