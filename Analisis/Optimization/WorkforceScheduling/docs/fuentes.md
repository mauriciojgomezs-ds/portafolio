# Fuentes y recuperación

Escenario **sintético didáctico**, creado localmente por `setup()` sin acceso externo. Demanda exógena en data/raw/demand.csv; empleados ficticios en data/raw/employees.csv; procedencia y reglas de generación en data/raw/scenario_origin.json. El perfil es fijo y no utiliza un generador aleatorio. Costes en unidades monetarias arbitrarias, sin salarios ni información personal reales.

Ejecuta `python scripts/download_sources.py` o 00 para crear las dos entradas si faltan ambas. Si falta solo una, se detiene para evitar mezclar una entrada del usuario con otra simulada. Las fuentes existentes se conservan. Sus SHA-256 se registran en preparación. [Documentación oficial del solver MILP](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.milp.html).

`data/raw/preferences.csv` se crea en 04 para el escenario sintético identificado si falta. Declara inicio preferido por empleado mediante índice módulo 5; el modelo conserva las fuentes existentes, verifica IDs/inicios y registra su SHA-256. [Escenario alternativo](equilibrio.md).
