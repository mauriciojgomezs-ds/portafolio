# Clasificación visual de prendas
![Python](https://img.shields.io/badge/python-3.10%2B-blue) ![scikit--learn](https://img.shields.io/badge/scikit--learn-1.3%2B-orange) ![estado](https://img.shields.io/badge/estado-completado-brightgreen)

Identificar diez categorías de prendas a partir de imágenes en gris de 28×28 píxeles. El proyecto compara un clasificador lineal con una red neuronal densa y estudia qué clases confunde.

## Recorrido

| Notebook | Resultado |
| --- | --- |
| 00 · Entorno | Dependencias, descarga oficial e integridad de cuatro archivos |
| 01 · Preparación | Lectura IDX, deduplicación, train/valid y test oficial intacto |
| 02 · EDA visual | Distribución de clases, ejemplos e imágenes medias de train |
| 03 · Baseline | Clasificador lineal SGD con pérdida logística |
| 04 · Modelado | MLP de 64 neuronas; selección de regularización en validación |
| 05 · Evaluación | Accuracy, F1 macro, métricas por clase, confusiones y errores visuales |
| 06 · Maestro | Cinco etapas secuenciales con kernels independientes |

Desde esta carpeta, instala `python -m pip install -r requirements.txt`. Abre [00](notebooks/00_configuracion_entorno.ipynb), selecciona ese Python y ejecuta sus tres celdas. Tras comprobar el entorno y recuperar las fuentes, guarda y cierra 01–05 y ejecuta las tres celdas de [06](notebooks/06_ejecucion_completa.ipynb). No requiere GPU ni servicios externos durante entrenamiento.

También puedes usar `python scripts/download_sources.py` y luego `python scripts/execute_notebooks.py`. Para reunir resultados existentes: `python scripts/generate_report.py`.

## Resultados y alcance

La entrada principal es el [informe integral](reports/informe_final/informe_final.md), actualizado por el maestro y las celdas finales de los análisis. Los resultados de cada etapa están en carpetas independientes de `reports/`; las alertas y el resumen de ejecución identifican avisos y pasadas incompletas.

La primera configuración utiliza 12.000 imágenes de train y 3.000 de validación para facilitar una ejecución en CPU, manteniendo las 10.000 imágenes del test oficial. La normalización divide por 255. La MLP usa píxeles aplanados: **no es una CNN**. La muestra y la limpieza de desarrollo impiden presentar las cifras como una reproducción exacta de benchmarks que entrenan con las 60.000 imágenes oficiales. No se ajustan parámetros con test.

Fashion-MNIST no representa fotografías reales de productos o personas. Una ampliación posterior puede incorporar una CNN y evaluar cambios de iluminación, rotación y dominio con un protocolo separado.

## Proyecto independiente

Código en `src/fashion_mnist_classification/`, comandos en `scripts/`, datos propios en `data/raw/`, artefactos locales en `data/processed/`, `models/` y `reports/`. Se puede copiar o renombrar esta carpeta completa sin otros proyectos. Las entradas y modelos no se versionan.

Consulta [metodología](docs/metodologia.md), [fuentes](docs/fuentes.md), [ejecución](docs/ejecucion.md) y [estructura](docs/estructura.md). El dataset se distribuye en el [repositorio oficial de Zalando Research](https://github.com/zalandoresearch/fashion-mnist), bajo su licencia MIT; el código de este proyecto requiere una decisión de licencia propia antes de publicar.

## Primera ejecución comprobada · 7 de octubre de 2026

00 y el maestro completaron los siete notebooks. En el test oficial, el baseline obtuvo accuracy 81.01% y F1 macro 0.8040; la MLP obtuvo 85.18% y 0.8536. Ambos candidatos MLP alcanzaron el máximo de 40 iteraciones sin converger. Los avisos se conservan en la tabla de alertas; no se modificaron parámetros después de observar test.

![Ejemplos de errores de clasificación en Fashion-MNIST](reports/evaluacion/errores_visuales.png)

Consulta el [registro de ejecución](docs/ejecuciones.md) y el informe integral para la evidencia vigente.
