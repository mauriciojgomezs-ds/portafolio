# Resultado del copiloto de datos

Cálculos deterministas sobre el archivo indicado. La muestra incluida es ficticia; no es una medición de calidad generativa.

Archivo: `ventas.csv`. Proveedor del plan: `local`.

Pregunta: total de ventas por region

Filas: 12. Duplicados completos conservados: 1.

## Operación y resultado

```json
{
  "plan": {
    "operation": "group_sum",
    "column": "ventas",
    "group_by": "region"
  },
  "result": {
    "status": "calculated",
    "value": {
      "Centro": "310000",
      "Norte": "530000",
      "Sur": "840000"
    },
    "valid_rows": 10,
    "missing_line_numbers": [
      8
    ],
    "invalid_line_numbers": [
      9
    ],
    "policy": "Cálculo sobre valores válidos; filas duplicadas conservadas; faltantes y no numéricos excluidos y declarados. Importes sin conversión de moneda."
  }
}
```

El JSON complementario conserva perfil de columnas y hash del archivo. Los valores omitidos se declaran y no se imputan.
