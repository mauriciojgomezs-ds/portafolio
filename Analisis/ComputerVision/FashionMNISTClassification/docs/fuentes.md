# Fuente y procedencia

Fuente primaria: [Zalando Research · Fashion-MNIST](https://github.com/zalandoresearch/fashion-mnist). Imágenes en gris de 28×28, diez categorías, 60.000 ejemplos oficiales de desarrollo y 10.000 de test. [Licencia MIT de la fuente](https://github.com/zalandoresearch/fashion-mnist/blob/master/LICENSE).

Los cuatro archivos gzip IDX se guardan en `data/raw/`. El comando `scripts/download_sources.py` y el notebook 00 utilizan el repositorio oficial, comprueban los MD5 publicados y no reemplazan fuentes existentes. Un checksum distinto produce un error. 01 calcula SHA-256 y registra URLs y huellas en `reports/preparacion/preparacion.json`.

El proyecto no requiere `back` ni otra carpeta del portafolio. Una copia nueva debe recuperar las fuentes con 00 o el comando de descarga. No se redistribuyen los datos en el repositorio del portafolio.
