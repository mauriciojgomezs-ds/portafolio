# Churn: proyectos de clasificación

Esta carpeta organiza los conjuntos disponibles en proyectos independientes con el mismo recorrido de ciencia de datos: entorno, preparación, EDA, baseline, modelado y evaluación. Cada proyecto tiene su paquete local en src y conserva sus particiones, modelos y reportes separados.

| Proyecto | Fuente local | Tamaño observado | Decisión inicial |
| --- | --- | ---: | --- |
| [BankChurn](BankChurn/README.md) | `Churn_Modelling.csv` | 10.000 filas, 14 columnas | Train/valid/test estratificados: 60/20/20 |
| [SubscriptionChurn](SubscriptionChurn/README.md) | Archivos de entrenamiento y prueba | 440.833 y 64.374 filas, 12 columnas | Conservar test suministrado; reservar 20 % de train para validación |
| [ActivityChurn](ActivityChurn/README.md) | `abt_churn.csv` | 5.496 filas, 43 columnas | Split temporal: fechas anteriores, penúltima y última |
| [TelecomChurn](TelecomChurn/README.md) | `churn-bigml-80.csv` y `churn-bigml-20.csv` | 2.666 y 667 filas, 20 columnas | Conservar test suministrado; reservar 20 % del archivo de entrenamiento para validación |

Los tres ZIP bancarios originales contienen exactamente el mismo CSV, verificado por SHA-256. BankChurn utiliza uno como fuente; los otros se conservan sin extraer duplicados. La procedencia pública, licencia y definición temporal del churn aún deben documentarse. El nombre del ZIP del ABT menciona SaaS, pero sus variables de puntos, chat y actividad requieren confirmar el dominio; por eso se denomina ActivityChurn.

## Recorrido común

Cada proyecto contiene:

```text
notebooks/
├── 00_configuracion_entorno.ipynb
├── 01_preparacion_datos.ipynb
├── 02_analisis_exploratorio.ipynb
├── 03_baseline.ipynb
├── 04_modelado.ipynb
├── 05_evaluacion.ipynb
└── 06_ejecucion_completa.ipynb
config.json
data/raw/
data/processed/
models/
reports/
docs/metodologia.md
```

El código vive dentro de cada proyecto: `BankChurn/src/bank_churn`, `SubscriptionChurn/src/subscription_churn`, `ActivityChurn/src/activity_churn` y `TelecomChurn/src/telecom_churn`. Cada proyecto incluye scripts, tests, requisitos y pyproject.toml propios. La preparación registra huellas, descarta filas sin objetivo y conserva IDs fuera de las features. El EDA explora exclusivamente train. El baseline utiliza las probabilidades previas de entrenamiento y predice la clase mayoritaria. El modelado compara regresión logística sin ponderar y con clases balanceadas, seleccionando por average precision en validación. La evaluación final compara el baseline y el modelo en test, sin ajustar con sus resultados.

## Cómo ejecutar

Desde la carpeta del proyecto elegido (por ejemplo, `Analisis/churn/BankChurn`), prepara Python 3.10 o posterior:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m ipykernel install --user --name churn-portfolio --display-name "Python (Churn)"
.\.venv\Scripts\python.exe -m jupyterlab
```

Abre el proyecto elegido, selecciona ese Python y ejecuta 00. Después guarda y cierra 01–05 y utiliza 06 para ejecutarlos secuencialmente con kernels independientes. También puedes recorrer los notebooks manualmente. Cada proyecto consume su ZIP local de `data/raw`, indicado en su propia configuración. No necesita la carpeta temática ni los originales de back.

## Reportes

Los nombres son estables y se reemplazan al repetir una etapa. Se generan diagnóstico de entorno, preparación, EDA y distribución del objetivo, métricas de baseline y candidatos en validación, evaluación JSON/Markdown y tablas de alertas. El maestro registra tiempos y estado y se detiene ante errores. Los detalles están en [la metodología compartida](docs/metodologia.md).

Los ZIP, datos, modelos, respaldos y copias de fallo se excluyen del versionado. Los reportes y notebooks finales pueden publicarse después de revisar su coherencia y las condiciones de uso de los datos. No se presenta la estructura inicial como modelos ya validados para producción.

Los próximos datasets pueden incorporarse como proyectos adicionales con su propio `config.json`, respetando su definición de objetivo y partición.

## Estado de la preparación inicial

Se comprobaron las funciones de preparación y EDA con los cuatro datasets reales y se generaron sus particiones y reportes. SubscriptionChurn descarta una fila sin objetivo. Los cuatro proyectos contienen 28 notebooks en total; se comprobaron las pruebas del recorrido de modelado/evaluación y del orden de la partición temporal con datos de prueba.

**Los cuatro proyectos completaron 00 y la secuencia 01–05. TelecomChurn completó su ejecución el 7 de octubre de 2026.**

| Proyecto | Accuracy baseline / modelo | ROC-AUC del modelo | Hallazgo principal |
| --- | --- | ---: | --- |
| ActivityChurn | 49,50 % / 77,23 % | 0,8374 | Mejora inicial en 303 registros del test temporal; horizonte y features pendientes de confirmar |
| BankChurn | 79,65 % / 81,00 % | 0,7752 | Recall de churn de 19,41 %: muchos abandonos omitidos |
| SubscriptionChurn | 47,37 % / 58,10 % | 0,6887 | Caída desde validación y muchas falsas alertas; diferencias entre archivos por investigar |
| TelecomChurn | 85,76 % / 85,91 % | 0,8117 | Detecta 28 de 95 abandonos: recall de churn de 29,47 % |

Sus README detallan resultados y alcance. Las métricas corresponden a poblaciones y particiones diferentes y no permiten ordenar los proyectos por calidad de modelo. La ejecución completa no cierra todavía la revisión de procedencia, etiquetado y disponibilidad temporal.

Consulta la [estructura homologada](../../docs/proyectos_tematicos.md) para comandos de terminal y ubicación de las funciones.

## Calibración y políticas — 8 de octubre de 2026

Los cuatro proyectos ejecutaron nuevamente 01–05 y añaden un modelo para decisiones con ajuste y calibración separados. Conservan la comparación original y distinguen el nuevo estimador en su guía local `docs/decisiones.md`. Las probabilidades y políticas se evalúan en test sin reajuste; FN=5 y FP=1 son costes ilustrativos. La calibración puede empeorar y el umbral de validación no garantiza mejor coste de test. [Resumen y comprobaciones](../../docs/ampliacion_analisis_oct08.md).
