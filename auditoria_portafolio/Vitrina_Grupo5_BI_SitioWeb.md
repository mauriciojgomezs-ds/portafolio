# Vitrina — Grupo 5 (BusinessIntelligence y SitioWeb)

## Resumen

Se agregaron elementos puramente visuales/de navegación a tres README para mejorar su presentación como vitrina de GitHub, sin eliminar ni modificar contenido textual existente (cifras, afirmaciones y limitaciones se mantienen intactas):

- `BusinessIntelligence/README.md`: badge de cantidad de aplicaciones (1).
- `BusinessIntelligence/SalesAccess/README.md`: badges de Python, Streamlit y tests (55 aprobadas, cifra ya documentada en el propio README) + tabla de contenido con anclajes (archivo de 159 líneas y 9 secciones).
- `SitioWeb/README.md`: badge de GitHub Pages y de Python + tabla de contenido con anclajes (archivo de 98 líneas y 5 secciones) + captura real incrustada (`docs/portada.jpg`).

Se verificó previamente (`grep -rln "README.md" scripts app sales_access tests` en SalesAccess, y `scripts src data` en SitioWeb) que ningún script de estas carpetas lee su propio README.md para generar reportes o builds: las únicas referencias a `README.md` en SitioWeb apuntan al README raíz del portafolio y a `Analisis/README.md`, usados por `build_site.py`/`test_site.py` para construir el catálogo del sitio, no a `SitioWeb/README.md` ni a `BusinessIntelligence/README.md`. Por lo tanto, los cambios no afectan ningún proceso automatizado.

Todas las líneas de badges se insertaron inmediatamente debajo del título (`# Nombre`), con un solo salto de línea, sin línea en blanco de por medio; el primer párrafo real conserva su separación habitual (línea en blanco) respecto al badge.

## Tabla de cambios

| ruta | archivo | línea | original | propuesta |
| --- | --- | --- | --- | --- |
| BusinessIntelligence/ | README.md | 2 (nueva) | *(no existía)* | `![Aplicaciones](https://img.shields.io/badge/aplicaciones-1-blue)` |
| BusinessIntelligence/SalesAccess/ | README.md | 2 (nueva) | *(no existía)* | `![Python](https://img.shields.io/badge/python-3.10%2B-blue) ![Streamlit](https://img.shields.io/badge/streamlit-1.65-red) ![Tests](https://img.shields.io/badge/tests-55%20aprobadas-brightgreen)` |
| BusinessIntelligence/SalesAccess/ | README.md | 5–15 (nuevas) | *(no existía)* | Tabla de contenido `## Contenido` con 9 anclajes (Vistas y cuentas … Fichas de agentes) |
| SitioWeb/ | README.md | 2 (nueva) | *(no existía)* | `![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-sitio_est%C3%A1tico-222222) ![Python](https://img.shields.io/badge/python-3.10%2B-blue)` |
| SitioWeb/ | README.md | 6–12 (nuevas) | *(no existía)* | Tabla de contenido `## Contenido` con 5 anclajes (Vista previa local … Organización y alcance) |
| SitioWeb/ | README.md | antes de `## Vista previa local` (nueva) | *(no existía)* | `![Captura de la portada del sitio de presentación](docs/portada.jpg)` |

## Fuentes verificadas para los badges

- Python 3.10+: declarado en `SitioWeb/README.md` ("Se necesita Python 3.10 o posterior") y usado como mínimo común para ambos proyectos.
- Streamlit 1.65: tomado de `BusinessIntelligence/SalesAccess/requirements.lock.txt` (`streamlit==1.65.0`), consistente con `requirements.txt` (`streamlit>=1.65,<2`).
- 55 pruebas: tomado textualmente del propio README de SalesAccess ("Validación actual: **55 pruebas aprobadas**"), no es una cifra nueva.
- GitHub Pages: el workflow `.github/workflows/portfolio-pages.yml` publica `SitioWeb/dist` en GitHub Pages, tal como describe la sección "Publicar en GitHub Pages" del propio README.
