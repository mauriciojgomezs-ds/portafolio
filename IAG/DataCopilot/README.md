# DataCopilot — Copiloto de análisis de datos
![Python](https://img.shields.io/badge/python-3.10%2B-blue) ![OpenAI](https://img.shields.io/badge/OpenAI-conector%20opcional-lightgrey) ![Estado](https://img.shields.io/badge/estado-MVP%20local%20ejecutado-brightgreen) ![Conector IA](https://img.shields.io/badge/conector%20IA-pendiente%20de%20prueba%20real-yellow)

## Contenido
- [Ejecutar](#ejecutar)
- [Datos y resultados de referencia](#datos-y-resultados-de-referencia)
- [Conectar IA](#conectar-ia)
- [Contrato y límites](#contrato-y-límites)
- [Evaluación y siguiente etapa](#evaluación-y-siguiente-etapa)

MVP que responde preguntas descriptivas sobre un CSV mediante operaciones controladas. El código calcula los resultados; un conector opcional de IA traduce la pregunta a un plan permitido, sin generar ni ejecutar código libre.

**Estado:** perfil de calidad, suma, promedio, suma por grupo, faltantes y duplicados implementados. Interpretación local mediante plantillas y conector OpenAI mediante JSON estructurado. La conexión real requiere credenciales y modelo; no está verificada. Predicción, causalidad, filtros arbitrarios y gráficos interactivos están pendientes.

## Ejecutar

Desde esta carpeta, con Python 3.10 o superior; el MVP no requiere dependencias externas:

```powershell
python scripts/analyze.py
python scripts/analyze.py --question "total de ventas"
python scripts/analyze.py --question "promedio de ventas"
python scripts/analyze.py --question "total de ventas por region"
python scripts/analyze.py --question "faltantes"
python scripts/analyze.py --question "duplicados"
python -m unittest discover -s tests -v
```

Puedes seleccionar otro archivo con `--csv` y otra salida con `--output`. El modo local admite estas plantillas y los nombres reales de columnas; preguntas fuera de alcance se rechazan sin inventar cálculos.

## Datos y resultados de referencia

[ventas.csv](examples/ventas.csv) contiene 12 filas ficticias de ventas en CLP, un duplicado completo, una venta faltante y una celda no numérica. El total de ventas con duplicados conservados es **1.680.000**, calculado sobre diez valores válidos. Norte suma 530.000, Sur 840.000 y Centro 310.000. El promedio sobre valores válidos es 168.000.

Las cifras proceden del CSV sintético, no de un modelo ni de datos reales. El [resultado de demostración](reports/demo.md) resume el cálculo; su [JSON complementario](reports/demo.json) conserva perfil, plan, hash del archivo y filas omitidas. Los números de línea incluyen el encabezado. Los duplicados se informan y se conservan en las agregaciones; no hay limpieza silenciosa.

## Conectar IA

Configura `OPENAI_API_KEY` y `OPENAI_MODEL` en el entorno del proceso. Usa un modelo compatible con Responses y salidas estructuradas. No pegues la clave en el chat ni la guardes en el proyecto.

```powershell
python scripts/analyze.py --provider openai --question "¿Cuál es el total de ventas por region?"
```

Solo se envían pregunta y nombres de columnas para proponer el plan. El CSV se procesa localmente. La solicitud consume uso de API y lleva `store=false`; esto no equivale a una garantía de retención cero. El plan se valida antes de ejecutar, pero el modelo puede interpretar mal una pregunta: revisa el plan y la política mostrados.

La implementación sigue la [documentación oficial de salidas estructuradas](https://developers.openai.com/api/docs/guides/structured-outputs?api-mode=responses). La fase siguiente incorporará explicaciones con referencias a métricas calculadas, filtros declarados y gráficos, sin delegar la aritmética al modelo.

## Contrato y límites

CSV UTF-8 separado por comas, con punto decimal y sin separadores de miles. Se usa `Decimal`; no se interpreta automáticamente formato chileno, fechas ni unidades. La muestra es de una sola moneda; un archivo con monedas mezcladas debe separarse o agruparse por moneda antes de agregar. No hay conversión monetaria.

Una cifra agregada no demuestra causalidad ni permite extrapolar a ventas futuras. Los valores inválidos y faltantes quedan identificados; no se imputan. Cada proyecto es independiente y puede copiarse sin los otros asistentes.

## Evaluación y siguiente etapa

Comparar planes con una referencia revisada: operación, columna, agrupación y rechazo correcto de preguntas no admitidas. Verificar resultados numéricos contra cálculos independientes, registrar omisiones y errores de interpretación. Incorporar luego casos nuevos, columnas renombradas, diferentes formatos y preguntas ambiguas en un conjunto separado del desarrollo.

Este MVP no es un analista general de cualquier CSV. Los primeros casos probados son operaciones descriptivas concretas; el conector real sigue pendiente de credenciales.
