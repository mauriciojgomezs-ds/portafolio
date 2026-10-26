# Knowledge Base MVP — Asistente de investigación documental
![Python](https://img.shields.io/badge/python-3.10%2B-blue) ![SQLite](https://img.shields.io/badge/SQLite-FTS5-003B57) ![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-scraping-lightgrey) ![Estado](https://img.shields.io/badge/estado-MVP%20de%20consola-brightgreen) ![LLM](https://img.shields.io/badge/LLM-no%20conectado-yellow)

## Contenido
- [Problema que aborda](#problema-que-aborda)
- [Documentación](#documentación)
- [Instalación](#instalación)
- [Primer uso](#primer-uso)
- [Estructura](#estructura)
- [IA y análisis en el portafolio](#ia-y-análisis-en-el-portafolio)

MVP local en Python para consultar documentación técnica desde sitios configurados, reunir fuentes y construir respuestas orientativas. Combina ingesta de datos web, búsqueda textual, ranking por reglas y análisis heurístico de cobertura.

**Estado:** aplicación de consola con recuperación documental y respuestas por reglas. No tiene un modelo de lenguaje conectado, embeddings ni entrenamiento automático. La integración con IA generativa es una evolución propuesta; todavía no se han publicado métricas de calidad.

## Problema que aborda

Responder una pregunta técnica puede exigir revisar varias páginas y ordenar requisitos, configuración y pruebas. El proyecto reúne documentos en una base local y selecciona información relacionada con la pregunta. Para temas conocidos incluye guías predefinidas; para otros extrae frases relevantes.

Por ejemplo, permite explorar preguntas sobre seguimiento web, reglas de acción o campañas de contacto, Azure Functions, compute de Databricks y AWS Lambda. Estos son ejemplos de temas con reglas en el código, no procedimientos certificados ni resultados de una evaluación.

## Documentación

| Documento | Contenido |
| --- | --- |
| [Ficha de portafolio](docs/portafolio.md) | Problema, valor, alcance actual y relación entre IA y análisis. |
| [Guía de uso](docs/guia_uso.md) | Comandos, parámetros, ejemplos e interpretación de resultados. |
| [Arquitectura](docs/arquitectura.md) | Flujo, módulos, almacenamiento y decisiones de implementación. |
| [Limitaciones y diagnóstico](docs/limitaciones.md) | Comportamientos actuales, errores frecuentes y mejoras necesarias. |
| [Evaluación y evolución hacia IA](docs/evaluacion_ia.md) | Protocolo de comparación, métricas y criterios de avance. |
| [Verificación local](docs/verificacion.md) | Comprobaciones realizadas y alcance de la evidencia. |
| [Historial](docs/historial.md) | Resumen de la evolución y de la generalización de componentes. |

## Instalación

Requiere Python 3.10 o superior por la sintaxis del código y una distribución de SQLite con FTS5. La verificación local se realizó con Python 3.12.10; no se comprobó una matriz de versiones. Los comandos siguientes se ejecutan en PowerShell desde esta carpeta.

```powershell
Set-Location D:\portafolio\IAG\knowledge_base_mvp
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app/main.py init
```

Si copias el proyecto a otra ubicación, ajusta la primera ruta. No es necesario activar el entorno: los ejemplos invocan directamente su intérprete. La instalación de dependencias y las consultas web requieren conexión; las consultas sobre una base ya cargada son locales.

## Primer uso

Registrar una fuente no descarga documentos. Este ejemplo registra un sitio de documentación y luego busca e ingiere información para una pregunta:

```powershell
.\.venv\Scripts\python.exe app/main.py source-add --tag docs --url "https://docs.python.org/3/" --include "/3/"
.\.venv\Scripts\python.exe app/main.py ask-live "Como crear un entorno virtual en Python" --tag docs --depth 1 --max-pages 8 --verbose --timing
```

Para consultar posteriormente los documentos guardados:

```powershell
.\.venv\Scripts\python.exe app/main.py ask "Como crear un entorno virtual en Python" --tag docs --timing
.\.venv\Scripts\python.exe app/main.py stats
```

La respuesta puede mostrar una guía, frases extraídas, checklist y URLs candidatas. Revisa las páginas originales: mostrar una fuente no garantiza que sostenga cada paso. Si no hay documentos y tampoco una respuesta validada similar, el sistema informa que falta información local.

## Estructura

```text
knowledge_base_mvp/
├── app/
│   ├── main.py             # Comandos y coordinación
│   ├── db.py               # Esquema y conexión SQLite
│   ├── scraper.py          # Extracción de HTML y enlaces
│   ├── live_discovery.py   # Descubrimiento de URLs y reglas de fuentes
│   ├── retrieval.py        # Recuperación, ranking y respuestas
│   └── models.py           # Reservado; sin entidades implementadas
├── examples/               # Listas de URLs semilla
├── docs/                   # Documentación del proyecto
├── tests/                  # Pruebas del uso de fuentes genéricas
├── data/                   # Base local creada durante el uso
├── requirements.txt
└── README.md
```

La base predeterminada es `data/kb.sqlite`, resuelta respecto a la ubicación del proyecto. Para una base diferente, coloca la opción global antes del comando:

```powershell
.\.venv\Scripts\python.exe app/main.py --db data/demo.sqlite init
```

`ask-live` requiere un `--tag` registrado; no selecciona un proveedor implícitamente. Puedes configurar cualquier sitio compatible con extracción HTML. Los conectores específicos de documentación siguen siendo opcionales.

Para verificar el comportamiento de las fuentes y las guías genéricas sin consultar la web:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## IA y análisis en el portafolio

El MVP sirve como referencia medible para una futura solución de generación apoyada en recuperación (RAG): un modelo redactaría respuestas desde fragmentos documentales con citas. El análisis debe comprobar si esa versión recupera mejores fuentes, cubre los pasos necesarios y reconoce la falta de evidencia, considerando tiempo y costo. El [protocolo propuesto](docs/evaluacion_ia.md) detalla esa comparación.

Ubicado en `IAG/knowledge_base_mvp`, el proyecto tiene un flujo propio de consola; no utiliza los notebooks ni el maestro 06 de los otros proyectos del portafolio. No requiere claves de un proveedor de IA en su implementación actual.
