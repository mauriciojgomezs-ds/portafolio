# Verificación local de la documentación

Fecha: 7 de octubre de 2026.

Se revisaron los módulos y la ayuda de la CLI y se realizó una comprobación funcional sin red con Python 3.12.10. La prueba utilizó una base separada bajo `.local/verification` y HTML sintético; no modificó la base habitual ni consultó sitios externos.

## Comprobaciones completadas

- Inicialización de una base aislada con FTS5.
- Registro y listado de un origen sin descargar páginas.
- Consulta sin documentos: aviso de información insuficiente.
- Extracción HTML sintética, almacenamiento, recuperación por tag y respuesta con URL.
- Registro y reutilización de una respuesta marcada como validada.
- Registro de error y conteo de estadísticas.
- Cambio de contenido: dos versiones y filas FTS, con un registro de cambio.
- Enlaces locales de la documentación comprobados.

## Alcance

Tras generalizar los componentes, se ejecutaron cuatro pruebas automatizadas sin red: descubrimiento limitado al dominio configurado sin semillas propietarias, rechazo de consultas web sin origen, uso del origen registrado en el flujo de ingesta y respuestas de reglas de acción sin rutas de interfaz de un producto. Las cuatro pasaron. Se verificó la sintaxis de los módulos modificados y la ayuda de la CLI, y se comprobó que el código, los ejemplos y la documentación no conservan nombres del proveedor retirado.

Estas comprobaciones acreditan el funcionamiento local básico descrito, no la calidad de las respuestas ni la disponibilidad de los conectores web. La conservación de versiones históricas en FTS se confirmó y se documenta como limitación. No se ejecutaron discovery, crawling web, instalación limpia ni integración con un LLM. Los ejemplos de consultas externas siguen siendo instrucciones de uso, sin resultados medidos.

La evaluación de relevancia, respaldo y cobertura está pendiente según el [protocolo propuesto](evaluacion_ia.md).
