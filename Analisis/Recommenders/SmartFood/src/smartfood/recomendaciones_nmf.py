from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import numpy as np
from sklearn.decomposition import NMF
from sklearn.metrics import mean_squared_error
import numpy as np
import time
import matplotlib.pyplot as plt


def entrenar_y_exportar_nmf_desde_grid(
    matriz_ratings_filled,
    df_resultados_grid,
    guardar=False,
    path_prefix="models/nmf"
):
    # Fila con menor RMSE
    mejor_fila = df_resultados_grid.sort_values("rmse").iloc[0]

    print(f"📌 Usando configuración óptima:")
    print(mejor_fila[["rmse", "init", "solver", "max_iter", "alpha_W", "alpha_H", "l1_ratio"]])

    return entrenar_y_exportar_nmf(
        matriz_ratings_filled=matriz_ratings_filled,
        n_componentes=int(mejor_fila.name),  # si está como índice
        init=mejor_fila["init"],
        solver=mejor_fila["solver"],
        max_iter=int(mejor_fila["max_iter"]),
        alpha_W=mejor_fila["alpha_W"],
        alpha_H=mejor_fila["alpha_H"],
        l1_ratio=mejor_fila["l1_ratio"],
        guardar=guardar,
        path_prefix=path_prefix
    )


def entrenar_y_exportar_nmf(
    matriz_ratings_filled, 
    n_componentes=10, 
    init='nndsvda', 
    solver='mu',
    max_iter=1000, 
    random_state=42, 
    alpha_W=0.01, 
    alpha_H=0.01, 
    l1_ratio=0.5,
    guardar=False,
    path_prefix="models/nmf"
):
    print(f"🚀 Entrenando NMF con {n_componentes} componentes...")
    
    modelo_nmf = NMF(
        n_components=n_componentes,
        init=init,
        solver=solver,
        max_iter=max_iter,
        random_state=random_state,
        alpha_W=alpha_W,
        alpha_H=alpha_H,
        l1_ratio=l1_ratio
    )

    # Entrenar
    U = modelo_nmf.fit_transform(matriz_ratings_filled.values)
    I = modelo_nmf.components_.T
    predicciones = U @ I.T

    # Convertir a DataFrames con índices originales
    embeddings_usuarios = pd.DataFrame(U, index=matriz_ratings_filled.index)
    embeddings_recetas = pd.DataFrame(I, index=matriz_ratings_filled.columns)
    pred_df = pd.DataFrame(predicciones, index=matriz_ratings_filled.index, columns=matriz_ratings_filled.columns)

    # Guardar si se solicita
    if guardar:
        embeddings_usuarios.to_parquet(f"{path_prefix}_usuarios.parquet")
        embeddings_recetas.to_parquet(f"{path_prefix}_recetas.parquet")
        pred_df.to_parquet(f"{path_prefix}_predicciones.parquet")
        print("💾 Embeddings y predicciones guardadas en disco.")

    return embeddings_usuarios, embeddings_recetas, pred_df


def graficar_resultados_grid(df_resultados):
    plt.figure(figsize=(10, 5))
    plt.plot(df_resultados.index, df_resultados["rmse"], marker='o', label="RMSE")
    plt.plot(df_resultados.index, df_resultados["mse"], marker='s', linestyle='--', label="MSE")
    plt.xlabel("n_components")
    plt.ylabel("Error")
    plt.title("Evaluación de NMF por número de componentes")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()


