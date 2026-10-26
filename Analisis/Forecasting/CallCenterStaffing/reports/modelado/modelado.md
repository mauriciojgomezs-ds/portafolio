# Demanda y dotación de call center: modelado

Se elige HistGradientBoosting con **30 hojas** por MAE de validación. La pérdida Poisson modela conteos; los atributos son solo calendario. Test se pronostica desde el mismo origen fijo posterior a train, sin actualizar modelos ni usar duraciones o volúmenes reales futuros.
