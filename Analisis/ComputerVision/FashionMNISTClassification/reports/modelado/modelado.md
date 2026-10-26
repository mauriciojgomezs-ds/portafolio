# Clasificación visual de prendas: modelado

Se selecciona una **MLP de 64 neuronas ocultas**, con **alpha 0.001**, por F1 macro de validación. No se reentrena con validación ni se consulta test para elegir. Es una red densa sobre píxeles aplanados, **no una CNN**; no incorpora convoluciones ni aumento de datos. Las alertas de convergencia deben revisarse, sin asumir que alcanzar el máximo de iteraciones implica convergencia.
