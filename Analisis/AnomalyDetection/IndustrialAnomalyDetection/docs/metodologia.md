# Metodología y límites

Se divide 60/20/20 de forma estratificada por etiqueta, sin combinaciones de sensores idénticas entre particiones. No hay validación temporal. El escalamiento y Isolation Forest se ajustan únicamente con filas normales de train. El baseline utiliza el máximo z-score y cuantil 0,99 de normales. El detector selecciona un umbral entre tres cuantiles mediante F1 de validación. Test se reserva para comparar precision, recall, F1 y average precision.

La cadena es semisupervisada: las etiquetas definen las filas normales y permiten elegir el umbral. El desbalance hace insuficiente la accuracy. Los fallos son sintéticos y no se demuestra anticipación de averías. Una mejora futura requiere sensores reales con fecha, coste de falsas alarmas y evaluación temporal.
