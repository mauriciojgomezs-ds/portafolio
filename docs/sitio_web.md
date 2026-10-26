# Presentación web del portafolio

La carpeta [SitioWeb](../SitioWeb/README.md) contiene una web estática independiente preparada para GitHub Pages. Presenta el catálogo del README general, las fichas de cada proyecto, los informes integrales y capturas de los MVP. Admite videos de YouTube o archivos MP4.

**Informes** y **Demos** son páginas independientes en la navegación. Informes permite filtrar por Análisis, Business Intelligence e IA y MVP. La clasificación utiliza la línea del proyecto; por ejemplo, RetailKPIAnalysis sigue dentro de Análisis. Actualmente existen 24 informes integrales de Análisis. Las otras líneas ofrecen enlaces a su documentación hasta que cuenten con informes propios.

## Fuente de cada contenido

| Contenido | Fuente | Actualización |
| --- | --- | --- |
| Catálogo, técnicas y estados | `README.md` de la raíz | Editar la tabla y reconstruir |
| Preguntas de los análisis | `Analisis/README.md` | Editar la pregunta y reconstruir |
| Fichas y documentación | README y documentos enlazados de cada proyecto | Editar en el proyecto y reconstruir |
| Informes | `reports/informe_final/informe_final.md` | Ejecutar el proyecto o su generador de informe y reconstruir |
| Perfil | `SitioWeb/data/perfil.json` | Editar y reconstruir |
| Demos y videos | `SitioWeb/data/demos.json` | Editar y reconstruir |

El sitio no sustituye los entornos de análisis ni ejecuta aplicaciones. Para reproducir un resultado, utiliza las instrucciones originales del proyecto. Los estados actuales distinguen resultados ejecutados, límites observados y pruebas pendientes.

La construcción puede realizarse con la documentación y la evidencia versionada: no requiere datasets ni modelos. La salida se escribe en `SitioWeb/dist`, con rutas relativas compatibles con una subcarpeta de GitHub Pages. El flujo de publicación manual está en `.github/workflows/portfolio-pages.yml`.

Consulta la [guía de vista previa, personalización y publicación](../SitioWeb/README.md). El sitio muestra a Mauricio Jason Gómez Sandoval, su [GitHub](https://github.com/mauriciojgomezs-ds), correo profesional y una selección de trayectoria y formación tomada del CV de octubre de 2026. La [guía del perfil](../SitioWeb/docs/perfil_profesional.md) documenta qué se incorporó y cómo editarlo. El enlace exacto de LinkedIn sigue pendiente de confirmar.

La navegación de los informes permite volver desde los reportes de etapa y las vistas de evidencia CSV al informe integral del proyecto correspondiente. Los botones aparecen arriba y abajo del documento y funcionan también al abrir un enlace directamente. Cada vista de evidencia permite descargar el archivo original.

Los JSON se abren en una nueva pestaña para conservar el informe abierto; junto a cada enlace se ofrece Descargar.


El botón Volver al informe recupera el punto de lectura desde el que se abrió el documento, dentro de la misma pestaña. Cada informe mantiene su propia posición durante la sesión de navegación.
