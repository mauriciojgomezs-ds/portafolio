import io
import zipfile

import pandas as pd
import pytest

from sales_access.kaggle_import import transform


def archive(duplicate_conflict=False):
    content = io.BytesIO()
    with zipfile.ZipFile(content, "w") as z:
        sales = "ID_Venta,Fecha,ID_Cliente,ID_Producto,Cantidad,Método_Pago,Estado\n1,1/2/2024,4,1,2,1,Completa\n1,1/2/2024,4,1,2,1,Completa\n2,2/2/2024,5,1,1,1,Pendiente\n3,3/2/2024,5,1,3,1,Completa\n"
        if duplicate_conflict:
            sales += "1,1/2/2024,4,1,8,1,Completa\n"
        for name, text in [("ventas.csv", sales), ("productos.csv", 'ID_Producto,Nombre_producto,Categoría,Precio_Unitario,Stock\n1,Leche,Lácteos,"12,24",100\n'),
                           ("clientes.csv", "ID_Cliente,Región\n4,Patagonia\n5,Centro\n")]:
            z.writestr(name, text.encode("cp1252"))
    content.seek(0)
    return zipfile.ZipFile(content)


def test_import_cleaning_and_honest_amounts():
    with archive() as z:
        data, metadata = transform(z)
    assert len(data) == 2
    assert metadata["exact_duplicates_removed"] == 1
    assert metadata["non_complete_excluded"] == 1
    assert data.venta_neta.tolist() == [24.48, 36.72]
    assert set(data.agente_id) == {"agente_1", "agente_2"}
    assert set(data.equipo) == {"Norte", "Sur"}
    assert data.costo.isna().all() and data.margen.isna().all()
    assert data.fecha.min() == pd.Timestamp("2024-02-01")
    assert "Lácteos" in set(data.sector)


def test_conflicting_sale_ids_rejected():
    with archive(True) as z, pytest.raises(ValueError, match="contenido diferente"):
        transform(z)
