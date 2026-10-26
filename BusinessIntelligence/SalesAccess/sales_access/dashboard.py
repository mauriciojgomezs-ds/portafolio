import altair as alt
import streamlit as st

from .analytics import rank_extremes, segment_summary, previous_period, compare_segments
import pandas as pd
from .data import export_csv
from .agents import agent_labels, ranking_cards


LABELS = {"agente_id": "Vendedor", "producto": "Producto", "region": "Región",
          "sector": "Sector", "cliente_id": "Cliente", "equipo": "Equipo"}
METRICS = {"Importe": "importe", "Unidades": "unidades", "Operaciones": "operaciones"}


def period_comparator(segment, current, dates, metadata, money):
    st.divider()
    st.subheader("1 · Comparador de períodos")
    st.write("Identifica qué productos, regiones o vendedores aportan a la variación del importe. El período actual y los filtros se seleccionan en la barra lateral.")
    mode = st.radio("Comparar con", ["Período anterior equivalente", "Período personalizado"], horizontal=True, key="comparison_mode")
    reference, start, end, available = previous_period(segment, dates[0], dates[1])
    if mode == "Período personalizado":
        earliest = segment.fecha.min().date()
        latest = min(segment.fecha.max().date(), dates[0] - pd.Timedelta(days=1))
        if latest < earliest:
            st.info("El período actual comienza al inicio del historial disponible. Selecciona un período actual más reciente para comparar.")
            return
        # El historial/filtros pueden cambiar durante una sesión: descarta un rango fuera de sus límites.
        saved = st.session_state.get("comparison_reference")
        if saved and any(day < earliest or day > latest for day in saved):
            st.session_state.pop("comparison_reference", None)
        chosen = st.date_input("Período de referencia", value=(max(earliest, start.date()), latest),
                               min_value=earliest, max_value=latest, key="comparison_reference")
        if len(chosen) != 2:
            st.info("Selecciona el inicio y el fin del período de referencia.")
            return
        start, end = map(pd.Timestamp, chosen)
        reference = segment[segment.fecha.between(start, end)].copy()
        available = True
    st.caption(f"Actual: {dates[0]:%d/%m/%Y} — {dates[1]:%d/%m/%Y} · Referencia: {start:%d/%m/%Y} — {end:%d/%m/%Y} · {metadata['currency']}")
    if not available:
        st.info("No hay historial suficiente para cubrir el período de referencia completo. Selecciona Últimos 30 días o Últimos 90 días, o define un período personalizado.")
        return
    current_days = (pd.Timestamp(dates[1]) - pd.Timestamp(dates[0])).days + 1
    reference_days = (end - start).days + 1
    if current_days != reference_days:
        st.warning(f"Los períodos tienen distinta duración: {current_days} y {reference_days} días. Se comparan importes totales sin normalizar por día.")
    if reference.empty:
        st.info("El período de referencia no registra operaciones para estos filtros. Las diferencias se muestran sin variación porcentual cuando no hay base.")
    actual_total, reference_total = current.venta_neta.sum(), reference.venta_neta.sum()
    diff = actual_total - reference_total
    cards = st.columns(3)
    for card, label, value in [(cards[0], "IMPORTE ACTUAL", money(actual_total)),
                               (cards[1], "IMPORTE DE REFERENCIA", money(reference_total)),
                               (cards[2], "DIFERENCIA TOTAL", f"{diff:+,.2f}")]:
        with card:
            with st.container(border=True):
                st.caption(label)
                st.markdown(f"**{value}**")
    total_change = f"{diff/reference_total:+.1%}" if reference_total else "sin base para un porcentaje"
    st.write(f"Variación total: **{total_change}**. La suma de las diferencias del desglose explica el cambio total.")
    axis = st.selectbox("Explicar la variación por", ["producto", "region", "agente_id"], format_func=LABELS.get, key="comparison_axis")
    comparison = compare_segments(current, reference, axis)
    if metadata.get("simulated_assignments") and axis == "agente_id":
        st.caption("Los vendedores corresponden a asignaciones simuladas de la demo.")
    chart = alt.Chart(comparison.head(10)).mark_bar(cornerRadiusEnd=4).encode(
        x=alt.X("diferencia:Q", title="Diferencia de importe frente a referencia"),
        y=alt.Y(f"{axis}:N", title=None, sort=list(comparison.head(10)[axis])),
        color=alt.condition(alt.datum.diferencia >= 0, alt.value("#167D8D"), alt.value("#D99344")),
        tooltip=[alt.Tooltip(f"{axis}:N", title=LABELS[axis]),
                 alt.Tooltip("importe_actual:Q", title="Actual", format=",.2f"),
                 alt.Tooltip("importe_referencia:Q", title="Referencia", format=",.2f"),
                 alt.Tooltip("diferencia:Q", title="Diferencia", format="+,.2f"),
                 alt.Tooltip("variacion_pct:Q", title="Variación (%)", format=".1f")]).properties(height=max(180, min(10, len(comparison))*30))
    st.altair_chart(chart, width="stretch")
    st.caption("Los 10 mayores cambios por magnitud. Verde: aumento; naranja: disminución. Es una descomposición aritmética del resultado, no una prueba de causalidad.")
    st.dataframe(comparison, hide_index=True, width="stretch", column_config={
        axis: LABELS[axis], "importe_actual": st.column_config.NumberColumn("Importe actual", format="%.2f"),
        "importe_referencia": st.column_config.NumberColumn("Importe referencia", format="%.2f"),
        "diferencia": st.column_config.NumberColumn("Diferencia", format="%.2f"),
        "variacion_pct": st.column_config.NumberColumn("Variación (%)", format="%.1f"),
        "aporte_variacion_pp": st.column_config.NumberColumn("Aporte al cambio (pp)", format="%.2f")})
    st.caption("El aporte en puntos porcentuales usa como base el importe total de referencia. Su suma coincide con la variación global en porcentaje. Los porcentajes sin base se dejan vacíos.")
    st.download_button("Descargar comparación CSV", export_csv(comparison), file_name=f"comparacion_{axis}_{dates[0]}_{dates[1]}.csv", mime="text/csv")


