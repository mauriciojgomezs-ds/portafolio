"""Identidades de demostración vinculadas por ID, sin información personal real."""
from html import escape

import pandas as pd
import streamlit as st

from .data import agent_roster
from .security import authorized_sales


NAMES = ["Camila", "Diego", "Valentina", "Matías", "Francisca", "Sebastián", "Catalina", "Tomás",
         "Javiera", "Nicolás", "Antonia", "Felipe", "Constanza", "Benjamín", "Paula", "Gabriel",
         "Daniela", "Vicente", "Fernanda", "Ignacio", "Isidora", "Joaquín", "Carolina", "Alonso",
         "María", "Cristóbal", "Sofía", "Andrés", "Josefina", "Pablo", "Trinidad", "Martín",
         "Amanda", "Rodrigo", "Emilia", "Esteban", "Renata", "Simón", "Mariana", "Lucas"]
SURNAMES = ["Rojas", "Muñoz", "Soto", "Vargas", "Silva", "Torres", "Flores", "Díaz",
            "Castro", "Morales", "Reyes", "Herrera", "Navarro", "Fuentes", "Sepúlveda", "Contreras",
            "Araya", "Espinoza", "González", "Pérez", "Medina", "Salazar", "Cortés", "Carrasco",
            "Vega", "Pizarro", "Campos", "Valdés", "Bravo", "Sandoval", "Molina", "Gutiérrez",
            "Ortega", "Figueroa", "Leiva", "Peña", "Vera", "Godoy", "Cáceres", "Bustos"]
BRANCHES = {"Antofagasta": "Antofagasta Centro", "Tarapacá": "Iquique",
            "Atacama": "Copiapó", "Coquimbo": "La Serena", "Biobío": "Concepción",
            "Los Lagos": "Puerto Montt", "La Araucanía": "Temuco", "Los Ríos": "Valdivia"}


def agent_directory():
    records = []
    for index, assignment in enumerate(agent_roster()):
        number = index + 1
        region = assignment["region"]
        records.append({**assignment, "nombre": f"{NAMES[index]} {SURNAMES[index]}",
                        "email": f"agente.{number:02}@ventas.example",
                        "movil": f"+56 9 XXXX {1000+number:04}",
                        "oficina": f"+56 XX XXXX {2000+list(BRANCHES).index(region):04}",
                        "anexo": str(100+number), "sucursal": BRANCHES[region],
                        "iniciales": NAMES[index][0] + SURNAMES[index][0]})
    return pd.DataFrame(records)


def visible_directory(profile):
    # Mismas reglas de autorización que las ventas, incluidos los ejes del supervisor.
    return authorized_sales(agent_directory(), profile)


def agent_labels():
    directory = agent_directory()
    return dict(zip(directory.agente_id, directory.nombre))


def compact_card(record):
    color = "#167D8D" if record["equipo"] == "Norte" else "#6654A2"
    st.markdown(f"""<div style="display:flex;gap:12px;align-items:center;margin:8px 0">
      <div aria-label="Avatar con iniciales" style="background:{color};color:white;min-width:42px;
      width:42px;height:42px;border-radius:50%;display:flex;align-items:center;justify-content:center;
      font-weight:700">{escape(record['iniciales'])}</div>
      <div><strong>{escape(record['nombre'])}</strong><br>
      <span style="font-size:.83rem;color:#526572">{escape(record['sucursal'])} · {escape(record['agente_id'])}</span></div>
    </div>""", unsafe_allow_html=True)


def ranking_cards(frame):
    """Recibe únicamente IDs del ranking ya autorizado."""
    lookup = agent_directory().set_index("agente_id")
    for identifier in frame.agente_id:
        if identifier in lookup.index:
            record = lookup.loc[identifier].to_dict()
            record["agente_id"] = identifier
            compact_card(record)
            st.button(f"Ver ficha de {record['nombre']}", key=f"view_agent_{identifier}",
                      on_click=open_agent, args=(identifier,),
                      help="Abre sus contactos e indicadores en la pestaña Directorio de agentes.")


def open_agent(identifier):
    st.session_state["directory_agent"] = identifier
    st.session_state["workspace_tab"] = "Directorio de agentes"
    st.session_state["directory_zone"] = "Todas las zonas"
    st.session_state["directory_branch"] = "Todas las sucursales"
    st.session_state["directory_search"] = ""


