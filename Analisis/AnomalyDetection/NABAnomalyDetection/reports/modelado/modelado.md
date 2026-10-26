# Anomalías en temperatura de una máquina: modelado

Se eligió un umbral **2.6492** por F1 de validación. Los candidatos provienen de cuantiles de los scores de train; el detector utiliza solo observaciones anteriores para calcular media y escala. Las ventanas anómalas de test no intervienen en esta elección.
