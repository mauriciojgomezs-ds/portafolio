# Guía de uso

Ejecuta los ejemplos desde la carpeta del proyecto, después de instalar los requisitos e inicializar la base como indica el [README](../README.md). Las consultas web son ejemplos de uso; no representan ejecuciones verificadas contra los sitios.

## Comandos disponibles

Prefijo común: `.\.venv\Scripts\python.exe app/main.py`. Puedes agregar `--db data/demo.sqlite` antes del subcomando para separar una demostración de la base habitual. Inicializa cada base nueva con `init`.

| Comando | Argumentos principales | Efecto |
| --- | --- | --- |
| `init` | Sin argumentos obligatorios | Crea el esquema si falta y aplica la migración ligera de `source_tag`. No vacía una base existente. |
| `source-add` | `--tag`, `--url`; opcionales `--include`, `--exclude`, `--notes` | Registra o actualiza un origen. No descarga páginas. |
| `source-list` | Sin argumentos obligatorios | Lista orígenes registrados. |
| `ingest-url` | URL; opcional `--tag` | Descarga y almacena una página. |
| `ingest-file` | Ruta de archivo; opcional `--tag` | Lee una lista UTF-8 de URLs y descarga cada una. No ingiere el contenido del archivo como documento. |
| `crawl` | Una o más URLs o listas; opcionales `--tag`, `--depth`, `--max-pages`, `--delay`, `--include`, `--exclude` | Sigue enlaces internos desde semillas. |
| `ask` | Pregunta; opcionales `--tag`, `--limit` | Consulta documentos locales y construye una respuesta. |
| `ask-live` | Pregunta; parámetros de búsqueda y rastreo | Descubre URLs, ingiere páginas y consulta la base actualizada. |
| `validate` | `--question`, `--answer`; opcionales `--sources`, `--notes`, `--successful-query` | Guarda una respuesta marcada manualmente como validada. |
| `mark-error` | `--question`, `--reason`; opcionales `--bad-answer`, `--better-query` | Registra un error y una posible búsqueda alternativa. |
| `check-changes` | Sin argumentos obligatorios | Descarga de nuevo todas las URLs guardadas y compara hashes. |
| `stats` | Sin argumentos obligatorios | Cuenta documentos, versiones, respuestas validadas, errores, estrategias y cambios. No mide calidad. |

Todos aceptan `--timing` después del subcomando. Para consultar la ayuda exacta:

```powershell
.\.venv\Scripts\python.exe app/main.py --help
.\.venv\Scripts\python.exe app/main.py ask-live --help
```

## Fuentes configuradas

```powershell
.\.venv\Scripts\python.exe app/main.py source-add --tag mslearn --url "https://learn.microsoft.com/" --include "/en-us/azure/"
.\.venv\Scripts\python.exe app/main.py source-add --tag aws --url "https://docs.aws.amazon.com/" --include "/lambda/"
.\.venv\Scripts\python.exe app/main.py source-list
```

Usa un tag descriptivo para cualquier sitio, por ejemplo `docs`. Los conectores opcionales `mslearn` y `aws` deben corresponder a sus sitios: algunas reglas dependen del tag. Cambiar el sitio de un tag existente no elimina ni vuelve a etiquetar sus documentos. Actualizar un origen con `source-add` reemplaza también sus filtros y notas por los valores suministrados o los valores vacíos predeterminados.

Los filtros son coincidencias de texto en URLs, no expresiones regulares. En `ask-live`, `--include` toma el valor registrado si se omite. `--exclude` tiene un valor vacío predeterminado que evita heredar el filtro registrado; pásalo explícitamente cuando lo necesites. Las URLs obligatorias por tema se agregan aparte, por lo que los filtros no constituyen una restricción uniforme de toda la ingesta.

## Consulta con descubrimiento

```powershell
.\.venv\Scripts\python.exe app/main.py ask-live "Como crear un Azure Function en Python" --tag mslearn --depth 1 --max-pages 8 --verbose --timing
.\.venv\Scripts\python.exe app/main.py ask-live "Como crear un cluster en Databricks" --tag mslearn --depth 1 --max-pages 8 --verbose --timing
.\.venv\Scripts\python.exe app/main.py ask-live "Como crear una Lambda en Python" --tag aws --depth 1 --max-pages 8 --verbose --timing
```

