# Clasificación visual de prendas: evaluacion

En el **test oficial de 10,000 imágenes**, la MLP obtiene **accuracy 85.18%** y **F1 macro 0.8536**: **supera** el F1 macro del baseline (**0.8040**). La clase con menor recall es **Abrigo: 68.80%**. Hay **1,482 errores**. La confusión más frecuente es **Jersey → Camisa (171 casos)**. Estos resultados describen un benchmark de prendas pequeñas en gris; no acreditan desempeño con fotografías reales. Test se usa para evaluación y diagnóstico, no para elegir alpha ni iteraciones.