def grid_nmf(
    matriz_ratings,
    componentes=[10, 20, 30, 40, 50],
    porcentaje_test=0.2,
    random_state=42,
    init='nndsvda',
    solver='mu',
    max_iter=1000,
    alpha_W=0.01,
    alpha_H=0.01,
    l1_ratio=0.5
):
    resultados = []

    for n in componentes:
        print(f"🔧 Evaluando NMF con {n} componentes...")
        t0 = time.time()

        resultado = evaluar_nmf_con_mascara(
            matriz_original=matriz_ratings,
            porcentaje_test=porcentaje_test,
            n_componentes=n,
            random_state=random_state,
            init=init,
            solver=solver,
            max_iter=max_iter,
            alpha_W=alpha_W,
            alpha_H=alpha_H,
            l1_ratio=l1_ratio
        )

        resultado.update({
            "tiempo": round(time.time() - t0, 2),
            "init": init,
            "solver": solver,
            "max_iter": max_iter,
            "alpha_W": alpha_W,
            "alpha_H": alpha_H,
            "l1_ratio": l1_ratio
        })

        resultados.append(resultado)

    df_resultados = pd.DataFrame(resultados)
    df_resultados["componentes"] = componentes
    return df_resultados.set_index("componentes")


def evaluar_nmf_con_mascara(
    matriz_original,
    porcentaje_test=0.2,
    n_componentes=20,
    random_state=42,
    init='nndsvda',
    solver='mu',
    max_iter=1000,
    alpha_W=0.01,
    alpha_H=0.01,
    l1_ratio=0.5
):
    np.random.seed(random_state)

    matriz = matriz_original.copy()
    mask_observados = matriz > 0

    observados = np.argwhere(mask_observados.values)
    n_test = int(len(observados) * porcentaje_test)

    idx_test = np.random.choice(len(observados), size=n_test, replace=False)
    test_indices = observados[idx_test]

    matriz_entrenamiento = matriz.copy()
    for u, i in test_indices:
        matriz_entrenamiento.iat[u, i] = 0  # ocultar

    modelo_nmf = NMF(
        n_components=n_componentes,
        init=init,
        solver=solver,
        max_iter=max_iter,
        random_state=random_state,
        alpha_W=alpha_W,
        alpha_H=alpha_H,
        l1_ratio=l1_ratio
    )

    U = modelo_nmf.fit_transform(matriz_entrenamiento.values)
    I = modelo_nmf.components_.T
    reconstruida = U @ I.T

    y_true, y_pred = [], []
    for u, i in test_indices:
        real = matriz.values[u, i]
        pred = reconstruida[u, i]
        y_true.append(real)
        y_pred.append(pred)

    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)

    return {
        "mse": mse,
        "rmse": rmse,
        "interacciones_test": len(y_true),
        "componentes": n_componentes
    }


def calcular_similitud_coseno(matriz, index=None):
    similitud = cosine_similarity(matriz)
    if isinstance(matriz, pd.DataFrame):
        index = matriz.index if index is None else index
    elif index is None:
        raise ValueError("Debes proporcionar un índice si la matriz no es un DataFrame")
    return pd.DataFrame(similitud, index=index, columns=index)


def obtener_mas_similares(entidad_id, matriz_similitud, df_nombres=None, col_id=None, col_nombre=None, top_n=5):
    similares = matriz_similitud[entidad_id].drop(entidad_id).sort_values(ascending=False).head(top_n)
    resultado = []
    for entidad, score in similares.items():
        nombre = str(entidad)
        if df_nombres is not None and col_id is not None and col_nombre is not None:
            match = df_nombres.loc[df_nombres[col_id] == entidad, col_nombre].values
            if len(match) > 0:
                nombre = match[0]
        resultado.append((entidad, nombre, round(score, 2)))
    return resultado


def generar_recomendaciones(usuario_id, matriz_ratings, matriz_similitud, top_n=5):
    if usuario_id not in matriz_similitud.columns:
        return []
    similares = matriz_similitud[usuario_id].drop(usuario_id).sort_values(ascending=False).head(10)
    pesos = similares.values
    vecinos = similares.index
    ratings_vecinos = matriz_ratings.loc[vecinos]
    weighted_scores = ratings_vecinos.T.dot(pesos)
    recomendacion_scores = weighted_scores / pesos.sum()
    items_vistos = matriz_ratings.loc[usuario_id][matriz_ratings.loc[usuario_id] > 0].index
    recomendaciones = recomendacion_scores.drop(index=items_vistos, errors='ignore')
    return recomendaciones.sort_values(ascending=False).head(top_n)


