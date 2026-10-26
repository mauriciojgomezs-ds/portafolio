# Metodología y reportes compartidos

## Separación de etapas

00 comprueba imports y compatibilidad del entorno con `pip check`. Si faltan módulos instala los requisitos y solicita reiniciar el kernel. 01 prepara las entradas y crea particiones persistidas; 02 explora train; 03 ajusta el baseline; 04 compara candidatos exclusivamente en validación; 05 evalúa el modelo seleccionado en test; 06 automatiza 01–05, sin incluir 00.

Los transformadores numéricos y categóricos se ajustan solo en entrenamiento: imputación mediana y escalamiento de números; imputación modal y OneHotEncoder para categorías. Los IDs y atributos excluidos por configuración no participan como features. No se realiza oversampling ni se optimiza un threshold. El presupuesto inicial de iteraciones de regresión logística es 1.000; cualquier aviso de convergencia requiere revisión.

El baseline `DummyClassifier(strategy="prior")` usa las frecuencias de clase de train y predice la clase mayoritaria. Los dos candidatos logísticos difieren en `class_weight`: sin ponderación y `balanced`. Se elige el de mayor average precision en validación; en empate se conserva el primero. El modelo elegido se mantiene ajustado en train y se evalúa en test; no se reentrena con validación en esta versión.

## Particiones y supuestos

- **BankChurn:** división aleatoria estratificada 60/20/20, semilla 42. No mide una evolución temporal ni prueba generalización a otro banco.
- **SubscriptionChurn:** se conserva el archivo de test suministrado. El archivo de entrenamiento se divide 80/20 de forma estratificada, semilla 42. Una fila sin objetivo se descarta y queda registrada. La separación suministrada no acredita independencia: el reporte cuenta IDs compartidos y todavía deben contrastarse los clientes y posibles registros equivalentes.
- **ActivityChurn:** las fechas anteriores a la penúltima forman train; penúltima y última forman valid y test. Con las entradas actuales, validación es marzo de 2025 y test abril de 2025. Usuarios pueden aparecer en meses distintos: este protocolo representa predicción de actividad futura de usuarios existentes, no evaluación de usuarios completamente nuevos. `qtdeChurn` se excluye por su posible relación directa con el target. Hay que confirmar qué representa `flagChurn`, su horizonte y cuándo estaban disponibles los atributos.
- **TelecomChurn:** se conserva el test de 667 registros y se reserva 20 % del archivo de 2.666 para validación. `Area code` se fuerza a categoría y se excluyen cargos redundantes con minutos. No hay ID: se registran filas completas coincidentes, pero la independencia por cliente no puede verificarse. El target booleano se convierte a 0/1.

Estas decisiones permiten organizar los experimentos; no sustituyen la documentación del origen y del proceso de etiquetado. Los identificadores compartidos se registran como conteo, sin publicar una lista de clientes.

La preparación inicial encontró 0 IDs compartidos entre train y test en BankChurn, 50.320 en SubscriptionChurn y 185 en ActivityChurn. La coincidencia temporal de ActivityChurn es compatible con el protocolo descrito. En SubscriptionChurn debe confirmarse si los IDs identifican realmente los mismos clientes o son contadores locales de archivos; no se atribuye independencia al test suministrado sin esa revisión.

## Evidencia generada

| Archivo en reports/ | Evidencia |
| --- | --- |
| `environment.json` | Python, versiones importadas y pip check |
| `preparacion.json` | SHA-256 de CSV, registros originales/utilizables, filas sin objetivo, particiones y coincidencias de IDs |
| `eda.json`, `eda.md`, `distribucion_target.png` | Tamaño, balance de clases, nulos y exclusiones sobre train |
| `baseline_validacion.json` | Accuracy, average precision, ROC-AUC, matriz y métricas por clase |
| `modelos_validacion.json` | Comparación de candidatos y ponderación elegida |
| `evaluacion_test.json`, `evaluacion.md` | Comparación final del modelo y baseline sobre test |
| `alertas/<notebook>.json` | Avisos emitidos, descripción genérica y acción sugerida |
| `ejecucion/resumen.json` | Estado, intérprete y duración por etapa del maestro |

Los reportes se reemplazan por etapa; los modelos se guardan en `models/` y las particiones en `data/processed/`. El maestro actualiza las salidas de los notebooks completados. Ante errores conserva la copia parcial en `reports/runs/fallos/` y no ejecuta las etapas posteriores.

## Lectura de resultados

Accuracy debe acompañarse de recall por clase, matriz de confusión, average precision y ROC-AUC. Si test no contiene ambas clases, AP y ROC-AUC se guardan como `null`, sin atribuirles un valor artificial. Las métricas indefinidas del reporte de clasificación se representan como cero mediante `zero_division=0`.

Los comentarios cambian con las cifras y la comparación contra el baseline. Las alertas agrupan warnings, conservando el detalle; no convierten todos los logs o excepciones capturadas en una validación global. La ausencia de avisos no acredita buen desempeño ni ausencia de fuga.

Antes de una publicación final deben completarse procedencia y licencia, definición del churn, disponibilidad temporal, auditoría de registros compartidos y registro de resultados de la ejecución real de cada proyecto. Los resultados de datasets distintos no deben compararse como si midieran la misma población o dificultad.
