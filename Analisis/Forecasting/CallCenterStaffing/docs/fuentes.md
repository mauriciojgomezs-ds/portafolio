# Fuente y recuperación

Call Center Dataset, publicado en Kaggle por akash1vishwakarma. ZIP con 01 Call-Center-Dataset.xlsx: 5.000 llamadas entre enero y marzo de 2021, fecha, hora, atención Y/N y duración de conversación. El archivo no acredita procedencia operativa ni que contenga todas las llamadas. No se añaden llamadas simuladas. La disponibilidad pública no acredita permisos de redistribución; revisar las condiciones vigentes antes de publicar el archivo original.

[Fuente primaria](https://www.kaggle.com/datasets/akash1vishwakarma/call-center-dataset).

La ruta configurada es `data/raw/CallCenterKaggle.zip`. Ejecuta `python scripts/download_sources.py` para preparar la fuente local. Si falta el ZIP local, el script descarga la fuente pública de Kaggle; requiere acceso a Internet y conserva una fuente existente. Las huellas concretas se registran en `reports/preparacion/preparacion.json`. Consulta las condiciones y atribuciones de la fuente antes de redistribuirla.