def agent_sales_summary(sales, identifier):
    own = sales.loc[sales.agente_id.eq(identifier)]
    if own.empty:
        return None
    revenue = own.venta_neta.sum()
    return {"importe": revenue, "margen": own.margen.sum() if own.costo.notna().all() else None,
            "operaciones": len(own), "clientes": own.cliente_id.nunique(),
            "unidades": int(own.unidades.sum()), "importe_por_operacion": revenue / len(own)}


def render_directory(profile, sales=None, metadata=None, dates=None, money=None):
    visible = visible_directory(profile)
    if visible.empty:
        return
    title = "Mi ficha comercial" if profile.role == "agente" else f"Directorio de agentes · {len(visible)} en tu alcance"
    with st.container(border=True):
        st.subheader(title)
        st.caption("Identidades y contactos ficticios de demostración · avatares con iniciales · teléfonos de ejemplo.")
        if profile.role == "agente":
            record = visible.iloc[0]
        else:
            full_count = len(visible)
            left, right = st.columns(2)
            zones = ["Todas las zonas"] + sorted(visible.equipo.unique())
            if st.session_state.get("directory_zone", "Todas las zonas") not in zones:
                st.session_state.pop("directory_zone", None)
            zone = left.selectbox("Zona del directorio", zones, key="directory_zone")
            if zone != "Todas las zonas":
                visible = visible[visible.equipo.eq(zone)]
            branches = ["Todas las sucursales"] + sorted(visible.sucursal.unique())
            if st.session_state.get("directory_branch", "Todas las sucursales") not in branches:
                st.session_state.pop("directory_branch", None)
            branch = right.selectbox("Sucursal del directorio", branches, key="directory_branch")
            if branch != "Todas las sucursales":
                visible = visible[visible.sucursal.eq(branch)]
            search = st.text_input("Buscar por nombre o código", key="directory_search").strip()
            if search:
                import unicodedata
                def normalize(value):
                    return "".join(c for c in unicodedata.normalize("NFD", value.casefold()) if not unicodedata.combining(c))
                query = normalize(search)
                visible = visible[visible.apply(lambda row: query in normalize(f"{row['nombre']} {row['agente_id']}"), axis=1)]
            st.caption(f"{len(visible)} de {full_count} agentes de tu alcance · Los filtros del directorio no cambian el reporte de ventas.")
            if visible.empty:
                st.info("No hay agentes que coincidan con la búsqueda del directorio.")
                return
            lookup = visible.set_index("agente_id")
            options = list(lookup.index)
            if st.session_state.get("directory_agent") not in options:
                st.session_state.pop("directory_agent", None)
            selected = st.selectbox("Consultar agente", options,
                format_func=lambda identifier: f"{lookup.loc[identifier, 'nombre']} · {lookup.loc[identifier, 'sucursal']} · {identifier}",
                key="directory_agent")
            record = visible.loc[visible.agente_id.eq(selected)].iloc[0]
        compact_card(record)
        st.caption(f"Zona {record['equipo']} · {record['region']} · {record['sector']}")
        st.write(f"**Correo:** {record['email']}")
        left, right = st.columns(2)
        left.write(f"**Móvil:** {record['movil']}")
        right.write(f"**Oficina:** {record['oficina']} · **Anexo:** {record['anexo']}")
        st.write(f"**Sucursal:** {record['sucursal']}")
        if sales is not None and metadata is not None:
            st.markdown(f"#### Resumen de ventas · {record['nombre']}")
            if dates:
                st.caption(f"{dates[0]:%d/%m/%Y} — {dates[1]:%d/%m/%Y} · {metadata['currency']} · Respeta todos los filtros actuales del reporte.")
            summary = agent_sales_summary(sales, record["agente_id"])
            if summary is None:
                st.info("Este agente no tiene operaciones con los filtros actuales. Revisa el período y el filtro Agente para consultar sus ventas.")
                return
            format_money = money or (lambda value: f"{value:,.2f}")
            prefix = "$ " if metadata["currency"] == "CLP" else ""
            values = [(metadata["revenue_label"], prefix + format_money(summary["importe"])),
                      ("Margen bruto", prefix + format_money(summary["margen"]) if summary["margen"] is not None else "Sin costos"),
                      ("Operaciones", str(summary["operaciones"])), ("Clientes activos", str(summary["clientes"])),
                      ("Unidades vendidas", str(summary["unidades"])),
                      ("Importe por operación", prefix + format_money(summary["importe_por_operacion"]))]
            columns = st.columns(3)
            for index, (label, value) in enumerate(values):
                with columns[index % 3]:
                    st.caption(label)
                    st.markdown(f"**{value}**")
