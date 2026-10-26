# Fuente y recuperación

AI4I 2020, UCI. Fuente sintética de 10.000 filas; no corresponde a una planta industrial. Se excluyen IDs y todas las etiquetas de fallo como entradas. La descarga conserva el ZIP original y registra su SHA-256.

[Fuente primaria](https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset).

La ruta configurada es `data/raw/AI4I.zip`. Ejecuta `python scripts/download_sources.py` para preparar la fuente local. Si falta el ZIP local, el script descarga el archivo oficial de UCI; requiere acceso a Internet y conserva una fuente existente. Las huellas concretas se registran en `reports/preparacion/preparacion.json`. Consulta las condiciones y atribuciones de la fuente antes de redistribuirla.
