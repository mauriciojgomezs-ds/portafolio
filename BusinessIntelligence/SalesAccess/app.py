import time

import pandas as pd
import streamlit as st

from sales_access.data import export_csv, load_sales
from sales_access.security import DB, authenticate, authorized_sales, get_profile
from sales_access.analytics import previous_period, percent_change
from sales_access.dashboard import insights, period_comparator
from sales_access.agents import render_directory

st.set_page_config(page_title="Ventas · Portal comercial", page_icon="📊", layout="wide")
st.markdown("""<style>
    .block-container {padding-top: 2rem; max-width: 1440px;}
    [data-testid="stMetric"] {background: white; border: 1px solid #DCE5EB;
        padding: 18px; border-radius: 12px;}
    h1, h2, h3 {letter-spacing: -.025em;}
</style>""", unsafe_allow_html=True)


def money(value):
    return f"{value:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")


def logout():
    st.session_state.clear()


def login():
    _, center, _ = st.columns([1, 1.4, 1])
    with center:
        st.caption("PORTAL COMERCIAL / ACCESO PRIVADO")
        st.title("Tus ventas.\nTu perspectiva.")
        st.write("Indicadores y resultados según tu responsabilidad comercial.")
        if not DB.exists():
            st.info("Primero crea las cuentas con: python scripts/setup_demo.py")
            st.stop()
        with st.form("login"):
            username = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            submit = st.form_submit_button("Entrar al reporte", type="primary", width="stretch")
        if submit:
            profile = authenticate(username, password)
            if profile:
                st.session_state.clear()
                st.session_state["username"] = profile.username
                st.session_state["login_time"] = time.time()
                st.rerun()
            st.error("No fue posible ingresar. Revisa tus credenciales o espera si la cuenta está bloqueada.")
        st.caption("Demo local · después de 5 fallos, la cuenta se bloquea por 5 minutos.")


if "username" not in st.session_state:
    login()
    st.stop()

# Reconsulta el perfil en cada ejecución para aplicar revocaciones y cambios de alcance.
profile = get_profile(st.session_state["username"])
if profile is None or time.time() - st.session_state.get("login_time", 0) > 3600:
    logout()
    st.rerun()

with st.sidebar:
    st.subheader("Portal comercial")
    st.write(profile.name)
    st.badge(profile.role.capitalize())
    if profile.role in {"gerente", "analista"}:
        st.caption("Alcance: todas las ventas")
    elif profile.role == "agente":
        st.caption(f"Alcance: {profile.agent_id}")
    else:
        for label, values in [("Equipos", profile.teams), ("Sectores", profile.sectors), ("Regiones", profile.regions)]:
            if values:
                st.caption(f"{label}: {', '.join(values)}")
    st.button("Cerrar sesión", key="logout", on_click=logout, width="stretch")
    st.divider()

try:
    all_sales, metadata = load_sales()
except (ValueError, OSError) as exc:
    st.error(f"No se pudo cargar el reporte: {exc}")
    st.stop()

# Único punto de entrada al reporte: jamás alimentar widgets o exportaciones con all_sales.
sales = authorized_sales(all_sales, profile)
del all_sales
titles = {"gerente": ("Resumen gerencial", "Una visión global del desempeño y la contribución comercial."),
          "analista": ("Exploración de ventas", "Desglosa resultados y consulta cada operación."),
          "supervisor": ("Desempeño de mi segmento", "Sigue los resultados de los agentes dentro de tu alcance."),
          "agente": ("Mis resultados", "Consulta tu evolución y el detalle de tus ventas.")}
title, subtitle = titles[profile.role]
st.caption("VENTAS / " + profile.role.upper())
st.title(title)
st.write(subtitle)
st.caption(metadata["source"])
if metadata.get("synthetic_data"):
    st.info("Ventas, costos, clientes y agentes sintéticos para demostrar el reporte. Cada agente mantiene su zona, región, sector y cartera; los resultados no corresponden a ventas reales.")
if metadata.get("simulated_assignments"):
    st.info("Agentes y equipos simulados para demostrar el acceso. Importes estimados con precios de catálogo; moneda no declarada por la fuente. No hay costos para calcular margen.")
report_tab, directory_tab = st.tabs(["Reporte de ventas", "Mi ficha" if profile.role == "agente" else "Directorio de agentes"],
                                   key="workspace_tab", on_change="rerun")
if sales.empty:
    with directory_tab:
        render_directory(profile)
    with report_tab:
        st.info("No hay ventas disponibles dentro de tu perfil de acceso.")
    st.stop()

# Cambiar la fuente no debe conservar fechas o segmentos incompatibles de la anterior.
source_signature = (metadata["source"], len(sales), str(sales.fecha.min()), str(sales.fecha.max()), profile.username)
if st.session_state.get("sales_source_signature") != source_signature:
    for key in ["report_period", "comparison_reference", "filter_equipo", "filter_sector", "filter_region", "filter_agente_id", "filter_producto"]:
        st.session_state.pop(key, None)
    st.session_state["sales_source_signature"] = source_signature

