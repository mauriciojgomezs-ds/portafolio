# Regresión de potencia eléctrica
![Python](https://img.shields.io/badge/python-3.10%2B-blue) ![scikit--learn](https://img.shields.io/badge/scikit--learn-1.3%2B-orange) ![estado](https://img.shields.io/badge/estado-completado-brightgreen)

Predecir la potencia eléctrica de una central a partir de sus condiciones contemporáneas, con selección del modelo e intervalos de predicción calibrados por separado.

Proyecto independiente de `Regression`, con notebooks por etapa, comentarios calculados, alertas tabuladas y un informe integral automático.

## Fuente y protocolo

[Combined Cycle Power Plant, UCI](https://archive.ics.uci.edu/dataset/294/combined+cycle+power+plant). Atribución: P. Tüfekci y H. Kaya, 2014, DOI 10.24432/C5002N. La ficha publica CC BY 4.0. ZIP original en data/raw/CCPP.zip; se conserva el Excel completo pero el análisis utiliza solo su primera hoja, porque las cinco son reordenamientos del mismo conjunto.

Consulta la [metodología](docs/metodologia.md) para interpretar el resultado y la [guía de fuentes](docs/fuentes.md) para recuperar entradas. La calibración de intervalos es independiente de la selección del modelo y de test.

## Ejecutar

Desde esta carpeta, crea un entorno con Python 3.10 o superior e instala requisitos:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
```

Selecciona ese Python como kernel. Ejecuta [00_configuracion_entorno](notebooks/00_configuracion_entorno.ipynb) y después las tres celdas de [06_ejecucion_completa](notebooks/06_ejecucion_completa.ipynb). Si 00 instala bibliotecas, reinicia el kernel y repite 00. Guarda y cierra 01–05 antes del maestro; un error detiene la secuencia.

| Notebook | Función |
| --- | --- |
| 01_preparacion_datos | Fuentes, controles y preparación |
| 02_analisis_exploratorio | Distribuciones y diagnósticos |
| 03_baseline | Media de train como referencia |
| 04_modelado | Selección en validación y calibración separada |
| 05_evaluacion | Test, residuos y cobertura de intervalos |

![Distribuciones de condiciones de planta analizadas en el EDA](reports/eda/eda.png)

Desde terminal, con el mismo entorno: `python scripts/execute_notebooks.py`. Para los controles locales: `python -m unittest discover -s tests -v`.

## Resultados

- [Verificación de autonomía](docs/verificacion.json): cinco etapas recalculadas en copia independiente y tests locales.
- [Informe integral](reports/informe_final/informe_final.md): entrada principal a resultados y conclusiones.
- `reports/ejecucion/resumen.json`: estado y tiempos de las cinco etapas.
- `reports/alertas`: avisos originales agrupados y explicados.
- `reports/preparacion`, `eda`, `baseline`, `modelado`, `evaluacion`: cifras, comentarios y evidencia por etapa.
- `reports/evaluacion/`: metricas_test.csv y predicciones con intervalos.

Para reunir reportes guardados sin repetir el análisis, utiliza `python scripts/generate_report.py`. La [guía del informe](docs/informe_final.md) explica estados y actualización. Reejecutar conserva una única versión vigente; las cifras de una primera revisión son históricas.

## Autonomía y límites

El proyecto conserva `src/power_plant_regression`, scripts, tests, configuración, fuentes y modelos propios. Puedes copiar o renombrar esta carpeta con sus datos locales, instalarla y ejecutarla sin los demás proyectos. Para otra máquina, crea un entorno nuevo y recupera las fuentes según la guía local.

Regresión contemporánea en una central a plena carga. No es pronóstico temporal ni evaluación entre plantas. Los intervalos conformales suponen intercambiabilidad y su cobertura marginal no garantiza cobertura por grupo o periodo.
