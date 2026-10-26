### Interpretación de clasificación

Accuracy: **93,80 %** sobre **2.065 casos**. El baseline constante de la clase mayoritaria de entrenamiento (**1**) obtiene **93,80 %** en el mismo test: el modelo iguala ese baseline en accuracy. Todas las predicciones pertenecen a la clase **1**.

Recall por clase: clase 0: **0,00 %** (128 casos); clase 1: **100,00 %** (1.937 casos). Si una clase no aparece en test, su recall no está definido. Revisa también F1 macro y la matriz de confusión; accuracy por sí sola no acredita discriminación. La comparación no mide calidad de ranking ni personalización: el clasificador utiliza atributos de receta.
