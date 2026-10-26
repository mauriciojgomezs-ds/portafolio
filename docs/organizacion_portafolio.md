# Organización del portafolio

`Analisis/<tema>/<proyecto>` agrupa los veinticuatro proyectos por notebooks. Cada uno conserva su paquete, requisitos, configuración, datos, modelos, documentación y reportes propios. El contenedor no suministra funciones compartidas.

`BusinessIntelligence/SalesAccess` es una aplicación de dashboards con Streamlit. `IAG` agrupa proyectos de IA generativa aplicada. `IAG/knowledge_base_mvp` contiene el prototipo de asistente documental, con evolución hacia IA descrita en su documentación. Conserva su código, datos y flujo de consola independientes de los otros proyectos de IAG. El nivel de implementación de cada aplicación se consulta en su README.

RetailKPIAnalysis se ubica en `Analisis/BusinessIntelligence`: su dashboard HTML es un artefacto del recorrido de análisis. SalesAccess dispone de su flujo propio de aplicación.

## Ejecutar después del traslado

Abre los notebooks desde las rutas nuevas y reinicia los kernels que seguían abiertos en la ubicación anterior. Instala los requisitos desde la carpeta del proyecto y selecciona su Python. El maestro 06 continúa ejecutando exclusivamente sus cinco etapas.

Los notebooks encuentran su propio paquete desde el proyecto, la carpeta notebooks, el tema, Analisis o la raíz del portafolio. También conservan la resolución local cuando se copia o renombra un proyecto por separado; las carpetas de archivo y las carpetas ocultas se excluyen de la búsqueda.

En SmartFood se corrigió la referencia editable y los activadores de texto de su entorno local. Se comprobó que su Python importa smartfood desde la ubicación nueva, junto con pandas y scikit-learn. Para trasladar el proyecto a otra máquina, crea un entorno nuevo siguiendo su README; los entornos virtuales no son artefactos portables.

## Alcance de la comprobación

Se validaron 19 proyectos y 133 notebooks: formato, sintaxis y localización del paquete en cinco contextos. Se comprobaron las entradas de terminal y se regeneraron los informes desde resultados guardados. Los enlaces de los índices y guías comprobados son válidos. No se repitió entrenamiento ni se recalcularon las evaluaciones durante esta reorganización.

Las rutas de intérpretes y mensajes de ejecuciones anteriores se conservan como evidencia histórica. Los registros globales de proyecto y fuentes apuntan a las rutas actuales. Consulta [verificacion_organizacion_analisis.json](verificacion_organizacion_analisis.json) para el alcance y los pendientes del traslado.

## MVP documental dentro de IAG

Knowledge Base MVP se encuentra en [IAG/knowledge_base_mvp](../IAG/knowledge_base_mvp/README.md). Se actualizaron los índices y el ejemplo de instalación para reflejar ese traslado. Su clasificación dentro de IAG no cambia el estado funcional: recuperación documental y respuestas por reglas, con integración generativa propuesta. Esta actualización es documental; no ejecuta consultas, instala paquetes ni modifica su base SQLite.

## Ampliación posterior al traslado

Se incorporaron inferencia causal, regresión tabular y optimización de turnos, con ejecución completa de sus maestros y comprobación en copias independientes. En esa ampliación se llegó a 22 proyectos en 11 temas, con 154 notebooks. La [verificación de la ampliación](verificacion_analisis_incorporados.json) distingue estas pruebas de la comprobación histórica del traslado.

## Ampliación del 8 de octubre

Grafos y supervivencia elevan los análisis a 24 proyectos en 13 temas, con 168 notebooks. Se complementan los cuatro churn y la planificación de turnos dentro de sus etapas existentes. Los dos proyectos nuevos recalcularon sus etapas desde copias independientes; se verificaron siete secuencias completas y 63 tests. Consulta el [registro y alcance](verificacion_analisis_oct08.json) y la [guía de la ampliación](ampliacion_analisis_oct08.md).
