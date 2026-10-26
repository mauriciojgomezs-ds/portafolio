"""Etapas compartidas: datos, EDA, baseline, selección y test reservado."""

import hashlib
import json
from pathlib import Path
import zipfile

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, average_precision_score, classification_report, confusion_matrix, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def configuracion(proyecto):
    proyecto = Path(proyecto)
    cfg = json.loads((proyecto / "config.json").read_text(encoding="utf-8"))
    for carpeta in ["data/raw", "data/processed", "models", "reports", "reports/entorno", "reports/preparacion", "reports/eda", "reports/baseline", "reports/modelado", "reports/evaluacion"]:
        (proyecto / carpeta).mkdir(parents=True, exist_ok=True)
    return cfg


def guardar_json(ruta, contenido):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(contenido, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")


def preparar(proyecto):
    proyecto = Path(proyecto)
    cfg = configuracion(proyecto)
    objetivo = cfg["target"]
    tablas, inventario = {}, []
    with zipfile.ZipFile(proyecto / cfg["source_zip"]) as archivo:
        for rol, nombre in cfg["members"].items():
            # Solo se escribe el basename declarado: nunca se extraen rutas del ZIP.
            destino = proyecto / "data/raw" / Path(nombre).name
            contenido = archivo.read(nombre)
            destino.write_bytes(contenido)
            df = pd.read_csv(destino)
            filas = len(df)
            sin_target = int(df[objetivo].isna().sum())
            df = df.dropna(subset=[objetivo]).copy()
            if not df[objetivo].isin([0, 1]).all():
                raise ValueError(f"{nombre}: target distinto de 0/1")
            df[objetivo] = df[objetivo].astype(int)
            df = df.drop_duplicates().reset_index(drop=True)
            tablas[rol] = df
            inventario.append({"archivo": nombre, "sha256": hashlib.sha256(contenido).hexdigest(),
                               "filas_originales": filas, "filas_sin_target": sin_target,
                               "filas_utilizables": len(df)})
    if cfg["split"] == "temporal":
        df = tablas["full"].copy()
        df[cfg["date"]] = pd.to_datetime(df[cfg["date"]], errors="raise")
        fechas = sorted(df[cfg["date"]].unique())
        if len(fechas) < 3:
            raise ValueError("Se requieren al menos tres fechas para train/valid/test.")
        train = df[df[cfg["date"]] < fechas[-2]].copy()
        valid = df[df[cfg["date"]] == fechas[-2]].copy()
        test = df[df[cfg["date"]] == fechas[-1]].copy()
    elif cfg["split"] == "provided":
        train, valid = train_test_split(tablas["train"], test_size=0.2, stratify=tablas["train"][objetivo], random_state=42)
        test = tablas["test"]
    else:
        parcial, test = train_test_split(tablas["full"], test_size=0.2, stratify=tablas["full"][objetivo], random_state=42)
        train, valid = train_test_split(parcial, test_size=0.25, stratify=parcial[objetivo], random_state=42)
    resumen = {"fuentes": inventario, "particion": cfg["split"], "semilla": 42, "datasets": {}}
    for nombre, df in [("train", train), ("valid", valid), ("test", test)]:
        if df.empty:
            raise ValueError(f"La partición {nombre} está vacía.")
        df.to_parquet(proyecto / "data/processed" / f"{nombre}.parquet", index=False)
        resumen["datasets"][nombre] = {"filas": len(df), "columnas": len(df.columns), "positivos": int(df[objetivo].sum())}
    ids = cfg.get("id")
    resumen["ids_compartidos_train_test"] = (
        len(set(train[ids].dropna()) & set(test[ids].dropna())) if ids else None
    )
    if not ids:
        resumen["limitacion_identidad"] = "Sin ID de cliente: no se puede comprobar independencia por persona."
        resumen["filas_identicas_train_test"] = len(train.merge(test, on=list(train.columns), how="inner"))
        resumen["filas_identicas_valid_test"] = len(valid.merge(test, on=list(valid.columns), how="inner"))
    guardar_json(proyecto / "reports/preparacion/preparacion.json", resumen)
    return pd.DataFrame(resumen["datasets"]).T


def cargar(proyecto, particion):
    return pd.read_parquet(Path(proyecto) / "data/processed" / f"{particion}.parquet")


def explorar(proyecto):
    import matplotlib.pyplot as plt

    proyecto = Path(proyecto)
    cfg = configuracion(proyecto)
    df = cargar(proyecto, "train")
    tasa = float(df[cfg["target"]].mean())
    resumen = {"filas_train": len(df), "positivos": int(df[cfg["target"]].sum()), "proporcion_positiva": tasa,
               "nulos": {c: int(v) for c, v in df.isna().sum().items()}, "features_excluidas": cfg["exclude"]}
    guardar_json(proyecto / "reports/eda/eda.json", resumen)
    diagnostico = "La clase positiva es minoritaria." if tasa < 0.5 else "La clase negativa es minoritaria." if tasa > 0.5 else "Las clases tienen igual frecuencia."
    texto = f"# EDA de entrenamiento\n\nRegistros: **{len(df):,}**. Churn positivo: **{tasa:.2%}**. {diagnostico}\n\n"
    texto += "Se explora solo train: validación selecciona el modelo y test queda reservado. No se infiere causalidad ni representatividad de estas cifras.\n\n"
    texto += "## Nulos por columna\n\n```text\n" + df.isna().sum().to_frame("nulos").to_string() + "\n```\n\n"
    texto += "## Atributos excluidos\n\n" + ", ".join(cfg["exclude"]) + "\n"
    (proyecto / "reports/eda/eda.md").write_text(texto, encoding="utf-8")
    fig, ax = plt.subplots(figsize=(6, 4))
    df[cfg["target"]].value_counts().sort_index().plot.bar(ax=ax)
    ax.set(xlabel="Clase", ylabel="Registros", title="Distribución del objetivo en train")
    fig.tight_layout()
    fig.savefig(proyecto / "reports/eda/distribucion_target.png")
    plt.close(fig)
    return texto


def features(df, cfg):
    X = df.drop(columns=[cfg["target"], *cfg["exclude"]], errors="ignore").copy()
    for columna in cfg.get("categorical_columns", []):
        if columna not in X:
            raise ValueError(f"La categoría configurada {columna} no está en las features.")
        # Un código numérico de categoría no representa una magnitud continua.
        X[columna] = X[columna].map(lambda v: str(v) if pd.notna(v) else np.nan)
    return X


def metricas(modelo, X, y):
    pred = modelo.predict(X)
    clases = list(modelo.classes_)
    proba = modelo.predict_proba(X)[:, clases.index(1)] if 1 in clases else np.zeros(len(X))
    dos_clases = len(pd.unique(y)) == 2
    return {"casos": len(y), "accuracy": float(accuracy_score(y, pred)),
            "average_precision": float(average_precision_score(y, proba)) if dos_clases else None,
            "roc_auc": float(roc_auc_score(y, proba)) if dos_clases else None,
            "matriz_confusion": confusion_matrix(y, pred, labels=[0, 1]).tolist(),
            "clasificacion": classification_report(y, pred, labels=[0, 1], zero_division=0, output_dict=True)}


def baseline(proyecto):
    proyecto = Path(proyecto)
    cfg = configuracion(proyecto)
    train, valid = cargar(proyecto, "train"), cargar(proyecto, "valid")
    modelo = DummyClassifier(strategy="prior", random_state=42)
    modelo.fit(features(train, cfg), train[cfg["target"]])
    joblib.dump(modelo, proyecto / "models/baseline.joblib")
    resultado = metricas(modelo, features(valid, cfg), valid[cfg["target"]])
    guardar_json(proyecto / "reports/baseline/baseline_validacion.json", resultado)
    return resultado


def entrenar(proyecto):
    proyecto = Path(proyecto)
    cfg = configuracion(proyecto)
    train, valid = cargar(proyecto, "train"), cargar(proyecto, "valid")
    X, y = features(train, cfg), train[cfg["target"]]
    numericas = X.select_dtypes(include="number").columns.tolist()
    categoricas = [c for c in X.columns if c not in numericas]
    resultados = []
    for peso in [None, "balanced"]:
        pre = ColumnTransformer([
            ("num", Pipeline([("nulos", SimpleImputer(strategy="median")), ("escala", StandardScaler())]), numericas),
            ("cat", Pipeline([("nulos", SimpleImputer(strategy="most_frequent")), ("ohe", OneHotEncoder(handle_unknown="ignore"))]), categoricas),
        ])
        modelo = Pipeline([("pre", pre), ("clf", LogisticRegression(max_iter=1000, class_weight=peso, random_state=42))])
        modelo.fit(X, y)
        evaluacion = metricas(modelo, features(valid, cfg), valid[cfg["target"]])
        if evaluacion["average_precision"] is None:
            raise ValueError("Validación necesita ambas clases para seleccionar por average precision.")
        resultados.append((peso, modelo, evaluacion))
    elegido = max(resultados, key=lambda r: r[2]["average_precision"])
    joblib.dump(elegido[1], proyecto / "models/modelo.joblib")
    resumen = {"criterio": "average_precision_validacion", "class_weight_elegido": elegido[0],
               "candidatos": [{"class_weight": p, **m} for p, _, m in resultados]}
    guardar_json(proyecto / "reports/modelado/modelos_validacion.json", resumen)
    from .decisiones import entrenar_decisiones
    entrenar_decisiones(proyecto)
    return pd.DataFrame([{ "class_weight": p or "sin ponderar", "accuracy": m["accuracy"], "average_precision": m["average_precision"]} for p, _, m in resultados])


def evaluar(proyecto):
    proyecto = Path(proyecto)
    cfg = configuracion(proyecto)
    test = cargar(proyecto, "test")
    resultado = {nombre: metricas(joblib.load(proyecto / "models" / archivo), features(test, cfg), test[cfg["target"]])
                 for nombre, archivo in [("baseline", "baseline.joblib"), ("modelo", "modelo.joblib")]}
    guardar_json(proyecto / "reports/evaluacion/evaluacion_test.json", resultado)
    comparacion = pd.DataFrame({k: {m: v[m] for m in ["accuracy", "average_precision", "roc_auc"]} for k, v in resultado.items()}).T
    diferencia = resultado["modelo"]["accuracy"] - resultado["baseline"]["accuracy"]
    lectura = "supera" if diferencia > 0 else "iguala" if diferencia == 0 else "queda por debajo de"
    texto = f"# Evaluación final\n\nCasos de test: **{len(test):,}**. El modelo **{lectura}** el baseline en accuracy.\n\n"
    texto += "```text\n" + comparacion.to_string() + "\n```\n\n"
    texto += "Las métricas describen esta partición. Revisar recall por clase y matriz de confusión en el JSON; no ajustar parámetros ni thresholds con este test. La definición del churn y la disponibilidad temporal de las features deben confirmarse en la fuente.\n"
    from .decisiones import evaluar_decisiones
    texto += "\n" + evaluar_decisiones(proyecto)
    (proyecto / "reports/evaluacion/evaluacion.md").write_text(texto, encoding="utf-8")
    return texto
