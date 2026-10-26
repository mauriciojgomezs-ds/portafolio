"""Cifras reproducibles y textos Markdown para el análisis exploratorio."""

import math


def numero(valor, decimales=0):
    """Formato español; las estadísticas no definidas se muestran explícitamente."""
    if valor is None or not math.isfinite(float(valor)):
        return "no disponible"
    return f"{valor:,.{decimales}f}".translate(str.maketrans({",": ".", ".": ","}))


def _division(numerador, denominador):
    return numerador / denominador if denominador else None


def _estadisticas(serie):
    return {
        clave: float(valor) if math.isfinite(float(valor)) else None
        for clave, valor in serie.describe().items()
    }


def calcular_metricas_eda(recipes, reviews):
    """Resume cada dataset sin materializar la matriz usuario–receta.

    La esparsidad cuenta pares registrados distintos, incluidos ratings cero.
    Los porcentajes de rating usan todas las reseñas como denominador.
    """
    pares = reviews[["authorid", "recipeid"]].dropna().drop_duplicates()
    usuarios = pares.authorid.nunique()
    items = pares.recipeid.nunique()
    densidad = _division(len(pares), usuarios * items)
    return {
        "recetas": int(recipes.recipeid.nunique()),
        "filas_catalogo": len(recipes),
        "reviews": len(reviews),
        "usuarios": int(usuarios),
        "items": int(items),
        "pares": len(pares),
        "pares_repetidos": int(reviews.duplicated(["authorid", "recipeid"]).sum()),
        "esparsidad": 100 * (1 - densidad) if densidad is not None else None,
        "rating_5": _division(100 * int(reviews.rating.eq(5).sum()), len(reviews)),
        "rating_0": _division(100 * int(reviews.rating.eq(0).sum()), len(reviews)),
        "rating_positivo": _division(100 * int(reviews.rating.ge(4).sum()), len(reviews)),
        "nulos_reviews_claves": int(reviews[["authorid", "recipeid", "rating"]].isna().sum().sum()),
        "items_fuera_catalogo": int((~pares.recipeid.isin(recipes.recipeid)).sum()),
        "calorias": _estadisticas(recipes.calories),
        "rating_agregado": _estadisticas(recipes.aggregatedrating),
        "rating_agregado_5": _division(100 * int(recipes.aggregatedrating.eq(5).sum()), len(recipes)),
        "nulos_recetas": {
            col: _division(100 * int(recipes[col].isna().sum()), len(recipes))
            for col in ["aggregatedrating", "reviewcount", "recipeyield", "recipeservings"]
        },
        "historial_usuarios": _estadisticas(pares.groupby("authorid").size()),
        "historial_recetas": _estadisticas(pares.groupby("recipeid").size()),
        "matriz_gb": usuarios * items * 8 / 1e9,
    }


