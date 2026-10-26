import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from IPython.display import display
from io import StringIO
import contextlib
import textwrap
import ipywidgets as widgets
import numpy as np
import html


def convertir_a_hashable(valor):
    """Convierte estructuras anidadas en valores aptos para conteos."""
    if isinstance(valor, np.ndarray):
        return convertir_a_hashable(valor.tolist())

    if isinstance(valor, (list, tuple)):
        return tuple(convertir_a_hashable(item) for item in valor)

    if isinstance(valor, dict):
        return frozenset(
            (
                convertir_a_hashable(clave),
                convertir_a_hashable(item),
            )
            for clave, item in valor.items()
        )

    if isinstance(valor, (set, frozenset)):
        return frozenset(convertir_a_hashable(item) for item in valor)

    return valor


def inspeccion_visual(df):
    """
    Muestra una inspección interactiva de un DataFrame en Jupyter.

    Incluye dimensiones, columnas, cardinalidad, nulos, duplicados,
    primeras filas, información, estadísticas, histogramas y correlación.

    Los arrays y listas se comparan por su contenido completo y en orden.
    Los diccionarios y conjuntos se comparan sin considerar su orden.
    El DataFrame original no se modifica.

    La cardinalidad excluye valores nulos de nivel superior.
    Las estadísticas de columnas con arrays describen combinaciones
    completas, no sus elementos internos.

    Args:
        df (pd.DataFrame): DataFrame que se desea inspeccionar.

    Returns:
        None.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df debe ser un pandas.DataFrame.")

    def bloque_texto(texto):
        return widgets.HTML(
            value=f"<pre>{html.escape(str(texto))}</pre>"
        )

    def tabla_html(tabla):
        return widgets.HTML(
            value=tabla.to_html(escape=True, border=0)
        )

    # Copia auxiliar: convierte estructuras en las columnas object.
    df_conteo = df.copy()

    for posicion, dtype in enumerate(df.dtypes):
        if pd.api.types.is_object_dtype(dtype):
            columna = df.iloc[:, posicion].map(convertir_a_hashable)
            df_conteo.isetitem(posicion, columna)

    total = len(df)
    cantidad_columnas = df.shape[1]

    if cantidad_columnas:
        cardinalidad = df_conteo.nunique()
    else:
        cardinalidad = pd.Series(dtype="int64")

    tabs_content = {}

    # 1 - Dimensiones
    dimensiones = (
        f"Dimensiones del dataset: {total:,} filas (registros) "
        f"y {cantidad_columnas:,} columnas."
    ).replace(",", ".")

    tabs_content["Dimensiones"] = bloque_texto(dimensiones)

    # 2 - Columnas
    nombres = ", ".join(str(col) for col in df.columns)
    nombres = textwrap.fill(nombres, width=80)
    tipos = df.dtypes.astype(str).to_string()

    resumen_columnas = (
        f"Columnas ({cantidad_columnas}):\n{nombres}"
        f"\n\nTipos de datos:\n{tipos}"
    )

    tabs_content["Columnas"] = bloque_texto(resumen_columnas)

    # 3 - Cardinalidad
    cardinalidad_ordenada = cardinalidad.sort_values(ascending=False)

    tabs_content["Cardinalidad"] = bloque_texto(
        "Valores distintos no nulos por columna:\n\n"
        + cardinalidad_ordenada.to_string()
    )

    # 4 - Valores nulos
    nulos = df.isna().sum()
    porcentaje_nulos = (
        (nulos / total * 100).round(2)
        if total
        else nulos.astype(float)
    )

    resumen_nulos = pd.DataFrame({
        "Nulos": nulos,
        "Porcentaje (%)": porcentaje_nulos,
    })

    tabs_content["Valores nulos"] = tabla_html(resumen_nulos)

    # 5 - Duplicados
    duplicados = (
        int(df_conteo.duplicated().sum())
        if total and cantidad_columnas
        else 0
    )

    porcentaje_duplicados = (
        duplicados / total * 100 if total else 0
    )

    texto_duplicados = [
        f"Cantidad de registros 100% duplicados: "
        f"{duplicados} ({porcentaje_duplicados:.2f}%)",
        "\n\nPor columna:",
    ]

    for columna, distintos in cardinalidad.items():
        porcentaje = distintos / total * 100 if total else 0

        texto_duplicados.append(
            f"\n - {columna}: {distintos} valores distintos no nulos "
            f"de {total} registros ({porcentaje:.2f}%)"
        )

    tabs_content["Duplicados"] = bloque_texto(
        "".join(texto_duplicados)
    )

    # 6 - Primeras filas
    tabs_content["Primeras filas"] = tabla_html(
        df.head().astype(str)
    )

    # 7 - Información
    info_buffer = StringIO()
    df.info(buf=info_buffer)

    tabs_content["Información"] = bloque_texto(
        info_buffer.getvalue()
    )

    # 8 - Estadísticas
    if total and cantidad_columnas:
        estadisticas = df_conteo.describe(include="all")
        tabs_content["Estadísticas"] = tabla_html(estadisticas)
    else:
        tabs_content["Estadísticas"] = bloque_texto(
            "No hay datos suficientes para calcular estadísticas."
        )

    # Selección de columnas numéricas para los gráficos.
    df_numerico = df.select_dtypes(include="number")

    # Los gráficos y correlaciones se calculan sobre números reales.
    posiciones_reales = [
        posicion
        for posicion, dtype in enumerate(df_numerico.dtypes)
        if not pd.api.types.is_complex_dtype(dtype)
    ]

    df_numerico = df_numerico.iloc[:, posiciones_reales]

    # Conversión auxiliar para gráficos y valores no finitos.
    df_graficos = df_numerico.astype(float).replace(
        [np.inf, -np.inf], np.nan
    )

    posiciones_con_datos = [
        posicion
        for posicion in range(df_graficos.shape[1])
        if df_graficos.iloc[:, posicion].notna().any()
    ]

    # 9 - Histogramas
    if posiciones_con_datos:
        cantidad = len(posiciones_con_datos)
        columnas_grafico = min(4, cantidad)
        filas_grafico = int(np.ceil(cantidad / columnas_grafico))

        fig, axes = plt.subplots(
            nrows=filas_grafico,
            ncols=columnas_grafico,
            figsize=(4 * columnas_grafico, 4 * filas_grafico),
            squeeze=False,
        )

        axes = axes.ravel()

        for indice, posicion in enumerate(posiciones_con_datos):
            columna = df_graficos.columns[posicion]
            valores = df_graficos.iloc[:, posicion].dropna()

            axes[indice].hist(valores, bins=30)
            axes[indice].set_title(f"Histograma de {columna}")
            axes[indice].set_xlabel(str(columna))
            axes[indice].set_ylabel("Frecuencia")

        for indice in range(cantidad, len(axes)):
            axes[indice].axis("off")

        fig.tight_layout()

        salida_histogramas = widgets.Output()
        with salida_histogramas:
            display(fig)

        plt.close(fig)
        tabs_content["Histogramas"] = salida_histogramas

    else:
        tabs_content["Histogramas"] = bloque_texto(
            "No hay columnas numéricas con valores finitos "
            "para mostrar histogramas."
        )

    # 10 - Matriz de correlación
    if len(posiciones_con_datos) > 1 and total > 1:
        datos_correlacion = df_graficos.iloc[:, posiciones_con_datos]
        correlacion = datos_correlacion.corr()

        if correlacion.notna().to_numpy().any():
            fig_corr, ax = plt.subplots(figsize=(12, 10))

            sns.heatmap(
                correlacion,
                annot=True,
                cmap="coolwarm",
                fmt=".2f",
                linewidths=0.5,
                vmin=-1,
                vmax=1,
                center=0,
                ax=ax,
            )

            ax.set_title("Matriz de correlación", fontsize=14)
            ax.set_xticklabels(
                ax.get_xticklabels(),
                rotation=45,
                ha="right",
                fontsize=10,
            )
            ax.set_yticklabels(
                ax.get_yticklabels(),
                rotation=0,
                fontsize=10,
            )

            fig_corr.tight_layout()

            salida_correlacion = widgets.Output()
            with salida_correlacion:
                display(fig_corr)

            plt.close(fig_corr)
            tabs_content["Matriz de correlación"] = salida_correlacion

        else:
            tabs_content["Matriz de correlación"] = bloque_texto(
                "No se pudieron calcular correlaciones. "
                "Revisa si las columnas son constantes o tienen "
                "pocos valores válidos."
            )

    else:
        tabs_content["Matriz de correlación"] = bloque_texto(
            "Se necesitan al menos dos columnas numéricas "
            "con datos y dos filas para calcular correlaciones."
        )

    # Crear y mostrar pestañas
    tab = widgets.Tab(children=list(tabs_content.values()))

    for indice, titulo in enumerate(tabs_content):
        tab.set_title(indice, titulo)

    display(tab)