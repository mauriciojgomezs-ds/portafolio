import pandas as pd
import numpy as np
from tqdm import tqdm
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report
from smartfood.texto import texto_ingredientes


def similitud_recetas_tfidf(df_recipes, top_n=5):
    """
    Calcula recetas similares entre sí usando TF-IDF sobre ingredientes.
    """
    df = df_recipes.dropna(subset=["recipeid", "name", "recipeingredientparts"]).copy()
    df["recipeingredientparts"] = df["recipeingredientparts"].map(texto_ingredientes)
    df = df.dropna(subset=["recipeingredientparts"])
    tfidf = TfidfVectorizer()
    tfidf_matrix = tfidf.fit_transform(df["recipeingredientparts"])

    similitudes = cosine_similarity(tfidf_matrix)

    resultados = {}

    for idx, receta_id in enumerate(df["recipeid"]):
        similares_idx = similitudes[idx].argsort()[::-1][1:top_n+1]
        similares = df.iloc[similares_idx][["recipeid", "name"]].copy()
        similares["score"] = similitudes[idx][similares_idx]
        resultados[receta_id] = similares

    return resultados


def evaluar_threshold(pipeline, X_test, y_test, thresholds=[0, 0.2, 0.4, 0.6, 0.8]):
    """
    Evalúa el desempeño del modelo SVM ajustando el umbral de decisión.
    """
    scores = pipeline.decision_function(X_test)

    for th in thresholds:
        y_pred = (scores > th).astype(int)
        print(f"\n🔎 Threshold: {th}")
        print(classification_report(y_test, y_pred, zero_division=0))


def exportar_recomendaciones_svm_en_lote(pipeline, df_reviews, df_recipes, top_n=5, max_users=1000, output_path="data/output/recomendaciones_svm.csv"):
    """
    Genera recomendaciones para múltiples usuarios usando un modelo SVM entrenado.

    Incluye un resumen con:
    - Número de usuarios con recomendaciones
    - Recetas únicas sugeridas
    - Promedio de recomendaciones por usuario

    Parámetros:
    - pipeline: Pipeline entrenado (con LinearSVC o SVC).
    - df_reviews: DataFrame con columnas ['authorid', 'recipeid'].
    - df_recipes: DataFrame con recetas completas (debe tener ['recipeid', 'calories', 'aggregatedrating', 'recipeingredientparts', 'recipecategory']).
    - top_n: número de recomendaciones por usuario.
    - max_users: máximo de usuarios a procesar.
    - output_path: ruta del archivo .csv exportado.
    """

    resultados = []
    usuarios = df_reviews["authorid"].unique()[:max_users]

    for usuario_id in tqdm(usuarios, desc="🔄 Generando recomendaciones"):

        # Recetas ya evaluadas
        recetas_vistas = df_reviews[df_reviews["authorid"] == usuario_id]["recipeid"].unique()

        # Recetas no vistas
        recetas_disponibles = df_recipes[~df_recipes["recipeid"].isin(recetas_vistas)].copy()
        recetas_disponibles = recetas_disponibles.dropna(subset=["calories", "aggregatedrating", "recipeingredientparts", "recipecategory"])

        if recetas_disponibles.empty:
            continue

        # Crear DataFrame con columnas esperadas por el pipeline
        X = pd.concat([
            recetas_disponibles["recipeingredientparts"].reset_index(drop=True).to_frame(),
            recetas_disponibles[["calories", "aggregatedrating"]].reset_index(drop=True),
            recetas_disponibles["recipecategory"].reset_index(drop=True).to_frame()
        ], axis=1)

        try:
            scores = pipeline.decision_function(X)
        except:
            continue

        # Normalizar los scores
        scores = (scores - scores.min()) / (scores.max() - scores.min())
        recetas_disponibles["score"] = scores

        recomendaciones = recetas_disponibles.sort_values(by="score", ascending=False).head(top_n)

        for _, row in recomendaciones.iterrows():
            resultados.append({
                "usuario": usuario_id,
                "receta_id": row["recipeid"],
                "receta_nombre": row["name"],
                "score": round(row["score"], 3)
            })

    df_resultados = pd.DataFrame(resultados)
    df_resultados.to_csv(output_path, index=False)

    # 🎯 Resumen
    usuarios_totales = df_resultados["usuario"].nunique()
    recetas_unicas = df_resultados["receta_id"].nunique()
    promedio = df_resultados.groupby("usuario").size().mean()

    print(f"\n✅ Recomendaciones exportadas a {output_path} ({len(df_resultados):,} filas)")
    print(f"👤 Usuarios con recomendaciones: {usuarios_totales}")
    print(f"🍽️ Recetas recomendadas únicas: {recetas_unicas}")
    print(f"📊 Promedio de recetas por usuario: {promedio:.2f}")