def comentario_eda(seccion, metricas, originales=None, umbral=None):
    """Genera texto descriptivo; no infiere calidad predictiva de estas cifras."""
    m = metricas
    n = numero
    c, a = m["calorias"], m["rating_agregado"]
    if seccion in {"recetas", "recetas_filtradas"}:
        titulo = "Interpretación de las recetas filtradas" if originales else "Interpretación del catálogo de recetas"
        nulos = "; ".join(f"`{col}`: **{n(pct, 2)} %**" for col, pct in m["nulos_recetas"].items())
        comparacion = ""
        if originales:
            comparacion = (
                f"\n\nLa desviación estándar de `aggregatedrating` pasa de **{n(originales['rating_agregado']['std'], 3)} "
                f"a {n(a['std'], 3)}**. El **{n(m['rating_agregado_5'], 2)} %** del catálogo filtrado tiene rating agregado 5. "
                "Estos cambios describen la selección; no demuestran mejora predictiva ni corrección de errores."
            )
        return (
            f"### {titulo}\n\n"
            f"Hay **{n(m['recetas'])} recetas distintas** en **{n(m['filas_catalogo'])} filas**. "
            f"Entre los **{n(a['count'])} ratings agregados disponibles**, la mediana es **{n(a['50%'], 2)}**, "
            f"la media **{n(a['mean'], 3)}** y la desviación estándar **{n(a['std'], 3)}**.\n\n"
            f"Porcentaje de nulos: {nulos}.\n\n"
            f"Las calorías tienen mediana **{n(c['50%'], 2)}**, media **{n(c['mean'], 2)}** "
            f"y máximo **{n(c['max'], 1)}**. Los extremos requieren revisar unidades y procedencia."
            f"{comparacion}\n\n"
            "Las cifras anteriores no validan cardinalidad ni redundancia de columnas con listas; revisa los errores "
            "del diagnóstico precedente. Seleccionar solo `int64/float64` tampoco incluye todos los tipos numéricos. "
            "El rating agregado difiere de una valoración individual y su uso requiere revisar la disponibilidad temporal."
        )
    if seccion in {"reviews", "reviews_filtradas"}:
        titulo = "Interpretación de las reseñas filtradas" if originales else "Interpretación de las reseñas"
        comparacion = ""
        if originales:
            comparacion = (
                f"\n\nAntes del filtro, los ratings 5 representaban **{n(originales['rating_5'], 2)} %** "
                f"y los ceros **{n(originales['rating_0'], 2)} %**. El target `rating >= 4` "
                f"sería positivo en el **{n(m['rating_positivo'], 2)} %** del subconjunto. "
                "Ese porcentaje sería la accuracy de predecir siempre positivo sobre este conjunto, no una evaluación del SVM."
            )
        return (
            f"### {titulo}\n\n"
            f"Hay **{n(m['reviews'])} reseñas**, **{n(m['usuarios'])} usuarios** y **{n(m['items'])} recetas evaluadas**. "
            f"El **{n(m['rating_5'], 2)} %** de los ratings es 5 y el **{n(m['rating_0'], 2)} %** es 0.\n\n"
            f"La esparsidad es **{n(m['esparsidad'], 4)} %**, calculada con **{n(m['pares'])} pares únicos**. "
            "Los ceros cuentan como interacciones registradas; excluirlos cambia la definición de observación.\n\n"
            f"Se detectan **{n(m['pares_repetidos'])} filas adicionales con pares usuario–receta repetidos**, "
            f"**{n(m['nulos_reviews_claves'])} valores nulos** en usuario, receta o rating y "
            f"**{n(m['items_fuera_catalogo'])} pares** cuya receta no aparece en el catálogo. "
            "Estos controles no validan semánticamente todos los campos."
            f"{comparacion}\n\n"
            "Debe definirse el significado de rating cero y comparar modelos con baselines. "
            "La esparsidad no demuestra que NMF sea adecuado; centrar ratings puede generar negativos incompatibles con NMF. "
            "Los ingredientes necesitan preparación para TF-IDF y los IDs recodificados requieren mapeos persistidos."
        )
    if seccion == "viabilidad":
        return (
            "### Alcance del diagnóstico de viabilidad\n\n"
            "`evaluar_viabilidad_modelo_general` aplica umbrales heurísticos, no valida desempeño. "
            "«Varianza aceptable» solo comprueba si la clase dominante está por debajo del 90 %; "
            "«Target con más de dos clases» describe el rating original, aunque el SVM usa `rating >= 4`.\n\n"
            f"Una matriz densa float64 de los usuarios y recetas observados ocuparía **{n(m['matriz_gb'], 2)} GB** "
            "(unidades decimales), sin copias ni objetos adicionales. Conviene evaluar estructuras dispersas y documentar el muestreo."
        )
    if seccion in {"historial_usuarios", "historial_recetas"}:
        h = m[seccion]
        entidad = "usuarios" if seccion == "historial_usuarios" else "recetas"
        return (
            f"### Historial de {entidad}\n\n"
            f"Para **{n(h['count'])} {entidad} con pares registrados**, la mediana es **{n(h['50%'], 2)}**, "
            f"el tercer cuartil **{n(h['75%'], 2)}**, la media **{n(h['mean'], 2)}**, "
            f"la desviación estándar **{n(h['std'], 2)}** y el máximo **{n(h['max'])}**. "
            "Se cuentan recetas distintas por usuario y usuarios distintos por receta.\n\n"
            f"El catálogo contiene **{n(m['recetas'])} recetas distintas**; las recetas sin reseñas no participan "
            "en la distribución de historiales. Un historial escaso limita la personalización; no demuestra ruido "
            "ni justifica excluir entidades sin evaluar cobertura y cold start."
        )
    if seccion == "filtro":
        if originales is None or umbral is None:
            raise ValueError("El resumen del filtro requiere métricas originales y umbral.")
        cobertura = {k: _division(100 * m[k], originales[k]) for k in ["usuarios", "recetas", "reviews"]}
        return (
            "### Elección exploratoria del umbral\n\n"
            f"Se aplica el umbral **{n(umbral)}** a los conteos originales antes de intersectar usuarios y recetas. "
            "No se ha demostrado que optimice error o ranking.\n\n"
            f"El resultado contiene **{n(m['usuarios'])} usuarios**, **{n(m['recetas'])} recetas del catálogo** "
            f"(**{n(m['items'])} con reseñas**) y **{n(m['reviews'])} reseñas**. "
            f"Conserva el **{n(cobertura['usuarios'], 3)} %** de los usuarios observados, "
            f"el **{n(cobertura['recetas'], 4)} %** del catálogo y el **{n(cobertura['reviews'], 3)} %** de las reseñas.\n\n"
            f"Los mínimos finales de interacciones distintas son **{n(m['historial_usuarios']['min'])} por usuario** "
            f"y **{n(m['historial_recetas']['min'])} por receta observada**. "
            "El umbral previo no garantiza ese mínimo en el resultado. Las recetas del catálogo sin interacciones "
            "quedan fuera de estos mínimos. La cobertura no acredita representatividad."
        )
    raise ValueError(f"Sección desconocida: {seccion}")


