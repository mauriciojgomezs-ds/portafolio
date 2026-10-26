# Dirección visual del portafolio

Identidad vigente: **Mauricio Gómez S**, con un emblema tipográfico **MG**. La línea profesional reproduce los cuatro encabezados del CV de octubre de 2026: AI & Data Solutions, Data Engineering, Automation y Business Intelligence.

## Composición

La portada utiliza dos columnas asimétricas en escritorio: presentación principal e índice de trabajo. El índice muestra cantidades calculadas desde el catálogo y las demos configuradas. En móvil, ambos bloques se apilan.

Las secciones numeradas organizan la selección de proyectos, el archivo completo, los informes, las áreas profesionales, la trayectoria y el contacto. Las fichas se delimitan con líneas y espacios; los gráficos y las capturas corresponden a los proyectos existentes.

Informes y Demos conservan páginas independientes. Los filtros muestran su selección mediante texto, contraste y bordes. Los enlaces activos en la navegación tienen subrayado y `aria-current`.

## Tipografía y color

- Tipografía principal: fuentes sans serif del sistema; peso marcado en títulos.
- Etiquetas y referencias: fuentes monoespaciadas del sistema.
- Fondo: `#f3f1eb`; texto principal: `#20231f`.
- Texto secundario: `#62665d`; acento terracota: `#983c20`.
- No se requieren fuentes externas ni imágenes decorativas descargadas.

Los estilos se mantienen en `src/styles.css`. Los contenidos, nombres, especialidades y proyectos destacados siguen configurándose en `data/perfil.json`.

## Verificación

Se comprobó la portada en escritorio y la adaptación móvil de la navegación y la página Demos. El ancho de contenido coincide con el ancho disponible, sin desbordamiento horizontal observado. Se comprobaron los filtros del catálogo y de informes después del cambio visual; la revisión automática valida las rutas locales y las anclas.

Para conservar la coherencia, utiliza las clases existentes, evita añadir un color distinto por proyecto y mantén los estados y limitaciones visibles. Al incorporar contenido nuevo, reconstruye el sitio y revisa sus páginas en escritorio y móvil.
