import re
import textwrap
from pathlib import Path
from io import StringIO
from datetime import datetime

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np


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


def nombre_archivo_seguro(nombre):
    """Normaliza un nombre para utilizarlo en rutas y archivos."""
    nombre = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", str(nombre))
    nombre = re.sub(r"\s+", "_", nombre).strip(" ._")
    nombre = nombre[:100] or "dataset"

    reservados = {
        "CON", "PRN", "AUX", "NUL",
        *(f"COM{i}" for i in range(1, 10)),
        *(f"LPT{i}" for i in range(1, 10)),
    }

    if nombre.split(".")[0].upper() in reservados:
        nombre = f"dataset_{nombre}"

    return nombre


def inspeccion_visual_md(df, nombre="dataset", carpeta_base="reports/eda"):
    """
    Genera un informe Markdown y gráficos de inspección de un DataFrame.

    Incluye dimensiones, tipos, cardinalidad, nulos, duplicados,
    primeras filas, información, estadísticas, histogramas y correlación.

    No modifica el DataFrame original.
    Los arrays y listas se comparan por su contenido completo y en orden.
    Las estadísticas de esas columnas describen combinaciones completas,
    no sus elementos internos.

    Args:
        df (pd.DataFrame): DataFrame que se desea inspeccionar.
        nombre (str): Nombre del dataset.
        carpeta_base (str o Path): Directorio donde guardar los informes.

    Returns:
        Path: Ruta del archivo Markdown generado.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df debe ser un pandas.DataFrame.")

    total, cantidad_columnas = df.shape

    # Copia auxiliar para cardinalidad, duplicados y estadísticas.
    df_conteo = df.copy()

    for posicion, dtype in enumerate(df.dtypes):
        if pd.api.types.is_object_dtype(dtype):
            columna = df.iloc[:, posicion].map(convertir_a_hashable)
            df_conteo.isetitem(posicion, columna)

    cardinalidad = (
        df_conteo.nunique()
        if cantidad_columnas
        else pd.Series(dtype="int64")
    )

    # Una versión vigente por dataset; la fecha se conserva dentro del informe.
    nombre_seguro = nombre_archivo_seguro(nombre)
    fecha = datetime.now().strftime("%Y-%m-%d_%H-%M-%S_%f")

    carpeta = Path(carpeta_base) / nombre_seguro
    carpeta.mkdir(parents=True, exist_ok=True)

    prefijo = nombre_seguro
    path_md = carpeta / f"inspeccion_{prefijo}.md"
    # Retirar únicamente imágenes generadas por este informe para evitar
    # histogramas obsoletos cuando cambian las columnas de entrada.
    for imagen in [*carpeta.glob(f"{prefijo}_hist_*.png"), carpeta / f"{prefijo}_correlacion.png"]:
        if imagen.is_file() and imagen.resolve().parent == carpeta.resolve():
            imagen.unlink()

    # Datos numéricos reales para gráficos.
    df_numerico = df.select_dtypes(include="number")

    posiciones_reales = [
        posicion
        for posicion, dtype in enumerate(df_numerico.dtypes)
        if not pd.api.types.is_complex_dtype(dtype)
    ]

    df_graficos = (
        df_numerico.iloc[:, posiciones_reales]
        .astype(float)
        .replace([np.inf, -np.inf], np.nan)
    )

    posiciones_con_datos = [
        posicion
        for posicion in range(df_graficos.shape[1])
        if df_graficos.iloc[:, posicion].notna().any()
    ]

    with path_md.open("w", encoding="utf-8") as f:

        def escribir_bloque(texto):
            # Ajusta el delimitador si el contenido contiene backticks.
            texto = str(texto)
            secuencias = re.findall(r"`+", texto)
            longitud = max(
                3,
                max((len(item) for item in secuencias), default=0) + 1,
            )
            delimitador = "`" * longitud
            f.write(f"{delimitador}text\n{texto}\n{delimitador}\n\n")

        f.write("# Inspección visual del dataset\n\n")
        f.write(f"Generado: {fecha}. Esta versión reemplaza el informe anterior.\n\n")
        escribir_bloque(nombre)

        # 1 - Dimensiones
        dimensiones = (
            f"{total:,} filas y {cantidad_columnas:,} columnas."
        ).replace(",", ".")

        f.write("## Dimensiones\n\n")
        f.write(f"{dimensiones}\n\n")

        # 2 - Columnas
        columnas_texto = textwrap.fill(
            ", ".join(str(col) for col in df.columns),
            width=80,
        )

        f.write("## Columnas y tipos\n\n")
        f.write(f"Cantidad de columnas: {cantidad_columnas}\n\n")
        escribir_bloque(columnas_texto)

        f.write("Tipos de datos:\n\n")
        escribir_bloque(df.dtypes.astype(str).to_string())

        # 3 - Cardinalidad
        f.write("## Cardinalidad\n\n")
        f.write(
            "Cantidad de valores distintos no nulos por columna. "
            "Los arrays y listas se cuentan como combinaciones completas.\n\n"
        )
        escribir_bloque(
            cardinalidad.sort_values(ascending=False).to_string()
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

        f.write("## Valores nulos\n\n")
        f.write(
            "Se cuentan celdas nulas; no los valores nulos "
            "dentro de arrays o listas.\n\n"
        )
        escribir_bloque(resumen_nulos.to_string())

        # 5 - Duplicados
        duplicados = (
            int(df_conteo.duplicated().sum())
            if total and cantidad_columnas
            else 0
        )
        porcentaje_duplicados = (
            duplicados / total * 100 if total else 0
        )

        f.write("## Duplicados\n\n")
        f.write(
            f"Total de filas duplicadas después de la primera aparición: "
            f"{duplicados} ({porcentaje_duplicados:.2f}%).\n\n"
        )

        resumen_unicos = pd.DataFrame({
            "Valores distintos no nulos": cardinalidad,
            "Registros": total,
            "Porcentaje (%)": (
                (cardinalidad / total * 100).round(2)
                if total
                else cardinalidad.astype(float)
            ),
        })

        escribir_bloque(resumen_unicos.to_string())

        # 6 - Primeras filas
        f.write("## Primeras filas\n\n")
        escribir_bloque(df.head().astype(str).to_string())

        # 7 - Información
        info_buffer = StringIO()
        df.info(buf=info_buffer)

        f.write("## Información\n\n")
        escribir_bloque(info_buffer.getvalue().rstrip())

        # 8 - Estadísticas
        f.write("## Estadísticas descriptivas\n\n")

        if total and cantidad_columnas:
            f.write(
                "En columnas con arrays o listas, los conteos y "
                "frecuencias corresponden a combinaciones completas.\n\n"
            )
            escribir_bloque(
                df_conteo.describe(include="all").to_string()
            )
        else:
            f.write(
                "No hay datos suficientes para calcular estadísticas.\n\n"
            )

        # 9 - Histogramas
        f.write("## Histogramas numéricos\n\n")

        if posiciones_con_datos:
            for posicion in posiciones_con_datos:
                columna = df_graficos.columns[posicion]
                valores = df_graficos.iloc[:, posicion].dropna()

                # La posición diferencia columnas con nombres repetidos.
                nombre_imagen = f"{prefijo}_hist_{posicion + 1}.png"
                img_path = carpeta / nombre_imagen

                fig, ax = plt.subplots(figsize=(6, 4))

                try:
                    ax.hist(valores, bins=30)
                    ax.set_title(f"Histograma de {columna}")
                    ax.set_xlabel(str(columna))
                    ax.set_ylabel("Frecuencia")

                    fig.tight_layout()
                    fig.savefig(img_path, dpi=150, bbox_inches="tight")
                finally:
                    plt.close(fig)

                escribir_bloque(f"Columna: {columna}")
                f.write(f"![Histograma]({nombre_imagen})\n\n")
        else:
            f.write(
                "No hay columnas numéricas con valores finitos "
                "para mostrar histogramas.\n\n"
            )

        # 10 - Matriz de correlación
        f.write("## Matriz de correlación\n\n")

        if len(posiciones_con_datos) > 1 and total > 1:
            datos_corr = df_graficos.iloc[:, posiciones_con_datos]
            correlacion = datos_corr.corr()

            if correlacion.notna().to_numpy().any():
                nombre_corr = f"{prefijo}_correlacion.png"
                img_corr_path = carpeta / nombre_corr

                fig_corr, ax = plt.subplots(figsize=(10, 8))

                try:
                    sns.heatmap(
                        correlacion,
                        annot=True,
                        fmt=".2f",
                        cmap="coolwarm",
                        linewidths=0.5,
                        vmin=-1,
                        vmax=1,
                        center=0,
                        ax=ax,
                    )

                    ax.set_title("Matriz de correlación")
                    ax.set_xticklabels(
                        ax.get_xticklabels(),
                        rotation=45,
                        ha="right",
                    )
                    ax.set_yticklabels(
                        ax.get_yticklabels(),
                        rotation=0,
                    )

                    fig_corr.tight_layout()
                    fig_corr.savefig(
                        img_corr_path,
                        dpi=150,
                        bbox_inches="tight",
                    )
                finally:
                    plt.close(fig_corr)

                f.write(
                    f"![Matriz de correlación]({nombre_corr})\n\n"
                )
            else:
                f.write(
                    "No se pudieron calcular correlaciones. "
                    "Revisa si las columnas son constantes o tienen "
                    "pocos valores válidos.\n\n"
                )
        else:
            f.write(
                "Se necesitan al menos dos columnas numéricas "
                "con datos y dos filas para calcular correlaciones.\n\n"
            )

    print(f"Archivo Markdown generado en: {path_md.resolve()}")
    return path_md
