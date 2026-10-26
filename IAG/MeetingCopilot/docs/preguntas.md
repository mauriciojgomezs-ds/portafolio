# Preguntas conectadas a la reunión

## Uso local inmediato

Desde la carpeta del proyecto, con Python 3.10 o superior y sin instalar dependencias:

```powershell
python scripts/ask.py "¿Cuál fue el presupuesto final aprobado?"
python scripts/ask.py "¿Quién carga los datos y cuándo debe entregarlos?"
python scripts/ask.py "¿Qué se acordó sobre el plan de pruebas?"
```

El modo predeterminado busca fragmentos candidatos mediante coincidencias léxicas y muestra hablante, identificador y tiempo. No genera una respuesta ni calcula cumplimiento. Una coincidencia no garantiza relevancia y la falta de coincidencias no demuestra que no se habló del tema.

## Activar respuestas generativas

El conector implementado utiliza la API Responses de OpenAI y JSON Schema estricto para solicitar afirmaciones con citas. El modelo se configura explícitamente; debe admitir Responses y salidas estructuradas. La implementación sigue la [documentación oficial de salidas estructuradas](https://developers.openai.com/api/docs/guides/structured-outputs?api-mode=responses).

Configura `OPENAI_API_KEY` en el entorno local. No pegues la clave en el chat ni la guardes en archivos versionados. Para cargarla sin mostrarla mientras escribes en PowerShell:

```powershell
$meetingApiSecret = Read-Host "Clave API" -AsSecureString
$env:OPENAI_API_KEY = [System.Net.NetworkCredential]::new("", $meetingApiSecret).Password
$env:OPENAI_MODEL = Read-Host "Identificador del modelo compatible"
python scripts/ask.py "¿Cuál fue el presupuesto final aprobado?" --provider openai --agenda examples/agenda.json
```

También puedes pasar el modelo mediante `--model`. El código lee variables del proceso; no carga archivos `.env` automáticamente. Las consultas con `--provider openai` envían pregunta, contexto previo suministrado y transcripción seleccionada al proveedor, y consumen uso de API. La solicitud lleva `store=false`; esto no debe interpretarse como una garantía general de retención cero.

La prueba local no invoca al proveedor. No hay clave ni modelo configurados en el entorno de desarrollo de esta entrega, por lo que la conexión real sigue sin verificarse.

## Otra reunión y guardar resultados

```powershell
python scripts/ask.py "¿Qué fecha quedó confirmada?" --transcript examples/transcript.json --agenda examples/agenda.json --provider openai --output .local/questions/fecha.json
```

Usa el formato de intervenciones de `examples/transcript.json`. Si agregas agenda, su `meeting_id` debe coincidir con el de la transcripción. Cada consulta es independiente: no hay memoria de conversación; formula preguntas completas, evitando referencias como «¿y él?» sin contexto.

El JSON opcional conserva pregunta, proveedor, modelo, versión del prompt, alcance e identificadores de contexto, respuesta con citas, tiempos y uso reportado por el proveedor. No guarda la clave ni calcula costos monetarios. Estos resultados pueden contener información de la reunión; por defecto no se guardan en disco.

## Cómo se construye la respuesta

1. Validar la transcripción, los tiempos y la correspondencia de la agenda.
2. Buscar candidatos por términos normalizados y algunas equivalencias de vocabulario.
3. Para reuniones pequeñas, enviar todas las intervenciones: esto ayuda a conservar negaciones, cambios de responsable y correcciones al cierre.
4. Si se supera el límite de contexto, seleccionar candidatos, vecinos y últimas intervenciones; declarar que el contexto es parcial. Si aun así excede el límite, detenerse antes de llamar al proveedor.
5. Pedir afirmaciones, citas y limitaciones en JSON estructurado, sin incluir archivos de respuestas o revisiones de referencia.
6. Rechazar estructuras inválidas, citas inventadas o identificadores fuera del contexto enviado. Añadir hablante y tiempo a partir de los datos originales.

El límite predeterminado es de 80.000 caracteres del contexto serializado, configurable con `--max-context-chars`. Es un límite de la aplicación, no una medición de tokens ni una garantía de compatibilidad con la ventana del modelo. `--limit` controla candidatos léxicos, no el tamaño del contexto completo en reuniones pequeñas.

## Garantías y límites

El código comprueba que cada cita existe literalmente. No verifica automáticamente que la interpretación del modelo sea correcta: una afirmación podría citar un fragmento real que no la sustente. Los hechos deben revisarse contra el texto y su contexto.

Una respuesta puede declarar `insufficient_evidence`, incluir hallazgos parciales con citas y explicar lo faltante. Los errores de acceso, cuota, conexión, respuestas incompletas y rechazos se muestran como fallos; no se sustituyen por respuestas supuestamente generadas ni por el resultado esperado.

Las preguntas sobre porcentajes no activan una evaluación automática de agenda. Esa integración permanece pendiente y debe reutilizar el cálculo determinista del proyecto, después de proponer y revisar estados por objetivo.

## Verificación realizada

Se prueban recuperación local, conservación de correcciones, exclusión de referencias del contexto, trazabilidad, abstención, límite de contexto y manejo de credenciales ausentes. El contrato de petición y respuesta del proveedor se prueba con una respuesta simulada. Esto no mide calidad generativa ni confirma acceso real al modelo.

```powershell
python -m unittest discover -s tests -v
```