def comentario_correlacion(df, x, y, metodo="pearson", cortes=(0.1, 0.3, 0.5, 0.7)):
    """Interpretación descriptiva con cortes del proyecto, sin inferir causalidad.

    Los pares incompletos o no finitos se excluyen. Los cortes se aplican a |r|.
    No se calcula significancia ni se ajustan comparaciones múltiples.
    """
    import pandas as pd

    if metodo not in {"pearson", "spearman"}:
        raise ValueError("Usa pearson o spearman.")
    if len(cortes) != 4 or not (0 < cortes[0] < cortes[1] < cortes[2] < cortes[3] < 1):
        raise ValueError("Se requieren cuatro cortes crecientes entre cero y uno.")
    pares = df[[x, y]].apply(pd.to_numeric, errors="coerce").replace([float("inf"), -float("inf")], float("nan")).dropna()
    encabezado = f"### Correlación: `{x}` y `{y}`\n\nMétodo: **{metodo}**; **{numero(len(pares))} pares válidos**; **{numero(len(df)-len(pares))} filas excluidas**.\n\n"
    if len(pares) < 3:
        return encabezado + "Hay menos de tres pares válidos: no se interpreta la correlación."
    if pares[x].nunique() < 2 or pares[y].nunique() < 2:
        return encabezado + "Una variable es constante: el coeficiente de correlación no está definido."
    r = pares[x].corr(pares[y], method=metodo)
    if not math.isfinite(float(r)):
        return encabezado + "El coeficiente no está definido; revisa los datos."
    etiquetas = ["muy débil", "débil", "moderada", "fuerte", "muy fuerte"]
    nivel = sum(abs(r) >= c for c in cortes)
    direccion = "positiva" if r > 0 else "negativa" if r < 0 else "sin dirección"
    rangos = ", ".join(numero(c, 2) for c in cortes)
    return (
        encabezado + f"El coeficiente es **{numero(r, 3)}**: asociación **{direccion}, {etiquetas[nivel]}**, "
        f"según los cortes descriptivos del proyecto para |r|: **{rangos}**. "
        "Se clasifica con el coeficiente sin redondear; estos cortes son configurables, no universales. "
        "La magnitud no prueba significancia estadística, causalidad ni capacidad predictiva. "
        "Pearson describe asociación lineal y puede ser sensible a extremos; Spearman describe asociación monótona. "
        "Revisa también el gráfico, las unidades y la selección de datos."
    )


