# Fuente y recuperación

Online Retail, UCI. Facturas entre diciembre de 2010 y diciembre de 2011, en libras esterlinas (GBP). Cantidades negativas se conservan como ajustes, sin afirmar que cada una sea una devolución de un pedido identificado. Copia local independiente de la utilizada en otros proyectos.

[Fuente primaria](https://archive.ics.uci.edu/dataset/352/online+retail).

La ruta configurada es `data/raw/OnlineRetailUCI.zip`. Ejecuta `python scripts/download_sources.py` para preparar la fuente local. Si falta el ZIP local, el script descarga Online Retail desde UCI; requiere acceso a Internet y conserva una fuente existente. Las huellas concretas se registran en `reports/preparacion/preparacion.json`. Consulta las condiciones y atribuciones de la fuente antes de redistribuirla.
