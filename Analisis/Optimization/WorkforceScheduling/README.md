# Optimización de turnos y cobertura
![Python](https://img.shields.io/badge/python-3.10%2B-blue) ![scipy](https://img.shields.io/badge/scipy-1.10%2B-orange) ![estado](https://img.shields.io/badge/estado-completado-brightgreen)

Asignar turnos y pausas para cubrir requisitos semanales al menor coste, respetando disponibilidad, horas máximas y días consecutivos en un escenario sintético.

Proyecto independiente de `Optimization`, con notebooks por etapa, comentarios calculados, alertas tabuladas y un informe integral automático.

## Fuente y protocolo

Escenario **sintético didáctico**, creado localmente por `setup()` sin acceso externo. Demanda exógena en data/raw/demand.csv; empleados ficticios en data/raw/employees.csv; procedencia y reglas de generación en data/raw/scenario_origin.json. El perfil es fijo y no utiliza un generador aleatorio. Costes en unidades monetarias arbitrarias, sin salarios ni información personal reales.

Consulta la [metodología](docs/metodologia.md) para interpretar el resultado y la [guía de fuentes](docs/fuentes.md) para recuperar entradas. No hay entrenamiento predictivo; la evaluación audita cobertura, restricciones y escenarios.

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
| 03_baseline | Heurística de asignación |
| 04_modelado | Optimización entera de turnos |
| 05_evaluacion | Auditoría de restricciones y estrés de demanda |

![Distribución de demanda y disponibilidad analizada en el EDA](reports/eda/eda.png)

Desde terminal, con el mismo entorno: `python scripts/execute_notebooks.py`. Para los controles locales: `python -m unittest discover -s tests -v`.

## Resultados

- [Verificación de autonomía](docs/verificacion.json): cinco etapas recalculadas en copia independiente y tests locales.
- [Informe integral](reports/informe_final/informe_final.md): entrada principal a resultados y conclusiones.
- `reports/ejecucion/resumen.json`: estado y tiempos de las cinco etapas.
- `reports/alertas`: avisos originales agrupados y explicados.
- `reports/preparacion`, `eda`, `baseline`, `modelado`, `evaluacion`: cifras, comentarios y evidencia por etapa.
- `reports/evaluacion/`: turnos_programados.csv, cobertura_por_intervalo.csv y horas_por_empleado.csv.

Para reunir reportes guardados sin repetir el análisis, utiliza `python scripts/generate_report.py`. La [guía del informe](docs/informe_final.md) explica estados y actualización. Reejecutar conserva una única versión vigente; las cifras de una primera revisión son históricas.

## Autonomía y límites

El proyecto conserva `src/workforce_scheduling`, scripts, tests, configuración, fuentes y modelos propios. Puedes copiar o renombrar esta carpeta con sus datos locales, instalarla y ejecutarla sin los demás proyectos. Para otra máquina, crea un entorno nuevo y recupera las fuentes según la guía local.

Escenario sintético con requisitos exógenos y costes arbitrarios. No predice llamadas, calcula Erlang C o mide SLA. Optimalidad limitada a patrones y tolerancia; las restricciones didácticas no acreditan legislación laboral ni preferencias observadas de empleados.

## Equilibrio y preferencias

04 añade un escenario con equilibrio de horas y preferencias sintéticas, limitado a un 10 % más de coste que el plan de referencia. 05 compara ambos planes factibles y exporta horas, preferencias incumplidas y costes. [Protocolo del escenario alternativo](docs/equilibrio.md).