def comentario_recomendaciones(recomendaciones, top_n):
    if not isinstance(top_n, int) or top_n <= 0:
        raise ValueError("top_n debe ser un entero positivo.")
    cantidad = len(recomendaciones)
    if cantidad == 0:
        estado = "No se obtuvieron recomendaciones: revisa el historial disponible y los candidatos que superan los filtros."
    elif cantidad < top_n:
        estado = "La lista queda incompleta porque hay menos candidatos elegibles que los solicitados."
    else:
        estado = "La lista alcanza la cantidad solicitada."
    return (
        f"### Resultado del baseline\n\nSe solicitaron **{numero(top_n)}** recetas y se devolvieron **{numero(cantidad)}**. "
        f"{estado} En este baseline se excluyen recetas vistas, candidatos con datos requeridos faltantes "
        "y categorías distintas de la más frecuente. La distancia calórica solo ordena; "
        "completar la lista no demuestra relevancia ni calidad nutricional."
    )


def comentario_nmf(resultados, seleccionados):
    validos = resultados[resultados.rmse.notna() & resultados.rmse.map(lambda v: math.isfinite(float(v)) and v >= 0)]
    if validos.empty:
        return "### Interpretación del grid NMF\n\nNo hay RMSE válidos para comparar configuraciones."
    minimo = validos.rmse.min()
    mejores = validos.index[validos.rmse.eq(minimo)].tolist()
    if seleccionados not in validos.index:
        estado = f"La configuración seleccionada ({numero(seleccionados)} componentes) no tiene un RMSE válido en el grid."
    elif seleccionados in mejores:
        estado = "La configuración seleccionada alcanza el menor RMSE del grid."
    else:
        estado = f"La configuración seleccionada ({numero(seleccionados)} componentes, RMSE {numero(validos.loc[seleccionados, 'rmse'], 4)}) no minimiza el error del grid."
    return (
        f"### Interpretación del grid NMF\n\nEl menor RMSE es **{numero(minimo, 4)}**, "
        f"con **{', '.join(numero(k) for k in mejores)} componentes**. {estado} "
        "Este resultado compara las configuraciones evaluadas; no determina un óptimo universal. "
        "El grid reutiliza las interacciones ocultas: hace falta un test independiente y baselines. "
        "El RMSE de reconstrucción no mide la calidad del ranking por vecinos."
    )


def comentario_clasificacion(y_train, y_test, y_pred):
    import pandas as pd

    train, test, pred = (pd.Series(v).reset_index(drop=True) for v in (y_train, y_test, y_pred))
    if len(test) != len(pred):
        raise ValueError("Las predicciones deben corresponder a todas las filas de test.")
    if train.empty or test.empty:
        return "### Interpretación de clasificación\n\nFaltan datos de entrenamiento o evaluación."
    if any(s.isna().any() or not s.isin([0, 1]).all() for s in (train, test, pred)):
        raise ValueError("Se esperan etiquetas binarias 0/1 sin nulos.")
    mayoritaria = int(train.mode().iloc[0])
    accuracy = 100 * test.eq(pred).mean()
    baseline = 100 * test.eq(mayoritaria).mean()
    unica = pred.unique()
    estado = f"Todas las predicciones pertenecen a la clase **{int(unica[0])}**." if len(unica) == 1 else "Se predicen ambas clases."
    comparacion = "supera" if accuracy > baseline else "iguala" if accuracy == baseline else "queda por debajo de"
    recalls = []
    for clase in (0, 1):
        mask = test.eq(clase)
        valor = 100 * pred[mask].eq(clase).mean() if mask.any() else None
        recalls.append(f"clase {clase}: **{numero(valor, 2)} %** ({numero(int(mask.sum()))} casos)")
    return (
        f"### Interpretación de clasificación\n\nAccuracy: **{numero(accuracy, 2)} %** sobre **{numero(len(test))} casos**. "
        f"El baseline constante de la clase mayoritaria de entrenamiento (**{mayoritaria}**) obtiene **{numero(baseline, 2)} %** "
        f"en el mismo test: el modelo {comparacion} ese baseline en accuracy. {estado}\n\n"
        f"Recall por clase: {'; '.join(recalls)}. Si una clase no aparece en test, su recall no está definido. "
        "Revisa también F1 macro y la matriz de confusión; accuracy por sí sola no acredita discriminación. "
        "La comparación no mide calidad de ranking ni personalización: el clasificador utiliza atributos de receta."
    )
