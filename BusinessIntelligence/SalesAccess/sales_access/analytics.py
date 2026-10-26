"""Cálculos sobre ventas ya autorizadas, sin acceso a la fuente global."""
import pandas as pd


def segment_summary(data, axis):
    result = data.groupby(axis, as_index=False).agg(
        importe=("venta_neta", "sum"), unidades=("unidades", "sum"),
        operaciones=("venta_id", "count"), clientes=("cliente_id", "nunique"))
    total = result.importe.sum()
    result["participacion"] = result.importe / total if total else 0.0
    result["importe_por_operacion"] = result.importe / result.operaciones
    return result


def rank_extremes(data, axis, metric="importe", limit=5):
    ranked = segment_summary(data, axis).sort_values([metric, axis], ascending=[False, True])
    if len(ranked) < 2:
        return ranked, ranked.iloc[:0]
    count = min(limit, len(ranked) // 2)
    return ranked.head(count), ranked.tail(count).sort_values([metric, axis], ascending=[True, True])


def previous_period(data, start, end):
    """Período anterior del mismo número de días, respetando alcance y filtros."""
    start, end = pd.Timestamp(start), pd.Timestamp(end)
    previous_end = start - pd.Timedelta(days=1)
    previous_start = previous_end - (end - start)
    available = not data.empty and data.fecha.min() <= previous_start and data.fecha.max() >= previous_end
    previous = data[data.fecha.between(previous_start, previous_end)].copy()
    return previous, previous_start, previous_end, available


def percent_change(current, previous, available):
    if not available or previous == 0:
        return None
    return f"{(current / previous - 1) * 100:+.1f}%"


def compare_segments(current, reference, axis):
    """Unión de ambos períodos: incluye entidades nuevas y sin ventas actuales."""
    actual = current.groupby(axis).venta_neta.sum().rename("importe_actual")
    prior = reference.groupby(axis).venta_neta.sum().rename("importe_referencia")
    result = pd.concat([actual, prior], axis=1).fillna(0).reset_index()
    result["diferencia"] = result.importe_actual - result.importe_referencia
    base = result.importe_referencia.where(result.importe_referencia.gt(0))
    result["variacion_pct"] = result.diferencia.div(base).mul(100)
    total_reference = result.importe_referencia.sum()
    result["aporte_variacion_pp"] = result.diferencia / total_reference * 100 if total_reference else float("nan")
    result["situacion"] = "Con ventas en ambos períodos"
    result.loc[result.importe_referencia.eq(0) & result.importe_actual.gt(0), "situacion"] = "Sin importe de referencia"
    result.loc[result.importe_actual.eq(0) & result.importe_referencia.gt(0), "situacion"] = "Sin importe actual"
    result.loc[result.importe_actual.eq(0) & result.importe_referencia.eq(0), "situacion"] = "Sin importe en ambos períodos"
    return result.assign(_impact=result.diferencia.abs()).sort_values(["_impact", axis], ascending=[False, True]).drop(columns="_impact").reset_index(drop=True)
