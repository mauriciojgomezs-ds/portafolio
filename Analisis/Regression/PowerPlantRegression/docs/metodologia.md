# Metodología y límites

La pregunta es la potencia eléctrica (PE, MW) asociada a cuatro variables contemporáneas de una central a plena carga: temperatura AT, vacío V, presión AP y humedad RH. Es regresión tabular, sin rezagos ni objetivo de pronóstico temporal. Las variables deben estar disponibles en el momento de la predicción; su asociación no identifica efectos causales.

El Excel de UCI contiene cinco reordenamientos del mismo conjunto. Se utiliza **solo la primera hoja** para no multiplicar la muestra. Se retiran duplicados exactos y se agrupan filas con las mismas cuatro entradas, incluso si sus objetivos difieren, para mantener esos grupos dentro de una única partición.

Split aproximado por grupos: train 60 %, validación 10 %, calibración 10 % y test 20 %. Los porcentajes por filas pueden variar con el tamaño de grupos. La semilla se declara en config.json. No hay fechas para afirmar validación temporal o independencia entre plantas.

La etapa 02 calcula el factor de inflación de varianza (VIF) de AT, V, AP y RH mediante regresión OLS de cada variable contra las demás; VIF>=10 se marca como multicolinealidad alta y VIF>=5 como moderada. Un VIF alto afecta la interpretación de los coeficientes de Ridge, no la capacidad predictiva evaluada por MAE/RMSE. La etapa 05 añade un diagnóstico de residuos sobre test: correlación entre el residuo absoluto y la predicción (señal de heterocedasticidad) y sesgo (skewness) de los residuos, además del gráfico de dispersión ya incluido.

03 utiliza una media constante ajustada en train. 04 compara Ridge (alpha 1, 10, 100) y HistGradientBoosting (15 o 31 hojas) por MAE de validación. Escalamiento y modelos se ajustan solo en train; no se reentrena con validación después de seleccionar. Calibración queda fuera de la selección y test fuera de toda decisión.

Conformal split: residuos absolutos de calibración ordenados; rango k = ceil((n_cal + 1) × (1 − alpha)). El radio es el residuo k, sin interpolación. Si no puede obtenerse un radio finito, se informa insuficiencia de calibración. Predicción ± radio constituye un intervalo de cobertura nominal 90 % por defecto. Requiere intercambiabilidad para su interpretación de cobertura marginal; no garantiza cobertura por subgrupo, planta, periodo o valor de los atributos.

05 reporta MAE/RMSE en MW, R², cobertura empírica y ancho del intervalo sobre test reservado. No recalibra a partir de su cobertura observada. Incluye residuos y una galería de las 80 predicciones menores, identificada como selección no aleatoria. Los resultados no se generalizan a otras centrales, funcionamiento parcial ni periodos futuros sin otra validación.

## Referencia metodológica

[Angelopoulos y Bates, introducción a predicción conformal](https://arxiv.org/abs/2107.07511).
