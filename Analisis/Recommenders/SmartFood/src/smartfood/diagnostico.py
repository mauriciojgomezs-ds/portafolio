import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.axes import Axes


def wrapped_print(lista, ancho=80):
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
    texto = ', '.join(map(str, lista))
    for i in range(0, len(texto), ancho):
        print(texto[i:i+ancho])


def ejecutar_diagnostico(df, diagnosticos, nombre_dataset="dataset"):
    print(f"📊 Diagnóstico de `{nombre_dataset}`\n" + "="*60)
    
    for clave, diagnostico in diagnosticos.items():
        print(f"📌 {diagnostico['pregunta']}")
        
        try:
            resultado = diagnostico['funcion'](df)
            # print(f"[DEBUG] Resultado tipo: {type(resultado)}")

            if resultado is None:
                # print("[DEBUG] Resultado es None")
                mensaje = diagnostico.get("mensaje_si_vacio", "✅ No se encontraron resultados relevantes.")
                print(mensaje)

            elif hasattr(resultado, 'empty') and resultado.empty:
                # print("[DEBUG] Resultado tiene atributo .empty y está vacío")
                mensaje = diagnostico.get("mensaje_si_vacio", "✅ No se encontraron resultados relevantes.")
                print(mensaje)

            elif isinstance(resultado, Axes):
                # print("[DEBUG] Resultado es un gráfico de matplotlib")
                plt.show()

            elif isinstance(resultado, pd.DataFrame):
                # print("[DEBUG] Resultado es un DataFrame")
                print(resultado.to_string())

            elif isinstance(resultado, pd.Series):
                # print("[DEBUG] Resultado es una Series")
                print(resultado.to_string())

            elif isinstance(resultado, (list, pd.Index)):
                if len(resultado) == 0:
                    # print("[DEBUG] Resultado es lista o Index vacío")
                    mensaje = diagnostico.get("mensaje_si_vacio", "✅ No se encontraron resultados relevantes.")
                    print(mensaje)
                else:
                    # print("[DEBUG] Resultado es lista o Index no vacío")
                    wrapped_print(resultado)

            else:
                # print("[DEBUG] Resultado es otro tipo")
                print(resultado)

        except Exception as e:
            print(f"⚠️ Error al ejecutar {clave}: {e}")
        
        print("-" * 60)


