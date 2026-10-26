# PortfolioDemo — Laboratorio de copilotos
![Python](https://img.shields.io/badge/python-3.10%2B-blue) ![Interfaz](https://img.shields.io/badge/interfaz-local%20%28http.server%29-blue) ![Estado](https://img.shields.io/badge/estado-demo%20local%20funcional-brightgreen)

## Contenido
- [Ejecutar](#ejecutar)
- [Qué puedes usar](#qué-puedes-usar)
- [IA, conversión y OCR](#ia-conversión-y-ocr)
- [Registros y capturas](#registros-y-capturas)
- [Verificación](#verificación)

Interfaz local para ejecutar DataCopilot, DocumentAnalyzer y MeetingCopilot desde el navegador y documentar consultas con capturas reales. Invoca el código de cada proyecto; no usa respuestas precargadas.

Consulta la [demostración con capturas y resultados](docs/demostracion.md).

![Consulta de ventas con resultados calculados y política de calidad](docs/capturas/datos.jpg)

## Ejecutar

Desde la raíz del portafolio, con Python 3.10 o superior:

```powershell
python IAG/PortfolioDemo/scripts/serve.py
```

Abre `http://127.0.0.1:8765`. Si ese puerto está ocupado, añade `--port 8766` y abre la dirección correspondiente. Mantén el proceso abierto mientras usas la demo; Ctrl+C lo detiene.

Los ejemplos locales de texto, CSV y transcripción no requieren paquetes adicionales. Esta interfaz necesita las tres carpetas hermanas; cada proyecto conserva sus comandos propios para ejecutarlo independientemente.

## Qué puedes usar

| Flujo | Entrada | Respuesta local |
| --- | --- | --- |
| Datos | CSV UTF-8 con cabecera | Total, promedio, agrupaciones, faltantes y duplicados |
| Documentos | TXT/Markdown con campos reconocibles | Extracción y validación de un lote de facturas |
| Reuniones | JSON en el formato del ejemplo de MeetingCopilot | Fragmentos candidatos con hablante y tiempo |

Sin archivos seleccionados se utilizan los ejemplos ficticios del proyecto. La interfaz acepta hasta diez archivos documentales o uno de datos/reunión; cada archivo tiene un límite de 5 MB y la petición completa de 8 MB.

El historial visual reúne consultas independientes: las preguntas posteriores no reciben automáticamente el contexto de las anteriores. Al cambiar de proyecto o recargar la página se reinicia la vista. No es todavía un chat general con memoria.

## IA, conversión y OCR

Datos y reuniones permiten seleccionar OpenAI. Configura `OPENAI_API_KEY` y `OPENAI_MODEL` en el entorno que inicia el servidor, según los README de [DataCopilot](../DataCopilot/README.md) y [MeetingCopilot](../MeetingCopilot/README.md). La configuración no se introduce en la pantalla. Las llamadas con un proveedor real no se han validado en esta demostración.

El flujo documental de esta interfaz usa validación local. No interpreta preguntas libres sobre un documento. PDF, Office e imágenes requieren las dependencias opcionales de [DocumentAnalyzer](../DocumentAnalyzer/README.md): MarkItDown para conversión y PaddleOCR/PaddlePaddle para OCR. Los adaptadores están implementados; esas integraciones no se han probado con los motores reales en esta sesión.

La agenda y su evaluación siguen disponibles mediante los comandos de MeetingCopilot; esta pantalla muestra el flujo de preguntas. El contexto de agenda del ejemplo se carga al usar la transcripción predeterminada.

## Registros y capturas

Cada ejecución conserva su resultado y, desde esta versión, `conversation.json` en `.local/runs/<identificador>/`. Esa carpeta queda excluida de Git. El botón de descarga solicita un JSON de las consultas visibles al navegador; su descarga no pudo verificarse en el navegador integrado de esta sesión. El registro del servidor permite recuperar las consultas aunque no se complete la descarga.

Para documentar otra prueba: registra entrada y pregunta, toma una captura donde se vea el modo de respuesta, copia el resultado correspondiente y describe sus limitaciones. Publica solo los ejemplos que hayas revisado; los incluidos aquí son sintéticos.

Los estilos de impresión permiten usar la opción de imprimir del navegador para guardar la conversación visible como PDF. La impresión no ha sido verificada en esta sesión.

## Verificación

```powershell
python -m unittest discover -s IAG/PortfolioDemo/tests -v
```

Prueba la conexión real con los tres programas locales, un CSV distinto al ejemplo, la conservación del registro y el rechazo de solicitudes no admitidas. No realiza llamadas a proveedores externos.

Este servidor escucha únicamente en el equipo local y está pensado para demostración. Publicar el documento en GitHub no despliega la aplicación: otra persona debe descargar el código y ejecutarla.
