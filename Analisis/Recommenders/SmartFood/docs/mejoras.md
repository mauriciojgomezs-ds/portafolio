# Plan de mejoras

La ejecución secuencial de 01–05 está completada y documentada. El siguiente trabajo debe mejorar la integridad de los datos y la evaluación, antes de construir una demo.

## Implementado

- Paquete reutilizable, instalación desde requirements y comprobación del entorno con 00.
- Maestro 06 con ejecución secuencial, kernels independientes, parada ante fallos y resumen de tiempos.
- Cifras automáticas del EDA e interpretaciones condicionadas para correlaciones, recomendaciones, grid NMF y clasificación.
- Conversión de listas de ingredientes a texto para el entrenamiento SVM y la similitud TF-IDF.
- Tabla de warnings con explicaciones, detalle original y exportación JSON.
- Reportes con nombres estables, respaldo local excluido y documentación de la pasada vigente.
- Comparación SVM con la clase mayoritaria del entrenamiento en el mismo test.

## Prioridades pendientes

| Orden | Trabajo | Motivo | Criterio de cierre |
| --- | --- | --- | --- |
| 1 | Regenerar el diagnóstico 00 | La nueva pasada no incluye el entorno y no hay reporte vigente | JSON, versiones exactas e imports satisfactorios del mismo Python |
| 2 | Completar controles de integridad | Cardinalidad por listas falla; hay 19 pares fuera del catálogo original | Controles reproducibles, tratamiento explícito del desajuste y mapeos persistidos |
| 3 | Definir relevancia y semántica de rating cero | Los enfoques utilizan diferentes nociones de observación y positividad | Criterio documentado y compartido entre particiones y métricas |
| 4 | Separar validación y test | Componentes y thresholds se exploran sobre las mismas interacciones de evaluación | Test independiente, validación definida y features revisadas temporalmente |
| 5 | Comparar y mejorar modelos | SVM iguala la clase mayoritaria; NMF selecciona 70 sin minimizar RMSE | Baselines apropiados, parámetros justificados y métricas por tarea |
| 6 | Evaluar ranking y casos de estudio | Los ejemplos no acreditan relevancia | Precision@K, Recall@K, NDCG@K y cobertura con candidatos y protocolo comunes |

## Datos y robustez

La pasada vigente de 01 ya no muestra el antiguo error de lectura de PyArrow. La conversión de ingredientes está implementada para SVM; el resto de campos de listas todavía requiere tratamiento según su uso. Deben revisarse las reglas generales de puntuación cuando afectan URLs, duraciones o cantidades.

La cobertura y las distribuciones ya se cuantifican en el EDA. Falta evaluar representatividad, conservar IDs originales, registrar procedencia y huellas de entradas y revisar los 19 pares cuyo ID de receta no aparece en el catálogo inicial.

Resolver categorías vacías, usuarios sin historial, vecinos sin peso y scores constantes. Diferenciar nombres de exportaciones SVM para evitar que dos funciones reemplacen el mismo CSV. Los errores capturados e impresos por los diagnósticos deben tener un estado estructurado para que el maestro pueda distinguir controles incompletos de una ejecución satisfactoria.

## Modelos y publicación

Para SVM, revisar aggregatedrating y su disponibilidad temporal; ajustar el modelo en validación y comparar métricas por clase. Para personalizar, incorporar información del usuario y medir el cambio. La normalización de scores no produce probabilidades.

Para NMF, comparar medias y popularidad, justificar la selección de componentes y revisar el efecto de imputar ausencias como cero. Medir reconstrucción y ranking por separado.

Los resultados actuales ya están documentados. Antes de publicar, completa el entorno 00 y revisa la coherencia entre notebooks y reportes. Las versiones, parámetros, semillas, huellas y ejemplos con IDs originales deben acompañar una evaluación final. La demo queda para después de validar el comportamiento que mostrará.
