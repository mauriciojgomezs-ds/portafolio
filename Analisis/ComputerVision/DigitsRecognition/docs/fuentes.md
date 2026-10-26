# Fuente y recuperación

load_digits de scikit-learn. 1.797 imágenes de 8×8 e intensidades 0–16, derivadas del dataset UCI de dígitos. No es MNIST. La copia se exporta a un NPZ local y se registra su huella; no requiere descarga adicional.

[Fuente primaria](https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_digits.html).

La ruta configurada es `data/raw/digits.npz`. Ejecuta `python scripts/download_sources.py` para preparar la fuente local. El script exporta a NPZ el dataset incluido en scikit-learn; no requiere una descarga externa y conserva una fuente existente. Las huellas concretas se registran en `reports/preparacion/preparacion.json`. Consulta las condiciones y atribuciones de la fuente antes de redistribuirla.