def recomendar_similares_por_receta(recipe_id, df_recipes, pipeline, top_n=5):
    receta_base = df_recipes[df_recipes["recipeid"] == recipe_id]

    if receta_base.empty:
        print(f"⚠️ Receta con ID {recipe_id} no encontrada.")
        return pd.DataFrame()

    # Eliminar la receta base del conjunto de comparación
    df_comparables = df_recipes[df_recipes["recipeid"] != recipe_id].copy()

    # Filtrar necesarias
    df_comparables = df_comparables.dropna(subset=["calories", "aggregatedrating", "recipeingredientparts", "recipecategory"])

    # Crear X con mismas columnas que el modelo
    X_comparables = pd.concat([
        df_comparables["recipeingredientparts"].reset_index(drop=True).to_frame("recipeingredientparts"),
        df_comparables[["calories", "aggregatedrating"]].reset_index(drop=True),
        df_comparables["recipecategory"].reset_index(drop=True).to_frame("recipecategory")
    ], axis=1)

    # scores = pipeline.predict_proba(X_comparables)[:, 1]
    scores = pipeline.decision_function(X_comparables)
    scores = (scores - scores.min()) / (scores.max() - scores.min())  # opcional para que esté entre 0 y 1

    df_comparables["score"] = scores

    recomendaciones = df_comparables.sort_values(by="score", ascending=False).head(top_n)

    print(f"\n📌 Recetas similares a '{receta_base['name'].values[0]}':")
    for idx, row in recomendaciones.iterrows():
        print(f"{idx + 1}. {row['name']} (Score: {row['score']:.2f})")

    return recomendaciones


def recomendar_por_keywords(texto, pipeline, df_recipes, top_n=5):
    """
    Recomienda recetas similares a una entrada textual (ingredientes, descriptores, etc.).

    Parámetros:
    - texto: texto base, puede incluir ingredientes o descripciones.
    - pipeline: modelo SVM entrenado con TF-IDF + features numéricos.
    - df_recipes: dataset completo de recetas.
    - top_n: cuántas recomendaciones retornar.

    Retorna:
    - DataFrame con top N recetas recomendadas.
    """
    df_comparables = df_recipes.dropna(subset=["calories", "aggregatedrating", "recipeingredientparts", "recipecategory"]).copy()

    texto_replicado = pd.Series([texto] * len(df_comparables), name="recipeingredientparts")

    X = pd.concat([
        texto_replicado.reset_index(drop=True).to_frame(),
        df_comparables[["calories", "aggregatedrating"]].reset_index(drop=True),
        df_comparables["recipecategory"].reset_index(drop=True).to_frame("recipecategory")
    ], axis=1)

    scores = pipeline.decision_function(X)
    scores = (scores - scores.min()) / (scores.max() - scores.min())

    df_comparables["score"] = scores
    recomendaciones = df_comparables.sort_values(by="score", ascending=False).head(top_n)

    print(f"\n📌 Recomendaciones basadas en texto: '{texto}'")
    for i, row in recomendaciones.iterrows():
        print(f"{i + 1}. {row['name']} (Score: {row['score']:.2f})")

    return recomendaciones


def recomendar_por_calorias(calorias_objetivo, df_recipes, top_n=5):
    """
    Retorna recetas cuya cantidad de calorías esté más cerca de un valor dado.

    Parámetros:
    - calorias_objetivo: valor (float o int) al cual comparar.
    - df_recipes: DataFrame con la columna 'calories'.
    - top_n: cantidad de recetas a retornar.

    Retorna:
    - DataFrame con las recetas más cercanas en calorías.
    """
    df_validas = df_recipes.dropna(subset=["calories", "name"]).copy()
    df_validas["diferencia"] = np.abs(df_validas["calories"] - calorias_objetivo)

    recomendadas = df_validas.sort_values("diferencia").head(top_n)

    print(f"\n📌 Recetas más cercanas a {calorias_objetivo} calorías:")
    for i, row in recomendadas.iterrows():
        print(f"{i+1}. {row['name']} ({row['calories']} cal)")

    return recomendadas.reset_index(drop=True)


def ranking_recetas_nuevas(pipeline, df_recipes, top_n=10):
    """
    Retorna un ranking de recetas que el modelo predice como altamente recomendables (sin usuario específico).

    Parámetros:
    - pipeline: modelo SVM entrenado.
    - df_recipes: DataFrame con todas las recetas (completo).
    - top_n: número de recetas a recomendar.

    Retorna:
    - DataFrame con las mejores recetas según el modelo.
    """
    df_validas = df_recipes.dropna(subset=["calories", "aggregatedrating", "recipeingredientparts", "recipecategory"]).copy()

    X = pd.concat([
        df_validas["recipeingredientparts"].reset_index(drop=True).to_frame("recipeingredientparts"),
        df_validas[["calories", "aggregatedrating"]].reset_index(drop=True),
        df_validas["recipecategory"].reset_index(drop=True).to_frame("recipecategory")
    ], axis=1)

    # Puntajes del modelo
    try:
        scores = pipeline.decision_function(X)
    except AttributeError:
        print("⚠️ Este modelo no soporta decision_function. Usa predict_proba si estás usando SVC con probability=True.")
        return pd.DataFrame()

    scores = (scores - scores.min()) / (scores.max() - scores.min())
    df_validas["score"] = scores

    recomendaciones = df_validas.sort_values(by="score", ascending=False).head(top_n)

    print(f"\n📌 Ranking de {top_n} recetas nuevas recomendadas por el modelo:")
    for i, row in recomendaciones.iterrows():
        print(f"{i+1}. {row['name']} (Score: {row['score']:.2f})")

    return recomendaciones.reset_index(drop=True)


