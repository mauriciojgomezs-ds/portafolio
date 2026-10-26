# Fuentes de IMDbSentiment

Fuente pública de referencia: [sitio de descarga](https://huggingface.co/datasets/stanfordnlp/imdb). La correspondencia y condiciones de uso de la descarga deben revisarse con la documentación de origen.

Las entradas son locales al proyecto:

- `data/raw/train.parquet` (20,979,968 bytes).
- `data/raw/test.parquet` (20,470,363 bytes).

Las huellas SHA-256 están en [fuentes.json](fuentes.json). El notebook de entorno también descarga la ficha original del dataset como [README_fuente.md](README_fuente.md) (en inglés, tal como la publica el origen); no se traduce ni se usa como metodología propia. Puedes recuperar las fuentes con `python scripts/download_sources.py`. Los datasets no se versionan. Compartir el proyecto exige suministrar sus datos por un medio permitido o seguir sus instrucciones de obtención; no requiere otra carpeta del portafolio.

Las copias originales del portafolio se conservaron como archivo; ninguna función de este proyecto las utiliza. Las métricas y supuestos se describen en [metodologia.md](metodologia.md).
