# Resultado del análisis documental

La demostración predeterminada usa documentos ficticios. La validación es aritmética y documental; no acredita validez fiscal ni implica decisiones automáticas.

## Totales incluidos

```json
{
  "validated_total_by_currency": {
    "CLP": "119000"
  },
  "included_count": 1,
  "policy": "Solo documentos completos, con importes válidos y sin discrepancias; duplicados excluidos; agrupación por moneda."
}
```

| Documento | Método | Avisos | Posible copia de |
| --- | --- | --- | --- |
| factura_001.md | native_text | Sin avisos | — |
| factura_002_error.md | native_text | total_mismatch | — |
| factura_003_faltante.md | native_text | missing:tax | — |
| factura_004_duplicada.md | native_text | Sin avisos | factura_001.md |

Campos, citas por línea, hashes y detalles OCR disponibles se conservan en `demo.json`. Un resultado sin avisos no garantiza que se hayan extraído correctamente campos de un diseño desconocido.
