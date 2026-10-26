import pandas as pd
import unicodedata
import re
import textwrap

def limpiar_columnas(df, verbose=False):
    """
    Elimina columnas cuyo nombre empiece con 'Unnamed' y normaliza los nombres
    de las columnas:
        - Quita espacios en blanco.
        - Convierte a minúsculas.
        - Elimina caracteres especiales como paréntesis, comillas dobles y simples.
        - Reemplaza espacios por guiones bajos.

    Parámetros:
        - verbose: si es True, imprime nombres antes y después.
    """
    original_columns = df.columns.tolist()

    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

    df.columns = (
        df.columns
        .str.strip() # elimina espacios al inicio y final
        .str.lower() # convierte a minúsculas
        .str.replace(r'[()"\']', '', regex=True) # elimina paréntesis, comillas dobles y simples
        .str.replace(' ', '_') # reemplaza espacios por guiones bajos
    )

    if verbose:
        print("Columnas originales:")
        print(original_columns)
        print("\nColumnas normalizadas:")
        print(df.columns.tolist())

    return df


def normalize_text(text, lower=True):
    """
    Normaliza una cadena de texto:
        - Normaliza codificación Unicode.
        - Elimina caracteres no ASCII.
        - Elimina caracteres especiales (como (, ), ', ", etc.).
        - Convierte a minúsculas o mayúsculas según parámetro 'lower'.
        - Elimina espacios extra.
    """
    if not isinstance(text, str):
        return text

    text = unicodedata.normalize('NFKD', text) # normaliza Unicode
    text = text.encode('ascii', 'ignore').decode('utf-8') # elimina caracteres no ASCII
    text = re.sub(r'\s+', ' ', text)     # reemplaza saltos de línea/tabs por espacio
    text = re.sub(r'[^\w\s]', '', text) # elimina caracteres especiales
    text = text.strip() # elimina espacios al inicio y final
    text = re.sub(r'\s+', ' ', text)     # reemplaza tabs, \n, múltiples espacios por uno solo
    return text.lower() if lower else text.upper()


def limpiar_valores_texto(df, lower=True):
    """
    Aplica la función de normalización a todas las columnas de texto (tipo object)
    del DataFrame.

    Parámetros:
        - lower: si es True, convierte a minúsculas; si False, a mayúsculas.
    """
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].apply(lambda x: normalize_text(x, lower=lower))
    return df


def wrapped_print(text, width=100):
    """
    Imprime una lista de elementos en bloques de texto ajustados a un ancho específico.

    Esta función convierte cada elemento de la lista en una cadena, une los elementos con comas,
    y luego imprime el texto resultante en bloques de longitud máxima especificada por el parámetro `ancho`.

    Args:
        lista (list): Lista de elementos que se desea imprimir. Los elementos deben ser convertibles a cadenas.
        ancho (int, optional): Ancho máximo de cada línea impresa. Por defecto es 80 caracteres.

    Returns:
        None: La función no retorna ningún valor, solo imprime el resultado en la consola.
    """
    if isinstance(text, (list, pd.Index)):
        print(textwrap.fill(', '.join(map(str, text)), width=width))
    elif isinstance(text, str):
        print(textwrap.fill(text, width=width))
    else:
        print(text)
