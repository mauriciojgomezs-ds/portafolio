# Metodología y evaluación

Se valida el tipo IDX, dimensiones, longitud, rango de etiquetas y correspondencia de imágenes y etiquetas. Se conserva íntegro el test oficial de 10.000 imágenes. En desarrollo se agrupa por SHA-256 del contenido de imagen, se retiran duplicados, grupos con etiquetas contradictorias y coincidencias exactas con test. Este control usa el contenido para prevenir solapamiento, no el desempeño o etiquetas de test para seleccionar modelos. Los conteos se registran.

Del desarrollo resultante se separa validación estratificada de 20 %, con semilla 42. Se muestrean de forma estratificada hasta 12.000 imágenes de entrenamiento y 3.000 de validación, según config.json. Los índices de origen se guardan en NPZ; test conserva su orden original. Se divide cada píxel por la constante 255: no se estima un escalamiento con validación o test.

El baseline es SGDClassifier lineal con log_loss y parámetros fijos. La MLP tiene una capa oculta de 64 neuronas; compara alpha 0,0001 y 0,001 sobre las mismas particiones. Se selecciona mayor F1 macro de validación, con accuracy como desempate; no se vuelve a entrenar sobre validación. Los criterios internos de parada de la MLP utilizan el entrenamiento, con early_stopping=False. El máximo de iteraciones no garantiza convergencia.

05 evalúa una vez por ejecución el test oficial: accuracy, F1 macro con diez clases, precision/recall/F1 por clase y matriz de confusión. Los ceros indefinidos se representan por convención con zero_division=0; deben leerse junto con los soportes. Las clases peor detectadas y confusiones principales se calculan automáticamente. Los primeros doce errores según el orden de test son ejemplos ilustrativos, no una muestra aleatoria representativa.

La MLP no aprovecha convoluciones ni aumentos de datos. Las cifras no son comparables sin matices con modelos entrenados sobre todo el conjunto oficial; no acreditan generalización a fotos reales. Los diagnósticos de test sirven para describir limitaciones, no para elegir nuevos parámetros contra ese mismo test. Una evolución hacia CNN o nuevas decisiones requiere validación y un test reservado para la nueva comparación.
