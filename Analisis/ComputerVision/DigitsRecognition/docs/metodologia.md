# Metodología y límites

Deduplica imágenes y divide 60/20/20 estratificado. El baseline es NearestCentroid con intensidades; el modelo SVM RBF usa 192 atributos: intensidad y gradientes horizontales/verticales. StandardScaler se ajusta solo en train; C se selecciona por F1 macro de validación.

Test contiene accuracy, F1 macro, métricas por clase y galería de errores. Una prueba adicional desplaza las imágenes un píxel a la derecha, con relleno cero y recorte del borde. Es una perturbación artificial de test, no un criterio de selección. No hay IDs de escritor para verificar independencia por persona. No es OCR de documentos ni una CNN; la resolución baja y la sensibilidad al desplazamiento limitan el uso real.
