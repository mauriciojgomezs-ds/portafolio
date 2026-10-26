import pandas as pd
import numpy as np

# Función para recomendar recetas basadas en el perfil de usuario
def recomendar_por_perfil_usuario(usuario_id, df_reviews, df_recipes, top_n=5):
    """
    Recomienda recetas alineadas al perfil promedio del usuario (calorías y categoría más común).

    Parámetros:
    - usuario_id: ID del usuario.
    - df_reviews: DataFrame con columnas ['authorid', 'recipeid'].
    - df_recipes: DataFrame con columnas ['recipeid', 'calories', 'recipecategory', 'name'].
    - top_n: número de recetas a retornar.

    Retorna:
    - DataFrame con recetas recomendadas.
    """
    # Obtener recetas evaluadas por el usuario
    recetas_usuario = df_reviews[df_reviews["authorid"] == usuario_id]["recipeid"].unique()
    recetas_info = df_recipes[df_recipes["recipeid"].isin(recetas_usuario)]

    if recetas_info.empty:
        print(f"⚠️ No hay recetas evaluadas por el usuario {usuario_id}")
        return pd.DataFrame()

    # Calcular perfil: calorías promedio y categoría más frecuente
    calorias_promedio = recetas_info["calories"].mean()
    categoria_frecuente = recetas_info["recipecategory"].mode().iloc[0] if "recipecategory" in recetas_info.columns else None

    # Filtrar recetas no vistas por el usuario
    recetas_no_vistas = df_recipes[~df_recipes["recipeid"].isin(recetas_usuario)].copy()
    recetas_no_vistas = recetas_no_vistas.dropna(subset=["calories", "recipecategory", "name"])

    # Calcular diferencia de calorías
    recetas_no_vistas["calorias_diff"] = np.abs(recetas_no_vistas["calories"] - calorias_promedio)

    # Filtrar por categoría (opcional)
    recetas_filtradas = recetas_no_vistas[recetas_no_vistas["recipecategory"] == categoria_frecuente]

    # Ordenar por cercanía calórica
    recomendaciones = recetas_filtradas.sort_values("calorias_diff").head(top_n)

    # Mostrar resultados
    print(f"\n📌 Recomendaciones para el usuario {usuario_id} (calorías ~{calorias_promedio:.0f}, categoría: {categoria_frecuente}):")
    for i, row in recomendaciones.iterrows():
        print(f"{i+1}. {row['name']} ({row['calories']} cal)")

    return recomendaciones.reset_index(drop=True)