with st.sidebar:
    st.subheader("Filtrar resultados")
    def reset_period():
        st.session_state.pop("report_period", None)

    preset = st.selectbox("Rango rápido", ["Todo el historial", "Últimos 30 días", "Últimos 90 días"], key="period_preset", on_change=reset_period)
    last = sales.fecha.max().date()
    first = sales.fecha.min().date() if preset == "Todo el historial" else max(sales.fecha.min().date(), last - pd.Timedelta(days=29 if preset == "Últimos 30 días" else 89))
    dates = st.date_input("Período", value=(first, last), key="report_period",
                          min_value=sales.fecha.min().date(), max_value=sales.fecha.max().date())
    selected = {}
    for column, label in [("equipo", "Equipo"), ("sector", "Sector"), ("region", "Región"), ("agente_id", "Agente"), ("producto", "Producto")]:
        selected[column] = st.multiselect(label, sorted(sales[column].unique()), key=f"filter_{column}")

if len(dates) != 2:
    st.info("Selecciona una fecha inicial y una final.")
    st.stop()
segment = sales.copy()
for column, values in selected.items():
    if values:
        segment = segment[segment[column].isin(values)]
filtered = segment[segment.fecha.between(pd.Timestamp(dates[0]), pd.Timestamp(dates[1]))].copy()
with directory_tab:
    render_directory(profile, filtered, metadata, dates, money)
with report_tab:
    if filtered.empty:
        st.info("No hay ventas para los filtros seleccionados.")
        st.stop()

    revenue = filtered.venta_neta.sum()
    previous, previous_start, previous_end, comparable = previous_period(segment, dates[0], dates[1])
    has_costs = filtered.costo.notna().all()
    margin = filtered.margen.sum() if has_costs else None
    cards = st.columns(4)
    cards[0].metric(f"{metadata['revenue_label']} · {metadata['currency']}", money(revenue), delta=percent_change(revenue, previous.venta_neta.sum(), comparable))
    cards[1].metric("Margen bruto", money(margin) if has_costs else "Sin costos", help="Venta neta menos costo; solo se calcula si todas las filas tienen costo.")
    cards[2].metric("Margen sobre ventas", f"{margin/revenue:.1%}" if has_costs and revenue else "—")
    cards[3].metric("Operaciones", f"{len(filtered):,}".replace(",", "."), delta=percent_change(len(filtered), len(previous), comparable), help="Cada fila representa una operación; no se deducen pedidos únicos.")
    extra = st.columns(4)
    extra[0].metric("Clientes activos", str(filtered.cliente_id.nunique()), delta=percent_change(filtered.cliente_id.nunique(), previous.cliente_id.nunique(), comparable))
    extra[1].metric("Unidades vendidas", f"{int(filtered.unidades.sum()):,}".replace(",", "."), delta=percent_change(filtered.unidades.sum(), previous.unidades.sum(), comparable))
    extra[2].metric("Importe por operación", money(revenue / len(filtered)))
    extra[3].metric("Productos vendidos", str(filtered.producto.nunique()))
    if comparable:
        st.caption(f"Variaciones frente al {previous_start:%d/%m/%Y} — {previous_end:%d/%m/%Y}, con los mismos filtros y alcance. Sin variación porcentual cuando la base es cero.")
    else:
        st.caption("Sin comparación porcentual: el historial del segmento no cubre todo el período anterior equivalente. Prueba un rango rápido más corto.")
    st.caption(f"{dates[0]:%d/%m/%Y} — {dates[1]:%d/%m/%Y} · {filtered.agente_id.nunique()} agentes · {int(filtered.unidades.sum())} unidades")

    left, right = st.columns([1.6, 1])
    with left:
        st.subheader("Evolución mensual")
        value_columns = ["venta_neta", "margen"] if has_costs else ["venta_neta"]
        monthly = filtered.assign(mes=filtered.fecha.dt.to_period("M").astype(str)).groupby("mes")[value_columns].sum()
        st.line_chart(monthly, color=["#167D8D", "#E6A23C"] if has_costs else ["#167D8D"])
    with right:
        axis = "equipo" if profile.role == "gerente" else "agente_id" if profile.role == "supervisor" else "producto"
        st.subheader({"equipo": "Contribución por equipo", "agente_id": "Ventas por agente", "producto": "Ventas por producto"}[axis])
        st.bar_chart(filtered.groupby(axis).venta_neta.sum().sort_values(ascending=False), color="#167D8D")

    insights(filtered, profile.role, metadata, money)
    if profile.role == "analista":
        period_comparator(segment, filtered, dates, metadata, money)

    if profile.role == "gerente":
        st.subheader("Resultados por equipo y región")
        summary = filtered.groupby(["equipo", "region"], as_index=False).agg(venta_neta=("venta_neta", "sum"), margen=("margen", "sum"), operaciones=("venta_id", "count"))
        if not has_costs:
            summary = summary.drop(columns="margen")
        st.dataframe(summary, hide_index=True, width="stretch")
        download = summary
    else:
        if profile.role == "supervisor":
            st.subheader("Resumen del equipo")
            agent_summary = filtered.groupby("agente_id", as_index=False).agg(venta_neta=("venta_neta", "sum"), margen=("margen", "sum"), operaciones=("venta_id", "count"))
            st.dataframe(agent_summary if has_costs else agent_summary.drop(columns="margen"), hide_index=True, width="stretch")
        st.subheader("Detalle de operaciones")
        st.dataframe(filtered, hide_index=True, width="stretch")
        download = filtered
    st.download_button("Descargar resumen CSV" if profile.role == "gerente" else "Descargar detalle CSV",
                       export_csv(download), file_name=f"ventas_{profile.role}.csv", mime="text/csv")