def visualizar_recomendaciones(entidad_id, recomendaciones, df_items, col_id="recipeid", col_nombre="name", tipo="usuario"):
    print(f"\n📌 Recomendaciones para el {tipo} {entidad_id}:")
    for idx, item_id in enumerate(recomendaciones.index, 1):
        nombre = df_items.loc[df_items[col_id] == item_id, col_nombre].values
        nombre = nombre[0] if len(nombre) > 0 else "Nombre no disponible"
        print(f"{idx}. {nombre} (Score: {recomendaciones[item_id]:.2f})")


def predecir_rating(user, item, matriz, similitud, k=5):
    if user not in similitud.index or item not in matriz.columns:
        return np.nan

    vecinos = similitud[user].drop(user).sort_values(ascending=False).head(k)
    vecinos_ids = vecinos.index
    pesos = vecinos.values

    ratings = matriz.loc[vecinos_ids, item].fillna(0)

    # Filtrar solo vecinos con rating no nulo
    mask = ratings != 0
    ratings_filtrados = ratings[mask]
    pesos_filtrados = pesos[mask]

    if len(ratings_filtrados) == 0 or pesos_filtrados.sum() == 0:
        return np.nan

    return np.dot(ratings_filtrados, pesos_filtrados) / pesos_filtrados.sum()


def evaluar_modelo(test_df, matriz_train, similitud, k=10):
    from sklearn.metrics import mean_squared_error
    reales = []
    predichos = []
    for _, row in test_df.iterrows():
        u, i, r = row["authorid"], row["recipeid"], row["rating"]
        pred = predecir_rating(u, i, matriz_train, similitud, k=k)
        if not np.isnan(pred):
            reales.append(r)
            predichos.append(pred)
    mse = mean_squared_error(reales, predichos)
    rmse = np.sqrt(mse)
    return mse, rmse


# from sklearn.metrics.pairwise import cosine_similarity
# import pandas as pd
# import numpy as np

# def calcular_similitud_coseno(matriz, index=None):
#     """
#     Calcula la matriz de similitud de coseno entre filas de una matriz (por ejemplo, usuarios o ítems).

#     Parámetros:
#         - matriz: array o DataFrame con los datos.
#         - index: índice a usar si la matriz es un array (opcional).
#     """
#     similitud = cosine_similarity(matriz)

#     if isinstance(matriz, pd.DataFrame):
#         index = matriz.index if index is None else index
#     elif index is None:
#         raise ValueError("Debes proporcionar un índice si la matriz no es un DataFrame")

#     return pd.DataFrame(similitud, index=index, columns=index)


# def obtener_mas_similares(entidad_id, matriz_similitud, df_nombres=None, col_id=None, col_nombre=None, top_n=5):
#     """
#     Devuelve las entidades más similares a una entidad dada.

#     Parámetros:
#         - entidad_id: ID del usuario o ítem de referencia.
#         - matriz_similitud: DataFrame de similitud coseno.
#         - df_nombres: DataFrame con nombres legibles de entidades (opcional).
#         - col_id: nombre de columna ID en df_nombres.
#         - col_nombre: nombre de columna legible en df_nombres.
#         - top_n: número de entidades similares a retornar.
#     """
#     similares = matriz_similitud[entidad_id].drop(entidad_id).sort_values(ascending=False).head(top_n)

#     resultado = []
#     for entidad, score in similares.items():
#         nombre = str(entidad)
#         if df_nombres is not None and col_id is not None and col_nombre is not None:
#             match = df_nombres.loc[df_nombres[col_id] == entidad, col_nombre].values
#             if len(match) > 0:
#                 nombre = match[0]
#         resultado.append((entidad, nombre, round(score, 2)))

#     return resultado


# def generar_recomendaciones(usuario_id, matriz_ratings, matriz_similitud, top_n=5):
#     """
#     Genera recomendaciones de ítems no vistos por el usuario, basadas en usuarios similares.

