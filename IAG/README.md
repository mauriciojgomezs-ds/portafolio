# IA generativa aplicada
![Python](https://img.shields.io/badge/python-3.10%2B-blue) ![Proyectos](https://img.shields.io/badge/proyectos-4-blue) ![Estado](https://img.shields.io/badge/estado-MVPs%20con%20evidencia%20verificable-yellow)

Asistentes y prototipos orientados a IA generativa aplicada, con evidencia, cálculos verificables y evaluación de calidad. Cada README distingue las capacidades implementadas de las propuestas y pruebas pendientes.

| Proyecto | Alcance | Estado |
| --- | --- | --- |
| [Knowledge Base MVP](knowledge_base_mvp/README.md) | Consulta de documentación técnica, búsqueda léxica y respuestas por reglas | MVP de consola; integración con IA generativa propuesta, sin modelo de lenguaje conectado. |
| [MeetingCopilot](MeetingCopilot/README.md) | Preguntas sobre reuniones, acuerdos y cumplimiento de agenda | Búsqueda local y conector de IA implementados; llamadas reales pendientes. Cálculo de agenda desde revisión explícita. |
| [DataCopilot](DataCopilot/README.md) | Preguntas sobre CSV con cálculos controlados y perfil de calidad | MVP local ejecutado; conector de interpretación de preguntas con IA pendiente de prueba real. |
| [DocumentAnalyzer](DocumentAnalyzer/README.md) | Markdown, campos con evidencia y validación de importes | MVP de texto ejecutado; adaptadores MarkItDown/OCR y extracción generativa pendientes de prueba real. |

El porcentaje de cumplimiento de una agenda y la calidad del modelo son indicadores distintos. Cada proyecto debe publicar su protocolo y el origen de sus resultados.

El [Laboratorio de copilotos](PortfolioDemo/README.md) reúne los tres asistentes —DataCopilot, DocumentAnalyzer (como copiloto documental) y MeetingCopilot— en una interfaz local. Incluye una [demostración con capturas reales](PortfolioDemo/docs/demostracion.md) y resultados reproducibles; las pruebas actuales usan el modo local.

Cada proyecto conserva su instalación, datos y flujo de ejecución propios. Knowledge Base MVP utiliza Python y SQLite; MeetingCopilot documenta sus comandos y configuración de proveedor. Consulta la [organización del portafolio](../docs/organizacion_portafolio.md) y los [análisis por notebooks](../Analisis/README.md).
