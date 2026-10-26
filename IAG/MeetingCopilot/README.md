# MeetingCopilot — Copiloto de reuniones
![Python](https://img.shields.io/badge/python-3.10%2B-blue) ![OpenAI](https://img.shields.io/badge/OpenAI-conector%20implementado-yellow) ![Estado](https://img.shields.io/badge/estado-sin%20llamadas%20reales-yellow)

## Contenido
- [Probar el caso](#probar-el-caso)
- [Preguntar sobre la reunión](#preguntar-sobre-la-reunión)
- [Material de prueba](#material-de-prueba)
- [Qué mostraría el producto](#qué-mostraría-el-producto)
- [Documentación](#documentación)

Proyecto para consultar una reunión mediante preguntas, extraer decisiones y tareas y comparar lo conversado con objetivos definidos antes de la reunión.

**Estado actual:** agenda y transcripción sintéticas, cálculo de indicadores desde una revisión explícita, búsqueda local de fragmentos y conector de preguntas con IA y citas. El conector utiliza OpenAI Responses con modelo configurable; se probó con respuestas simuladas, sin realizar llamadas reales porque no hay credenciales configuradas. La transcripción de audio, recuperación semántica y evaluación automática de agenda siguen pendientes. Los resultados de `demo.py` proceden de anotaciones de referencia, no de predicciones de IA.

## Probar el caso

Desde esta carpeta, con Python 3.10 o superior y sin dependencias externas:

```powershell
python scripts/demo.py
python -m unittest discover -s tests -v
```

El primer comando comprueba agenda, transcripción, referencias de evidencia y revisión; genera `reports/demo.json` y `reports/demo.md`. No consulta servicios externos ni usa la base del asistente documental.

## Preguntar sobre la reunión

```powershell
python scripts/ask.py "¿Cuál fue el presupuesto final aprobado?"
```

Esto muestra fragmentos candidatos con hablante y tiempo, sin generar una respuesta. Para activar respuestas de IA con citas, configura la clave y el modelo siguiendo la [guía de preguntas](docs/preguntas.md) y utiliza `--provider openai`. Puedes cargar otra transcripción mediante `--transcript` y contexto previo mediante `--agenda`.

## Material de prueba

| Archivo | Uso |
| --- | --- |
| [Agenda y contexto](examples/agenda.md) | Objetivos, pesos y criterios de aceptación definidos de antemano. |
| [Transcripción](examples/transcripcion.md) | Reunión ficticia en español con hablantes y tiempos simulados. |
| `examples/agenda.json` | Agenda estructurada para cálculo. |
| `examples/transcript.json` | Intervenciones con identificadores y marcas de tiempo. |
| `examples/reference_review.json` | Evaluación de referencia, con estado, explicación y citas. |
| [Preguntas de prueba](examples/preguntas.md) | Consultas, respuesta esperada, evidencia y condiciones de abstención. |
| `examples/reference_qa.json` | Las mismas preguntas en formato estructurado. |

Los nombres, cifras, tiempos y diálogos son inventados. No existe una grabación asociada. Este caso sirve para desarrollo y regresiones; no es un conjunto de evaluación independiente ni prueba de precisión de un modelo.

## Qué mostraría el producto

1. Cargar agenda, criterios y documentos de contexto.
2. Cargar una transcripción o, en una fase posterior, audio/video.
3. Consultar acuerdos y temas con citas a intervenciones y tiempos.
4. Revisar por objetivo qué se trató, qué se alcanzó y qué quedó pendiente.
5. Corregir la evaluación propuesta y recalcular los indicadores con registro de la revisión.

Una decisión tomada después puede reemplazar una propuesta anterior. Acordar una tarea no demuestra que se haya ejecutado. Una sección ausente de la transcripción puede hacer que un objetivo sea no evaluable.

## Documentación

- [Ruta de implementación y arquitectura](docs/implementacion.md).
- [Preguntas locales y conexión con IA](docs/preguntas.md).
- [Rúbrica, fórmulas y evaluación del modelo](docs/evaluacion.md).
- [Resultado de demostración](reports/demo.md).

El primer MVP utilizará texto y agenda. La incorporación de audio y documentos se hará después de comprobar las respuestas con evidencia y el cálculo de cumplimiento. El proyecto tiene estructura propia, independiente de los notebooks del portafolio.
