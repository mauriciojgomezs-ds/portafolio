# Perfil profesional del sitio

La presentación toma como fuente el CV proporcionado por Mauricio, `CV_MGomez_10-2026.pdf`, revisado en sus cuatro páginas. El sitio utiliza una síntesis editable en `data/perfil.json`; no necesita acceder al PDF para construirse.

## Contenido incorporado

- Nombre: Mauricio Jason Gómez Sandoval.
- Presentación centrada en ciencia de datos, ingeniería de datos, automatización e IA aplicada.
- Cuatro áreas de trabajo: análisis y BI; ingeniería de datos y automatización; IA y productos; gobierno y calidad.
- Recorrido en cuatro etapas: análisis y control de gestión; ingeniería de datos y automatización; liderazgo y arquitectura; desarrollo independiente de soluciones de IA. La presentación se organiza por responsabilidades y aportes, sin listar empleadores.
- Formación seleccionada en Data Science, Advanced Analytics, Gobierno y Protección de Datos e Ingeniería en Ejecución Informática, conservando la condición de **egresado**.
- GitHub aportado en la conversación y correo profesional aportado en el CV.

La síntesis combina la trayectoria del CV con la orientación del portafolio. No convierte los años de experiencia general en años de experiencia específica como data scientist ni reproduce los porcentajes de impacto laboral como métricas de estos proyectos. Las fechas se muestran según el CV de octubre de 2026; actualiza los periodos abiertos cuando cambie la trayectoria.

«Mi recorrido» resume la evolución de cargos y responsabilidades en orden cronológico. Cada etapa incluye un aporte destacado del CV: tableros para más de 50 campañas, integración de cinco sistemas y eliminación de diez horas semanales de reportabilidad manual, y un agente adoptado por 12 equipos con una reducción del 45 % en los tiempos de configuración. Estas cifras se atribuyen a la experiencia laboral descrita en el CV; no se presentan como resultados de los notebooks ni como mediciones verificadas por la web. La etapa actual describe iniciativas de IA sin añadir cifras de impacto no documentadas.

## Alcance de la selección

El PDF original se conserva en su ubicación original y no se copia al sitio. La selección omite teléfonos, referencias con contactos de terceros y detalles de clientes. Tampoco añade al catálogo los proyectos mencionados en el CV que aún no tienen una ficha verificable en este repositorio.

El enlace exacto de LinkedIn sigue pendiente: el CV muestra una dirección textual con un carácter acentuado, sin un enlace PDF asociado que permita confirmar su URL. Cuando tengas la dirección pública, añádela a `linkedin_url`.

Los estados actuales de los análisis y MVP mantienen sus limitaciones y pruebas pendientes. La experiencia profesional aporta contexto; la evidencia de cada proyecto sigue estando en sus propios documentos e informes.

Para actualizar: edita `data/perfil.json`, reconstruye el sitio con `scripts/build_site.py` y ejecuta `scripts/check_site.py`. La trayectoria y formación se presentan en la portada, después del catálogo y antes del contacto. Las demos tienen su propia página.