def ranking_por_categoria(categoria, pipeline, df_recipes, top_n=10):
    """
    Genera un ranking de recetas dentro de una categoría específica según el modelo SVM.

    Parámetros:
    - categoria: categoría de receta a filtrar (debe estar en la columna recipecategory).
    - pipeline: modelo SVM entrenado.
    - df_recipes: DataFrame completo de recetas.
    - top_n: cuántas recetas retornar.

    Retorna:
    - DataFrame con las recetas mejor puntuadas dentro de esa categoría.
    """
    df_filtrado = df_recipes[
        (df_recipes["recipecategory"] == categoria) &
        (df_recipes[["calories", "aggregatedrating", "recipeingredientparts"]].notna().all(axis=1))
    ].copy()

    if df_filtrado.empty:
        print(f"⚠️ No hay recetas con datos completos en la categoría '{categoria}'.")
        return pd.DataFrame()

    X = pd.concat([
        df_filtrado["recipeingredientparts"].reset_index(drop=True).to_frame("recipeingredientparts"),
        df_filtrado[["calories", "aggregatedrating"]].reset_index(drop=True),
        df_filtrado["recipecategory"].reset_index(drop=True).to_frame("recipecategory")
    ], axis=1)

    try:
        scores = pipeline.decision_function(X)
    except AttributeError:
        print("⚠️ Este modelo no soporta decision_function. Usa predict_proba si estás usando SVC con probability=True.")
        return pd.DataFrame()

    scores = (scores - scores.min()) / (scores.max() - scores.min())
    df_filtrado["score"] = scores

    recomendaciones = df_filtrado.sort_values(by="score", ascending=False).head(top_n)

    print(f"\n📌 Ranking de recetas en la categoría '{categoria}':")
    for i, row in recomendaciones.iterrows():
        print(f"{i+1}. {row['name']} (Score: {row['score']:.2f})")

    return recomendaciones.reset_index(drop=True)


def exportar_recomendaciones_svm_por_usuario(pipeline, df_reviews, df_recipes, path="data/output/recomendaciones_svm.csv", top_n=5, max_users = 100):
    """
    Genera recomendaciones personalizadas para cada usuario y las exporta a un CSV.

    Parámetros:
    - pipeline: modelo entrenado con SVM.
    - df_reviews: DataFrame con columnas ['authorid', 'recipeid'].
    - df_recipes: DataFrame completo de recetas.
    - path: ruta donde guardar el archivo CSV.
    - top_n: número de recetas recomendadas por usuario.

    Retorna:
    - DataFrame con las recomendaciones.
    """
    resultados = []
    usuarios = df_reviews["authorid"].unique()[:max_users]

    for usuario_id in usuarios:
        recetas_evaluadas = df_reviews[df_reviews['authorid'] == usuario_id]['recipeid'].unique()
        disponibles = df_recipes[~df_recipes["recipeid"].isin(recetas_evaluadas)].copy()
        disponibles = disponibles.dropna(subset=["calories", "aggregatedrating", "recipeingredientparts", "recipecategory"])

        if disponibles.empty:
            continue

        X = pd.concat([
            disponibles["recipeingredientparts"].reset_index(drop=True).to_frame(),
            disponibles[["calories", "aggregatedrating"]].reset_index(drop=True),
            disponibles["recipecategory"].reset_index(drop=True).to_frame()
        ], axis=1)

        try:
            scores = pipeline.decision_function(X)
        except Exception as e:
            print(f"⚠️ Error para usuario {usuario_id}: {e}")
            continue

        scores = (scores - scores.min()) / (scores.max() - scores.min())
        disponibles["score"] = scores
        top_recs = disponibles.sort_values("score", ascending=False).head(top_n)

        for _, row in top_recs.iterrows():
            resultados.append({
                "usuario": usuario_id,
                "receta_id": row["recipeid"],
                "receta_nombre": row["name"],
                "score": round(row["score"], 2)
            })

    df_resultado = pd.DataFrame(resultados)
    df_resultado.to_csv(path, index=False)
    print(f"✅ Recomendaciones exportadas a {path}")
    return df_resultado