#     Parámetros:
#         - usuario_id: ID del usuario para quien generar recomendaciones.
#         - matriz_ratings: DataFrame con ratings (usuarios como filas, ítems como columnas).
#         - matriz_similitud: matriz de similitud entre usuarios.
#         - top_n: número de recomendaciones a retornar.
#     """
#     if usuario_id not in matriz_similitud.columns:
#         return []

#     similares = matriz_similitud[usuario_id].drop(usuario_id).sort_values(ascending=False).head(10)
#     pesos = similares.values
#     vecinos = similares.index

#     ratings_vecinos = matriz_ratings.loc[vecinos]
#     weighted_scores = ratings_vecinos.T.dot(pesos)
#     recomendacion_scores = weighted_scores / pesos.sum()

#     items_vistos = matriz_ratings.loc[usuario_id][matriz_ratings.loc[usuario_id] > 0].index
#     recomendaciones = recomendacion_scores.drop(index=items_vistos, errors='ignore')

#     return recomendaciones.sort_values(ascending=False).head(top_n)


# def visualizar_recomendaciones(entidad_id, recomendaciones, df_items, col_id="recipeid", col_nombre="name", tipo="usuario"):
#     """
#     Imprime recomendaciones con nombres legibles a partir de IDs.
#     """
#     print(f"\n📌 Recomendaciones para el {tipo} {entidad_id}:")
#     for idx, item_id in enumerate(recomendaciones.index, 1):
#         nombre = df_items.loc[df_items[col_id] == item_id, col_nombre].values
#         nombre = nombre[0] if len(nombre) > 0 else "Nombre no disponible"
#         print(f"{idx}. {nombre} (Score: {recomendaciones[item_id]:.2f})")


# def exportar_recomendaciones_en_lote(df_ratings, matriz_similitud, df_items, top_n=5, path="data/output/recomendaciones.csv"):
#     resultados = []
#     for usuario in df_ratings.index:
#         recs = generar_recomendaciones(usuario, df_ratings, matriz_similitud, top_n)
#         for item, score in recs.items():
#             nombre = df_items.loc[df_items['recipeid'] == item, 'name'].values
#             resultados.append({
#                 "usuario": usuario,
#                 "receta_id": item,
#                 "receta_nombre": nombre[0] if len(nombre) > 0 else "Desconocido",
#                 "score": round(score, 2)
#             })
#     pd.DataFrame(resultados).to_csv(path, index=False)
#     print(f"✅ Recomendaciones exportadas a {path}")


# def predecir_rating(user, item, matriz, similitud, k=5):
#     if user not in similitud.index or item not in matriz.columns:
#         return np.nan

#     vecinos = similitud[user].drop(user).sort_values(ascending=False).head(k)
#     vecinos_ids = vecinos.index
#     pesos = vecinos.values

#     ratings = matriz.loc[vecinos_ids, item].fillna(0)
#     if ratings.sum() == 0:
#         return np.nan

#     return np.dot(ratings, pesos) / pesos.sum()


def evaluar_recomendador_colaborativo(test_df, matriz_train, similitud_usuarios, top_n=5):
    """
    Evalúa el sistema de recomendación basado en usuarios comparando contra un set de test.

    Retorna:
    - precisión promedio en la muestra
    """
    usuarios_test = test_df["authorid"].unique()
    aciertos = 0
    total = 0

    for usuario in usuarios_test:
        if usuario not in matriz_train.index or usuario not in similitud_usuarios.index:
            continue

        recomendaciones = generar_recomendaciones(usuario, matriz_train, similitud_usuarios, top_n=top_n)
        if len(recomendaciones) == 0:
            continue

        recetas_test = test_df[test_df["authorid"] == usuario]["recipeid"].values
        aciertos += sum([1 for receta in recomendaciones.index if receta in recetas_test])
        total += len(recomendaciones)

    precision = aciertos / total if total > 0 else 0
    print(f"🎯 Precisión promedio en top-{top_n}: {precision:.2%}")
    return precision