| Parámetro de `ask-live` | Predeterminado | Interpretación real |
| --- | --- | --- |
| `--search-limit` | 6 | Objetivo de candidatas en discovery; las URLs obligatorias agregadas después pueden superar este número. |
| `--max-pages` | 12 | Límite de páginas guardadas con éxito, no de intentos ni de tiempo total. |
| `--depth` | 1 | Profundidad de enlaces relacionados; 0 ingiere solo candidatas primarias. |
| `--related-per-page` | 8 | Máximo de enlaces encolados por página después del ranking. |
| `--min-link-score` | 2.0 | Umbral heurístico para seguir un enlace. |
| `--limit` | 5 | En el contexto por URLs se usa al menos 8; fuentes obligatorias pueden ampliar el resultado. No es un máximo estricto final. |
| `--delay` | 0.3 segundos | Pausa después de enlaces relacionados guardados; no se aplica a toda la ingesta primaria. |
| `--verbose` | Desactivado | Muestra candidatas y errores de scraping; no expone todos los fallos internos del buscador. |
| `--discover` | Desactivado | Se acepta por compatibilidad, pero el código actual no consulta esta bandera: `ask-live` descubre URLs con o sin ella. |

`ask-live` requiere indicar un origen mediante `--tag`; si se omite o no está registrado, termina antes de consultar la web.

## Ingesta desde URLs conocidas

Permite cargar documentación sin depender del descubrimiento del buscador:

```powershell
.\.venv\Scripts\python.exe app/main.py ingest-file examples/source_urls.txt --tag docs
.\.venv\Scripts\python.exe app/main.py crawl examples/related_urls.txt --tag docs --include "/3/" --depth 1 --max-pages 8 --delay 0.5
```

Los archivos contienen una URL por línea; se omiten líneas vacías y comentarios que empiezan con `#` en la primera columna. `crawl` restringe todas las semillas al dominio de la primera URL y usa los filtros del comando; no hereda los filtros del origen registrado. `ingest-url` e `ingest-file` tampoco aplican esos filtros. El tag de estos comandos etiqueta documentos y no exige un origen registrado.

## Leer y revisar una respuesta

Las guías conocidas contienen pasos escritos en el código. Las frases de evidencia provienen de documentos, pero no se vinculan individualmente a cada paso. La checklist `ENCONTRADA` / `FALTA/NO CONFIRMADA` se basa en términos presentes en título, URL y texto, no en una revisión semántica.

Una respuesta validada similar tiene prioridad y puede devolver su texto sin la guía ni la checklist. Las respuestas validadas y los errores no se filtran por tag. Antes de reutilizar una respuesta, comprueba que corresponde a la pregunta, al producto y a la versión documental.

## Retroalimentación manual

Ejemplo de error observado por quien revisa:

```powershell
.\.venv\Scripts\python.exe app/main.py mark-error --question "Como crear un entorno virtual en Python" --reason "La respuesta omitió un prerrequisito confirmado en la documentación" --better-query "python virtual environment prerequisites"
```

Para `validate`, suministra una respuesta completa ya revisada y sus fuentes mediante `--question`, `--answer` y `--sources`. El sistema no comprueba que esa revisión ocurrió. `--successful-query` guarda una estrategia exitosa; `--better-query` registra una alternativa en un caso de error. Estas estrategias no se usan automáticamente para entrenar o modificar discovery.

## Revisar cambios

```powershell
.\.venv\Scripts\python.exe app/main.py check-changes --timing
```

`CAMBIÓ` significa que cambió el hash del texto extraído, no que se haya identificado el significado del cambio. Se conservan versiones previas y permanecen en el índice de búsqueda. Consulta [las limitaciones](limitaciones.md) antes de usarlo como garantía de vigencia.

Para resguardar la base, termina los procesos que la usan y copia `data` a una ubicación de respaldo. SQLite usa WAL; evita copiar únicamente `kb.sqlite` durante una escritura activa.
