# Resultado del caso sintético

Calculado desde una revisión explícita. No es una evaluación producida por IA ni una medición de precisión del modelo.

Origen de la revisión: `synthetic_reference`.

| Indicador | Resultado |
| --- | --- |
| Cumplimiento ponderado evaluable | 69.44 % |
| Peso evaluable de la agenda | 90.00 % |
| Cobertura ponderada conocida | 83.33 % |
| Cobertura por temas conocidos | 75.00 % (3 de 4) |
| Sensibilidad sobre toda la agenda | 62.50 % a 72.50 % |

La sensibilidad supone resultados mínimo y máximo para los objetivos no evaluables; no es un intervalo estadístico.

| Objetivo | Cobertura | Cumplimiento | Evidencia |
| --- | --- | --- | --- |
| O1 | discussed | fulfilled | S06, S07, S20 |
| O2 | discussed | partial | S08, S09, S10, S20 |
| O3 | discussed | fulfilled | S11, S12, S13, S14, S15 |
| O4 | not_discussed | not_fulfilled | S20 |
| O5 | unknown | not_evaluable | S17 |

## Justificación

- **O1:** Se reemplazó una propuesta inicial y se aprobó explícitamente el máximo final.
- **O2:** Hay una fecha concreta propuesta, pero el acuerdo exige confirmación posterior.
- **O3:** Se asignaron las dos tareas con responsable final y fecha. La carga cambió de la propuesta inicial a Diego.
- **O4:** El cierre confirma que se pospone sin analizar permisos ni retención y que no hay acuerdos. Anunciar o aplazar el tema no es tratarlo sustantivamente.
- **O5:** Se anuncia el tema, pero el tramo siguiente está ausente. No es posible confirmar si se discutieron o acordaron sus componentes.

Las citas literales se conservan en el JSON. La validación confirma su existencia, no su respaldo semántico. Una propuesta automática futura requerirá revisión y comparación con anotaciones independientes.
