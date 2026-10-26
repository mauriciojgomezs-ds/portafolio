# Metodología y límites

Se toman líneas con CustomerID, cantidad e importe unitario positivos, excluyendo cancelaciones. No se descuentan devoluciones posteriores: el evento es otra compra positiva registrada, no gasto neto ni fidelidad. Se agrupan líneas y facturas del mismo cliente y timestamp como una ocasión de compra.

Origen individual: primera ocasión positiva observada. Evento: segunda ocasión a un timestamp posterior. Censura: mínimo de 90 días y tiempo hasta el cierre del registro. Si no hay seguimiento positivo, se excluye el cliente y se informa el conteo. Primera compra observada no garantiza que sea la primera compra real; el dataset empieza con clientes ya existentes.

Features: log(1 + importe GBP de primera ocasión), log(1 + productos distintos) y país Reino Unido. No se usan cantidades futuras, segunda fecha, historial total ni duración como predictor. Particiones aleatorias 60/20/20 por cliente, estratificadas por evento; no prueban predicción temporal ni independencia respecto a estacionalidad.

Referencia: Kaplan–Meier de train común a todos. Cox con penalizaciones 0,01, 0,1 y 1; selección por C-index de validación. No se reentrena con validación. Diagnóstico exploratorio de riesgos proporcionales en train con transformación rank; p sin ajuste por multiplicidad, por lo que no certifica el supuesto.

Test: C-index de Harrell, que puede depender de la censura, y 200 réplicas bootstrap de clientes con modelo fijo. Intervalo percentil 95 % no incluye incertidumbre del ajuste o selección. Las curvas agregadas comparan KM train, KM test y promedio Cox; son descriptivas y no demuestran calibración. Se requiere censura no informativa (condicional para Cox); la fecha de entrada y estacionalidad pueden cuestionarla. No es churn, causalidad ni garantía de retorno comercial. [Documentación de supervivencia](https://lifelines.readthedocs.io/en/latest/Survival%20Regression.html).

Se conservan las líneas positivas registradas, incluidas repeticiones exactas: no hay ID de línea para distinguir duplicación técnica de unidades registradas por separado. El importe y recuento de códigos pueden incorporar cargos no mercantiles. Estas decisiones afectan covariables de primera ocasión y se deben revisar con una fuente operativa.
