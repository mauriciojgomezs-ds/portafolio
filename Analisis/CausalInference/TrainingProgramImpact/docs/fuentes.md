# Fuentes y recuperación

[Página de datos de Dehejia en NBER](https://users.nber.org/~rdehejia/data/.nswdata2.html). Se descargan nswre74_treated.txt y nswre74_control.txt de esa página, la submuestra experimental con RE74. Se conservan los TXT y se crea un CSV combinado con el orden de variables publicado. La atribución corresponde a LaLonde y al trabajo de Dehejia–Wahba descrito por la fuente. No se presupone una licencia distinta de las condiciones publicadas; revisar atribución y redistribución antes de publicar originales.

Ejecuta `python scripts/download_sources.py` o 00 para recuperar las fuentes si faltan. Requiere Internet solo para una descarga nueva; las entradas existentes se conservan. SHA-256 del CSV en reports/preparacion/preparacion.json.
