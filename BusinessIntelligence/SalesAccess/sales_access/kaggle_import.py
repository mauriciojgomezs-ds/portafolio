"""Adaptación explícita del dataset dataregina, sin costos inventados."""
import io
import zipfile

import pandas as pd

from .data import COLUMNS, validate


def transform(archive: zipfile.ZipFile):
    def read(name):
        raw = archive.read(name)
        try:
            text = raw.decode("utf-8-sig")
        except UnicodeDecodeError:
            text = raw.decode("cp1252")
        return pd.read_csv(io.StringIO(text))

    sales, products, clients = read("ventas.csv"), read("productos.csv"), read("clientes.csv")
    before = len(sales)
    sales = sales.drop_duplicates()
    duplicates = before - len(sales)
    excluded = int(sales.Estado.ne("Completa").sum())
    sales = sales.loc[sales.Estado.eq("Completa")].copy()
    if sales.ID_Venta.duplicated().any():
        raise ValueError("Hay ID_Venta repetidos con contenido diferente; revisar manualmente.")
    merged = sales.merge(products, on="ID_Producto", how="left", validate="many_to_one").merge(
        clients[["ID_Cliente", "Región"]], on="ID_Cliente", how="left", validate="many_to_one")
    if merged[["Nombre_producto", "Precio_Unitario", "Categoría", "Región"]].isna().any().any():
        raise ValueError("Ventas sin producto o cliente válido.")
    price = pd.to_numeric(merged.Precio_Unitario.astype(str).str.replace(",", ".", regex=False), errors="raise")
    amount = pd.to_numeric(merged.Cantidad, errors="raise")
    agent_number = pd.to_numeric(merged.ID_Cliente, errors="raise").astype(int).mod(4) + 1
    data = pd.DataFrame({
        "venta_id": merged.ID_Venta.astype(str),
        "fecha": pd.to_datetime(merged.Fecha, format="%d/%m/%Y").dt.strftime("%Y-%m-%d"),
        "agente_id": "agente_" + agent_number.astype(str),
        "equipo": agent_number.map({1: "Norte", 2: "Sur", 3: "Norte", 4: "Sur"}),
        "sector": merged["Categoría"], "region": merged["Región"],
        "producto": merged.Nombre_producto, "cliente_id": merged.ID_Cliente.astype(str),
        "unidades": amount, "venta_neta": (amount * price).round(2), "costo": float("nan")})
    metadata = {
        "source": "Kaggle · DataRegina · ventas completas · agentes/equipos simulados · importes estimados",
        "currency": "U.M. (fuente sin moneda declarada)", "revenue_label": "Importe estimado",
        "url": "https://www.kaggle.com/datasets/dataregina/datasets-para-proyecto-bi",
        "license": "CC BY-NC-SA 4.0", "simulated_assignments": True,
        "exact_duplicates_removed": duplicates, "non_complete_excluded": excluded,
        "input_rows": before, "output_rows": len(data),
        "assignment_rule": "agente = (ID_Cliente % 4) + 1; agentes 1/3 Norte; 2/4 Sur",
        "amount_rule": "Cantidad * Precio_Unitario del catálogo; no es facturación histórica confirmada"}
    return validate(data[COLUMNS]), metadata
