# Limitaciones y diagnóstico

Estas observaciones provienen de la revisión del código actual. No indican que se haya medido su frecuencia en consultas reales.

## Límites que afectan la calidad

- **Pasos predefinidos:** las guías de temas conocidos no se generan a partir de cada conjunto de documentos. Pueden contener pasos sin respaldo en las fuentes recuperadas.
- **Versiones antiguas:** cada cambio agrega otra fila FTS; las búsquedas no restringen sistemáticamente a la versión actual ni deduplican URLs.
- **Contexto compartido:** las respuestas validadas y los errores se buscan sin tag. Una coincidencia léxica puede recuperar feedback de otro origen. En discovery existe además fallback a documentos locales y adición de fuentes obligatorias guardadas.
- **Cobertura heurística:** una coincidencia de términos en la checklist no demuestra que una página cubra el requisito ni que el procedimiento sea correcto.
- **Idioma y truncamiento:** las reglas mezclan vocabulario español e inglés y solo inspeccionan partes del texto para ranking y extractos. Paráfrasis y evidencia al final de una página pueden quedar fuera.
- **Sin aprendizaje automático:** registrar errores o estrategias no entrena un modelo ni actualiza automáticamente las reglas de búsqueda.

## Límites de operación

`--discover` se analiza como argumento pero no cambia el flujo. `--limit` y `--search-limit` no son máximos estrictos de fuentes finales. `--max-pages` cuenta ingestas exitosas y no fija un límite global de tiempo o intentos.

Los filtros del origen no se aplican de forma uniforme: `crawl` usa los del comando; la ingesta directa no los usa; en `ask-live` el valor predeterminado de `--exclude` impide heredar el registrado y las fuentes obligatorias se agregan aparte. Los tags de conectores deben corresponder a sus sitios, ya que algunas semillas dependen del tag y no se validan siempre contra el dominio configurado.

El scraper no ejecuta JavaScript, no autentica sesiones ni valida estrictamente que el contenido recibido sea HTML. La búsqueda pública puede bloquear peticiones o cambiar su formato. Algunos errores de discovery se silencian. La aplicación no tiene reintentos generales, una API de servicio, interfaz web, control multiusuario ni evaluador automatizado de calidad.

El código no comprueba automáticamente `robots.txt` ni términos de uso. Antes de ejecutar ingestas amplias, verifica las condiciones del sitio y usa límites y pausas adecuados; la pausa de `ask-live` no cubre todas las peticiones.

## Diagnóstico de problemas frecuentes

| Síntoma | Causa posible | Acción |
| --- | --- | --- |
| `ModuleNotFoundError` | Otro intérprete o dependencias ausentes | Usa el Python de `.venv` e instala `requirements.txt` con ese mismo intérprete. |
| `no such table` | Base nueva sin inicializar o ruta distinta | Ejecuta `init` con el mismo `--db` que usarás para consultar. |
| `no such module: fts5` | SQLite sin FTS5 | Usa una distribución de Python/SQLite con ese módulo. |
| Tag inexistente en `ask-live` | Origen no registrado en esa base | Revisa `source-list` y registra el origen con el mismo `--db`. |
| No hay fuentes nuevas | Buscador sin resultados, filtros demasiado estrechos o fallos web | Revisa `--verbose`; intenta `ingest-url` o una lista de URLs conocidas. |
| Texto vacío o incompleto | Página dependiente de JavaScript o estructura HTML distinta | Revisa el HTML y la página original; el MVP no renderiza un navegador. |
| Fuentes de un tema anterior | Fallback, feedback global o versiones históricas | Revisa fuentes, tags y fechas; una base separada por demostración reduce mezclas. |
| URLs repetidas | Varias versiones indexadas | Revisa `document_versions`; falta indexación exclusiva de la versión vigente. |
| `database is locked` | Escrituras simultáneas | Termina la operación que escribe y vuelve a intentar; el MVP se orienta a uso local secuencial. |
| Error de sintaxis FTS | Pregunta vacía o tokens interpretados como operadores | Reformula con palabras descriptivas simples; falta sanitización robusta de consultas. |

## Mejoras prioritarias

1. Separar versiones vigentes del índice histórico y deduplicar documentos.
2. Aplicar alcance por fuente también al feedback y a las URLs obligatorias.
3. Unificar filtros, corregir parámetros sin efecto y registrar fallos de discovery.
4. Vincular pasos y afirmaciones a fragmentos verificables, con abstención cuando falte evidencia.
5. Crear un conjunto de evaluación antes de incorporar búsqueda semántica y generación.

Estas mejoras están propuestas, no implementadas en esta actualización documental. Consulta el [plan de evaluación](evaluacion_ia.md).
