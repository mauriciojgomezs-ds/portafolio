# Vitrina Grupo 4 — IAG (presentación visual de los 6 README)

## Resumen

Se verificó primero que ninguno de los 6 proyectos de `IAG/` tiene notebooks ni un framework tipo `informe.py` que lea el primer párrafo del README automáticamente (`grep -rln "README.md" */scripts */app` no devolvió resultados). Por seguridad se mantuvo igualmente la convención: toda línea de badges se insertó inmediatamente debajo del título `#`, en un solo salto de línea, sin línea en blanco antes del párrafo de badges.

En los 5 READMEs con 5 o más secciones `##` (DataCopilot, DocumentAnalyzer, MeetingCopilot, PortfolioDemo, knowledge_base_mvp) se agregó una tabla de contenidos corta (`## Contenido`) con anclajes a cada sección existente, justo debajo de los badges. El README índice (`IAG/README.md`) no tiene secciones `##`, por lo que no se le agregó TOC.

Se detectaron imágenes reales referenciables (no solo .md de texto): `PortfolioDemo/docs/capturas/datos.jpg` (captura real de la demo, ya enlazada en `docs/demostracion.md`) y `DocumentAnalyzer/examples/factura_imagen.png` (imagen sintética de prueba para OCR, ya enlazada como archivo). Ambas se incorporaron como imagen embebida (`![...]`) además del enlace de texto ya existente, sin eliminar el enlace original.

Los badges de estado se redactaron citando literalmente lo que cada README ya afirma (por ejemplo "MVP local ejecutado", "conector implementado", "sin llamadas reales", "sin prueba real"), sin inventar cifras ni cambiar ninguna afirmación, número o limitación existente. No se modificó ni eliminó texto previamente auditado; solo se añadieron líneas nuevas (badges, TOC, imágenes).

Las dependencias usadas para armar badges de stack se tomaron de archivos reales del repositorio: `DocumentAnalyzer/requirements-conversion.txt` (MarkItDown) y `requirements-ocr.txt` (PaddleOCR), y `knowledge_base_mvp/requirements.txt` (beautifulsoup4, además de SQLite mencionado explícitamente en el texto). DataCopilot, MeetingCopilot y PortfolioDemo no tienen `requirements.txt` ni `pyproject.toml`: sus badges de stack se basaron en lo que el propio README declara (Python 3.10+, conector OpenAI opcional, `http.server` de la librería estándar).

## Tabla de cambios

| Ruta | Archivo | Línea | Original | Propuesta |
| --- | --- | --- | --- | --- |
| `IAG/` | README.md | 2 (nueva) | *(no existía)* | `![Python](...) ![Proyectos](...-4-blue) ![Estado](...-MVPs%20con%20evidencia%20verificable-yellow)` — badges insertados debajo de `# IA generativa aplicada` |
| `IAG/DataCopilot/` | README.md | 2 (nueva) | *(no existía)* | `![Python](...3.10%2B...) ![OpenAI](...conector%20opcional...) ![Estado](...MVP%20local%20ejecutado...) ![Conector IA](...pendiente%20de%20prueba%20real...)` |
| `IAG/DataCopilot/` | README.md | 4-9 (nuevas) | *(no existía)* | `## Contenido` + lista con anclajes a Ejecutar, Datos y resultados de referencia, Conectar IA, Contrato y límites, Evaluación y siguiente etapa |
| `IAG/DocumentAnalyzer/` | README.md | 2 (nueva) | *(no existía)* | `![Python](...) ![MarkItDown](...conversión%20opcional...) ![PaddleOCR](...OCR%20opcional...) ![Estado](...MVP%20de%20texto%20ejecutado...) ![Adaptadores](...sin%20prueba%20real...)` |
| `IAG/DocumentAnalyzer/` | README.md | 4-10 (nuevas) | *(no existía)* | `## Contenido` + 6 anclajes (Demostración local … Evaluación prevista) |
| `IAG/DocumentAnalyzer/` | README.md | tras línea "...es una imagen sintética para probar OCR." | *(solo enlace de texto)* | se agregó `![Factura sintética usada como entrada de prueba para OCR](examples/factura_imagen.png)` como imagen embebida, en línea nueva, sin tocar el enlace ni el texto original |
| `IAG/MeetingCopilot/` | README.md | 2 (nueva) | *(no existía)* | `![Python](...) ![OpenAI](...conector%20implementado...) ![Estado](...sin%20llamadas%20reales...)` |
| `IAG/MeetingCopilot/` | README.md | 4-9 (nuevas) | *(no existía)* | `## Contenido` + 5 anclajes (Probar el caso … Documentación) |
| `IAG/PortfolioDemo/` | README.md | 2 (nueva) | *(no existía)* | `![Python](...) ![Interfaz](...local%20%28http.server%29...) ![Estado](...demo%20local%20funcional...)` |
| `IAG/PortfolioDemo/` | README.md | 4-9 (nuevas) | *(no existía)* | `## Contenido` + 5 anclajes (Ejecutar … Verificación) |
| `IAG/PortfolioDemo/` | README.md | tras "Consulta la [demostración con capturas y resultados]..." | *(solo enlace de texto a demostracion.md)* | se agregó `![Consulta de ventas con resultados calculados y política de calidad](docs/capturas/datos.jpg)` como captura real embebida |
| `IAG/knowledge_base_mvp/` | README.md | 2 (nueva) | *(no existía)* | `![Python](...) ![SQLite](...FTS5...) ![BeautifulSoup](...scraping...) ![Estado](...MVP%20de%20consola...) ![LLM](...no%20conectado...)` |
| `IAG/knowledge_base_mvp/` | README.md | 4-10 (nuevas) | *(no existía)* | `## Contenido` + 6 anclajes (Problema que aborda … IA y análisis en el portafolio) |

Nota: en todos los casos la línea del título `#` y la línea de badges quedaron contiguas (sin línea en blanco entre ambas), tal como exige la convención del portafolio. No se modificó, reordenó ni eliminó ningún párrafo, cifra, afirmación o limitación del contenido ya auditado; todos los cambios son adiciones.
