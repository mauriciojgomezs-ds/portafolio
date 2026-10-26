import os
from datetime import datetime

def evaluar_viabilidad_modelo_general(
    df_interacciones,
    df_items,
    col_usuario="user_id",
    col_item="item_id",
    col_rating="rating",
    features_relevantes=None,
    min_usuarios=1000,
    min_items=1000,
    min_interacciones=1000,
    max_sparsity=0.8,
    min_features_para_svm=2
):
    reporte = []
    if features_relevantes is None:
        features_relevantes = []

    reporte.append("🔷 Evaluación para NMF")
    n_users = df_interacciones[col_usuario].nunique()
    n_items = df_interacciones[col_item].nunique()
    n_interacciones = len(df_interacciones)

    if n_users >= min_usuarios and n_items >= min_items:
        reporte.append(f"✅ Usuarios: {n_users}, Recetas: {n_items} → OK")
    else:
        reporte.append(f"⚠️ Usuarios: {n_users}, Recetas: {n_items} → Poca diversidad")

    if n_interacciones >= min_interacciones:
        reporte.append(f"✅ Interacciones: {n_interacciones} → OK")
    else:
        reporte.append(f"⚠️ Interacciones: {n_interacciones} → Pocas para NMF")

    rating_dist = df_interacciones[col_rating].value_counts(normalize=True)
    rating_dominante = rating_dist.max()
    if rating_dominante < 0.90:
        reporte.append("✅ Varianza en ratings aceptable")
    else:
        dominante_valor = rating_dist.idxmax()
        reporte.append(f"⚠️ {dominante_valor} representa más del 90% de los ratings")

    sparsity = 1 - (n_interacciones / (n_users * n_items))
    reporte.append(f"📉 Esparsidad: {sparsity:.5f}")
    if sparsity <= max_sparsity:
        reporte.append("✅ Esparsidad dentro de rango aceptable")
    else:
        reporte.append("⚠️ Esparsidad muy alta")

    reporte.append("\n🔶 Evaluación para SVM")
    if col_rating in df_interacciones.columns and df_interacciones[col_rating].nunique() > 2:
        reporte.append("✅ Columna target tiene más de 2 clases")
    else:
        reporte.append("⚠️ Variable objetivo posiblemente no adecuada")

    features_disponibles = [f for f in features_relevantes if f in df_items.columns]
    if len(features_disponibles) >= min_features_para_svm:
        reporte.append(f"✅ Features disponibles: {', '.join(features_disponibles)}")
    else:
        reporte.append("⚠️ Pocos campos útiles disponibles")

    if n_interacciones >= min_interacciones:
        reporte.append("✅ Volumen de datos adecuado para SVM")
    else:
        reporte.append("⚠️ Podría haber overfitting con pocos ejemplos")

    return "\n".join(reporte)
