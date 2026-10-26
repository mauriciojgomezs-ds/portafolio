# Metodología y límites

Elimina duplicados exactos, fechas/cantidades inválidas, cantidades cero y precios no positivos. Conserva cantidades negativas y clientes sin ID para evitar sesgar la facturación. Define positiva = suma de importes > 0; ajustes = valor absoluto de importes < 0; neta = positiva − ajustes. No equivale a beneficios ni a ventas cobradas.

Marca meses parciales según extremos de cobertura y compara los dos últimos meses completos. La etapa 04 construye indicadores y un dashboard, sin entrenar un clasificador. La etapa 05 reconcilia neta del detalle contra agregados mensuales y por país con tolerancia de 0,01 GBP. Coherencia aritmética no garantiza integridad de la operación. Los ajustes se contabilizan en su fecha, sin vinculación a la factura original.