def bars(frame, axis, metric, color):
    chart_axis = axis
    if axis == "agente_id":
        frame = frame.copy()
        names = agent_labels()
        frame["vendedor"] = frame.agente_id.map(lambda identifier: names.get(identifier, identifier))
        chart_axis = "vendedor"
    chart = alt.Chart(frame).mark_bar(cornerRadiusEnd=5).encode(
        x=alt.X(f"{metric}:Q", title=next(label for label, key in METRICS.items() if key == metric)),
        y=alt.Y(f"{chart_axis}:N", title=None, sort=list(frame[chart_axis])),
        color=alt.value(color),
        tooltip=[alt.Tooltip(f"{axis}:N", title=LABELS[axis]),
                 alt.Tooltip("importe:Q", title="Importe", format=",.2f"),
                 alt.Tooltip("unidades:Q", title="Unidades"),
                 alt.Tooltip("operaciones:Q", title="Operaciones"),
                 alt.Tooltip("participacion:Q", title="Participación", format=".1%")]
    ).properties(height=max(130, len(frame) * 40))
    st.altair_chart(chart, width="stretch")


def rankings(data, axis, metric):
    top, bottom = rank_extremes(data, axis, metric)
    left, right = st.columns(2)
    with left:
        st.markdown(f"#### Top {len(top)} · {LABELS[axis].lower()}")
        bars(top, axis, metric, "#167D8D")
        if axis == "agente_id":
            ranking_cards(top)
    with right:
        st.markdown(f"#### Bottom {len(bottom)} · {LABELS[axis].lower()}" if not bottom.empty else f"#### Menor aporte · {LABELS[axis].lower()}")
        if bottom.empty:
            st.caption("Solo hay un elemento con ventas en este período; no hay otro para comparar.")
        else:
            bars(bottom, axis, metric, "#D99344")
            if axis == "agente_id":
                ranking_cards(bottom)
    st.caption("Hasta 5 por extremo, sin repetir elementos. Solo considera elementos con ventas dentro de los filtros; menor importe no implica bajo desempeño ni incumplimiento de metas.")


