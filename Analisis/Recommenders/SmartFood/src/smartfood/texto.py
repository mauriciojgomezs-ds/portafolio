"""Preparación del contenido de recetas para los modelos de texto."""

import numpy as np
import pandas as pd


def texto_ingredientes(valor):
    """Convierte listas de ingredientes a texto, conservando los ausentes.

    No utiliza str(lista): evita incluir corchetes y representaciones de nulos.
    Los textos ya preparados se conservan. Los documentos vacíos son ausentes.
    """
    if isinstance(valor, str):
        return valor.strip() or None
    if isinstance(valor, (list, tuple, np.ndarray)):
        if isinstance(valor, np.ndarray) and valor.ndim != 1:
            raise ValueError("Los ingredientes deben ser un arreglo unidimensional.")
        partes = []
        for ingrediente in valor:
            if isinstance(ingrediente, str):
                if ingrediente.strip():
                    partes.append(ingrediente.strip())
            elif not pd.isna(ingrediente):
                raise TypeError("Cada ingrediente debe ser texto o un valor ausente.")
        return " ".join(partes) or None
    if pd.isna(valor):
        return None
    raise TypeError("Se esperaba texto o una lista de ingredientes.")
