# Reconocimiento de dígitos escritos: preparacion

Se usa la copia **load_digits de scikit-learn: imágenes de 8×8**, no el MNIST de 28×28. Se deduplica contenido y divide 60/20/20 estratificado. No hay IDs de escritor para comprobar independencia por persona. El conjunto procede de una parte del dataset UCI; este split propio no replica su protocolo oficial.