def insights(data, role, metadata, money):
    st.divider()
    st.subheader("Claves del período")
    product = segment_summary(data, "producto").sort_values(["importe", "producto"], ascending=[False, True]).iloc[0]
    region = segment_summary(data, "region").sort_values(["importe", "region"], ascending=[False, True]).iloc[0]
    cards = st.columns(3)
    with cards[0]:
        with st.container(border=True):
            st.caption("PRODUCTO CON MAYOR APORTE")
            st.markdown(f"**{product.producto}**")
            st.write(f"{product.participacion:.1%} del importe · {money(product.importe)}")
    with cards[1]:
        with st.container(border=True):
            st.caption("REGIÓN CON MAYOR APORTE")
            st.markdown(f"**{region.region}**")
            st.write(f"{region.participacion:.1%} del importe · {money(region.importe)}")
    with cards[2]:
        with st.container(border=True):
            axis = "cliente_id" if role == "agente" else "agente_id"
            concentration = segment_summary(data, axis).nlargest(3, "importe").participacion.sum()
            st.caption("CONCENTRACIÓN DE VENTAS")
            st.markdown(f"**{concentration:.1%}**")
            st.write("Aporte de los 3 principales clientes" if role == "agente" else "Aporte de los 3 principales vendedores")
    if metadata.get("simulated_assignments") and role != "agente":
        st.caption("Los rankings de vendedores corresponden a asignaciones simuladas de la demo.")

    st.subheader({"gerente": "Dónde se gana y dónde hay oportunidades",
                  "supervisor": "Prioridades de mi equipo", "analista": "Explorar concentración y mezcla",
                  "agente": "Productos y clientes de mi cartera"}[role])
    tabs = st.tabs(["Rankings", "Mezcla y territorio", "Cartera de clientes"])
    with tabs[0]:
        metric = METRICS[st.selectbox("Ordenar rankings por", list(METRICS), key="ranking_metric")]
        if role != "agente":
            rankings(data, "agente_id", metric)
        rankings(data, "producto", metric)
        if role in {"analista", "supervisor"}:
            axis = st.selectbox("Desglose del ranking", ["agente_id", "producto"], format_func=LABELS.get)
            table = segment_summary(data, axis).sort_values([metric, axis], ascending=[False, True])
            st.dataframe(table, hide_index=True, width="stretch",
                         column_config={"participacion": st.column_config.NumberColumn("Participación", format="percent")})
            st.download_button("Descargar ranking CSV", export_csv(table), file_name=f"ranking_{role}.csv", mime="text/csv")
    with tabs[1]:
        left, right = st.columns(2)
        with left:
            st.markdown("#### Mezcla por sector")
            sectors = segment_summary(data, "sector")
            if sectors.importe.sum() > 0:
                chart = alt.Chart(sectors).mark_arc(innerRadius=65).encode(
                    theta=alt.Theta("importe:Q"), color=alt.Color("sector:N", title="Sector"),
                    tooltip=["sector:N", alt.Tooltip("importe:Q", format=",.2f"), alt.Tooltip("participacion:Q", format=".1%")]).properties(height=280)
                st.altair_chart(chart, width="stretch")
            else:
                st.caption("No hay importe positivo para calcular la mezcla.")
        with right:
            st.markdown("#### Importe por región")
            bars(segment_summary(data, "region").sort_values("importe", ascending=False), "region", "importe", "#167D8D")
        if role == "analista":
            st.markdown("#### Matriz producto × región")
            matrix = data.groupby(["producto", "region"], as_index=False).venta_neta.sum()
            heatmap = alt.Chart(matrix).mark_rect().encode(
                x=alt.X("region:N", title="Región"), y=alt.Y("producto:N", title="Producto"),
                color=alt.Color("venta_neta:Q", title="Importe", scale=alt.Scale(scheme="tealblues")),
                tooltip=["producto:N", "region:N", alt.Tooltip("venta_neta:Q", format=",.2f")]).properties(height=max(250, matrix.producto.nunique()*18))
            st.altair_chart(heatmap, width="stretch")
    with tabs[2]:
        clients = segment_summary(data, "cliente_id").sort_values(["importe", "cliente_id"], ascending=[False, True])
        left, right = st.columns([1.4, 1])
        with left:
            st.markdown("#### Principales clientes")
            bars(clients.head(5), "cliente_id", "importe", "#167D8D")
        with right:
            st.markdown("#### Frecuencia de compra")
            repeated = int(clients.operaciones.gt(1).sum())
            st.write(f"**{repeated} de {len(clients)} clientes** tienen más de una operación en el período.")
            st.progress(repeated / len(clients))
            st.caption("La frecuencia cuenta operaciones, no pedidos únicos. Los clientes se identifican solo por su código.")
