### Interpretación del catálogo de recetas

Hay **522.517 recetas distintas** en **522.517 filas**. Entre los **269.294 ratings agregados disponibles**, la mediana es **5,00**, la media **4,632** y la desviación estándar **0,642**.

Porcentaje de nulos: `aggregatedrating`: **48,46 %**; `reviewcount`: **47,36 %**; `recipeyield`: **66,61 %**; `recipeservings`: **35,01 %**.

Las calorías tienen mediana **317,10**, media **484,44** y máximo **612.854,6**. Los extremos requieren revisar unidades y procedencia.

Las cifras anteriores no validan cardinalidad ni redundancia de columnas con listas; revisa los errores del diagnóstico precedente. Seleccionar solo `int64/float64` tampoco incluye todos los tipos numéricos. El rating agregado difiere de una valoración individual y su uso requiere revisar la disponibilidad temporal.

### Interpretación de las reseñas

Hay **1.401.982 reseñas**, **271.907 usuarios** y **271.678 recetas evaluadas**. El **72,19 %** de los ratings es 5 y el **5,44 %** es 0.

La esparsidad es **99,9981 %**, calculada con **1.401.982 pares únicos**. Los ceros cuentan como interacciones registradas; excluirlos cambia la definición de observación.

Se detectan **0 filas adicionales con pares usuario–receta repetidos**, **0 valores nulos** en usuario, receta o rating y **19 pares** cuya receta no aparece en el catálogo. Estos controles no validan semánticamente todos los campos.

Debe definirse el significado de rating cero y comparar modelos con baselines. La esparsidad no demuestra que NMF sea adecuado; centrar ratings puede generar negativos incompatibles con NMF. Los ingredientes necesitan preparación para TF-IDF y los IDs recodificados requieren mapeos persistidos.

### Alcance del diagnóstico de viabilidad

`evaluar_viabilidad_modelo_general` aplica umbrales heurísticos, no valida desempeño. «Varianza aceptable» solo comprueba si la clase dominante está por debajo del 90 %; «Target con más de dos clases» describe el rating original, aunque el SVM usa `rating >= 4`.

Una matriz densa float64 de los usuarios y recetas observados ocuparía **590,97 GB** (unidades decimales), sin copias ni objetos adicionales. Conviene evaluar estructuras dispersas y documentar el muestreo.

### Historial de usuarios

Para **271.907 usuarios con pares registrados**, la mediana es **1,00**, el tercer cuartil **2,00**, la media **5,16**, la desviación estándar **53,47** y el máximo **8.842**. Se cuentan recetas distintas por usuario y usuarios distintos por receta.

El catálogo contiene **522.517 recetas distintas**; las recetas sin reseñas no participan en la distribución de historiales. Un historial escaso limita la personalización; no demuestra ruido ni justifica excluir entidades sin evaluar cobertura y cold start.

### Historial de recetas

Para **271.678 recetas con pares registrados**, la mediana es **2,00**, el tercer cuartil **4,00**, la media **5,16**, la desviación estándar **19,71** y el máximo **2.892**. Se cuentan recetas distintas por usuario y usuarios distintos por receta.

El catálogo contiene **522.517 recetas distintas**; las recetas sin reseñas no participan en la distribución de historiales. Un historial escaso limita la personalización; no demuestra ruido ni justifica excluir entidades sin evaluar cobertura y cold start.

### Elección exploratoria del umbral

Se aplica el umbral **270** a los conteos originales antes de intersectar usuarios y recetas. No se ha demostrado que optimice error o ranking.

El resultado contiene **617 usuarios**, **190 recetas del catálogo** (**190 con reseñas**) y **10.343 reseñas**. Conserva el **0,227 %** de los usuarios observados, el **0,0364 %** del catálogo y el **0,738 %** de las reseñas.

Los mínimos finales de interacciones distintas son **1 por usuario** y **1 por receta observada**. El umbral previo no garantiza ese mínimo en el resultado. Las recetas del catálogo sin interacciones quedan fuera de estos mínimos. La cobertura no acredita representatividad.

### Interpretación de las recetas filtradas

Hay **190 recetas distintas** en **190 filas**. Entre los **190 ratings agregados disponibles**, la mediana es **5,00**, la media **4,934** y la desviación estándar **0,191**.

Porcentaje de nulos: `aggregatedrating`: **0,00 %**; `reviewcount`: **0,00 %**; `recipeyield`: **67,37 %**; `recipeservings`: **40,00 %**.

Las calorías tienen mediana **322,95**, media **402,50** y máximo **3.343,8**. Los extremos requieren revisar unidades y procedencia.

La desviación estándar de `aggregatedrating` pasa de **0,642 a 0,191**. El **88,42 %** del catálogo filtrado tiene rating agregado 5. Estos cambios describen la selección; no demuestran mejora predictiva ni corrección de errores.

Las cifras anteriores no validan cardinalidad ni redundancia de columnas con listas; revisa los errores del diagnóstico precedente. Seleccionar solo `int64/float64` tampoco incluye todos los tipos numéricos. El rating agregado difiere de una valoración individual y su uso requiere revisar la disponibilidad temporal.

### Correlación: `calories` y `proteincontent`

Método: **pearson**; **190 pares válidos**; **0 filas excluidas**.

El coeficiente es **0,713**: asociación **positiva, muy fuerte**, según los cortes descriptivos del proyecto para |r|: **0,10, 0,30, 0,50, 0,70**. Se clasifica con el coeficiente sin redondear; estos cortes son configurables, no universales. La magnitud no prueba significancia estadística, causalidad ni capacidad predictiva. Pearson describe asociación lineal y puede ser sensible a extremos; Spearman describe asociación monótona. Revisa también el gráfico, las unidades y la selección de datos.

### Correlación: `calories` y `proteincontent`

Método: **spearman**; **190 pares válidos**; **0 filas excluidas**.

El coeficiente es **0,797**: asociación **positiva, muy fuerte**, según los cortes descriptivos del proyecto para |r|: **0,10, 0,30, 0,50, 0,70**. Se clasifica con el coeficiente sin redondear; estos cortes son configurables, no universales. La magnitud no prueba significancia estadística, causalidad ni capacidad predictiva. Pearson describe asociación lineal y puede ser sensible a extremos; Spearman describe asociación monótona. Revisa también el gráfico, las unidades y la selección de datos.

### Interpretación de las reseñas filtradas

Hay **10.343 reseñas**, **617 usuarios** y **190 recetas evaluadas**. El **77,43 %** de los ratings es 5 y el **1,62 %** es 0.

La esparsidad es **91,1772 %**, calculada con **10.343 pares únicos**. Los ceros cuentan como interacciones registradas; excluirlos cambia la definición de observación.

Se detectan **0 filas adicionales con pares usuario–receta repetidos**, **0 valores nulos** en usuario, receta o rating y **0 pares** cuya receta no aparece en el catálogo. Estos controles no validan semánticamente todos los campos.

Antes del filtro, los ratings 5 representaban **72,19 %** y los ceros **5,44 %**. El target `rating >= 4` sería positivo en el **93,61 %** del subconjunto. Ese porcentaje sería la accuracy de predecir siempre positivo sobre este conjunto, no una evaluación del SVM.

Debe definirse el significado de rating cero y comparar modelos con baselines. La esparsidad no demuestra que NMF sea adecuado; centrar ratings puede generar negativos incompatibles con NMF. Los ingredientes necesitan preparación para TF-IDF y los IDs recodificados requieren mapeos persistidos.
