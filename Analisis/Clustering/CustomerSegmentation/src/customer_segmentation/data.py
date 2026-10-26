"""Preparación diferenciada por tarea; mantiene las fuentes originales."""
from io import BytesIO
from zipfile import ZipFile
import re

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, GroupShuffleSplit

from .common import config, root_for, save_frame, report, sha256

MUSIC_FEATURES = ['danceability', 'energy', 'loudness', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 'duration_ms']


def csv_zip(path, member, **kwargs):
    with ZipFile(path) as archive, archive.open(member) as stream:
        return pd.read_csv(stream, **kwargs)


def normalize_text(value):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', str(value))).strip().lower()


def text_partitions(df, seed=42, supplied_test=None, groups=None):
    """Deduplicación previa al split; test externo conserva su identidad."""
    df = df.copy()
    df['text_key'] = df['text'].map(normalize_text)
    df = df[df.text_key.str.len() > 0].drop_duplicates('text_key').copy()
    if supplied_test is not None:
        test = supplied_test.copy()
        test['text_key'] = test['text'].map(normalize_text)
        test = test[test.text_key.str.len() > 0].drop_duplicates('text_key').copy()
        df = df[~df.text_key.isin(test.text_key)].copy()
    elif groups is not None:
        # El grupo (título normalizado) evita títulos repetidos a ambos lados.
        split = GroupShuffleSplit(n_splits=1, test_size=.2, random_state=seed)
        a, b = next(split.split(df, groups=df[groups]))
        df, test = df.iloc[a].copy(), df.iloc[b].copy()
    else:
        df, test = train_test_split(df, test_size=.2, random_state=seed, stratify=df['label'])
    if groups is not None:
        split = GroupShuffleSplit(n_splits=1, test_size=.25, random_state=seed)
        a, b = next(split.split(df, groups=df[groups]))
        train, valid = df.iloc[a].copy(), df.iloc[b].copy()
    else:
        train, valid = train_test_split(df, test_size=.2, random_state=seed, stratify=df['label'])
    return {'train': train, 'valid': valid, 'test': test}


def retail_clean(df):
    df = df.copy()
    df['InvoiceDate'] = pd.to_datetime(df.InvoiceDate, errors='coerce')
    mask = df.InvoiceDate.notna() & (df.Quantity > 0) & (df.UnitPrice > 0) & ~df.InvoiceNo.astype(str).str.startswith('C')
    cleaned = df[mask].drop_duplicates().copy()
    cleaned['amount'] = cleaned.Quantity * cleaned.UnitPrice
    return cleaned


def prepare(project):
    cfg = config(project)
    kind = cfg['kind']
    root = root_for(project)
    source = root / cfg['source']
    info = {'fuente': cfg['source'], 'semilla': cfg.get('seed', 42)}
    if not source.exists():
        raise FileNotFoundError(f'No se encontró la fuente: {source}')
    info['sha256'] = sha256(source)
    seed = cfg.get('seed', 42)
    parts = None
    if kind in ('music_content', 'cluster_music'):
        df = csv_zip(source, 'dataset.csv').drop(columns=['Unnamed: 0'], errors='ignore')
        info['filas_originales'] = len(df)
        for col in MUSIC_FEATURES:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df = df.replace([np.inf, -np.inf], np.nan).dropna(subset=['track_id', *MUSIC_FEATURES])
        info['duplicados_track_id'] = int(df.duplicated('track_id').sum())
        df = df.drop_duplicates('track_id').sort_values('track_id').reset_index(drop=True)
        # Primera fila por ID conserva metadatos, no implica un único género real.
        if kind == 'cluster_music':
            cap = cfg.get('max_tracks', 20000)
            if len(df) > cap:
                df = df.sample(cap, random_state=seed).sort_values('track_id').reset_index(drop=True)
    elif kind in ('movie_content', 'text_genre'):
        df = csv_zip(source, 'netflix_titles.csv')
        info['filas_originales'] = len(df)
        df = df.dropna(subset=['show_id', 'title']).drop_duplicates('show_id').copy()
        df['description'] = df.description.fillna('')
        if kind == 'text_genre':
            df = df[df.type.eq('Movie') & df.description.str.strip().ne('')].copy()
            df['text'] = df.description
            df['labels'] = df.listed_in.fillna('').map(lambda s: [x.strip() for x in s.split(',') if x.strip()])
            df['title_key'] = df.title.map(normalize_text)
            df = df[df.labels.map(len) > 0]
            parts = text_partitions(df, seed, groups='title_key')
        else:
            df['text'] = df[['description', 'listed_in', 'cast', 'director']].fillna('').agg(' '.join, axis=1)
    elif kind == 'text_sentiment':
        train = pd.read_parquet(source)
        test_source = root / cfg['test_source']
        test = pd.read_parquet(test_source)
        info.update(filas_originales=len(train) + len(test), sha256_test=sha256(test_source))
        parts = text_partitions(train, seed, supplied_test=test)
        df = pd.concat(parts.values())
    elif kind in ('cluster_customers', 'forecast'):
        with ZipFile(source) as archive:
            df = pd.read_excel(BytesIO(archive.read('Online Retail.xlsx')), engine='openpyxl')
        info['filas_originales'] = len(df)
        raw_dates = pd.to_datetime(df.InvoiceDate, errors='coerce').dropna()
        df = retail_clean(df)
        info['politica_ventas'] = 'Compras positivas; excluye cancelaciones, devoluciones, precios no positivos y duplicados exactos. No mide ingresos netos.'
        if kind == 'cluster_customers':
            df = df.dropna(subset=['CustomerID']).copy()
            df['CustomerID'] = df.CustomerID.astype('int64').astype(str)
            anchor = df.InvoiceDate.max().normalize() + pd.Timedelta(days=1)
            df = df.groupby('CustomerID').agg(last_date=('InvoiceDate', 'max'), frequency=('InvoiceNo', 'nunique'), monetary=('amount', 'sum')).reset_index()
            df['recency'] = (anchor - df.last_date).dt.total_seconds() / 86400
            info['fecha_referencia'] = anchor.isoformat()
        else:
            # Cortes de calendario detectados en registros de origen, no en las ventas limpiadas.
            low, high = raw_dates.min().normalize(), raw_dates.max().normalize()
            series = df.set_index('InvoiceDate').amount.resample('W-SUN').sum()
            # Solo semanas lunes-domingo totalmente cubiertas por el rango observado.
            series = series[(series.index - pd.Timedelta(days=6) >= low) & (series.index <= high)]
            df = series.rename('value').reset_index().rename(columns={'InvoiceDate': 'timestamp'})
            info['unidad'] = 'Importe semanal de compras positivas, en moneda de la fuente (confirmar GBP).'
    elif kind == 'anomaly':
        with ZipFile(source) as archive:
            prefix = next(n[:-len('labels/combined_windows.json')] for n in archive.namelist() if n.endswith('labels/combined_windows.json'))
            import json
            windows = json.loads(archive.read(prefix + 'labels/combined_windows.json'))[cfg['series']]
            df = pd.read_csv(BytesIO(archive.read(prefix + 'data/' + cfg['series'])))
        df['timestamp'] = pd.to_datetime(df.timestamp)
        df = df.sort_values('timestamp').drop_duplicates('timestamp')
        df['label'] = 0
        for start, end in windows:
            df.loc[df.timestamp.between(pd.Timestamp(start), pd.Timestamp(end)), 'label'] = 1
        info.update(filas_originales=len(df), serie=cfg['series'], ventanas=windows)
        n = len(df)
        parts = {'train': df.iloc[:int(.6*n)].copy(), 'valid': df.iloc[int(.6*n):int(.8*n)].copy(), 'test': df.iloc[int(.8*n):].copy()}
    elif kind == 'collaborative':
        users = set()
        with ZipFile(source) as archive, archive.open('ml-32m/ratings.csv') as stream:
            for chunk in pd.read_csv(stream, usecols=['userId'], chunksize=1000000):
                users.update(chunk.userId.unique().tolist())
        selected = set(np.random.default_rng(seed).choice(sorted(users), min(cfg.get('max_users', 800), len(users)), replace=False).tolist())
        frames = []
        with ZipFile(source) as archive, archive.open('ml-32m/ratings.csv') as stream:
            for chunk in pd.read_csv(stream, chunksize=1000000):
                frames.append(chunk[chunk.userId.isin(selected)])
        ratings = pd.concat(frames, ignore_index=True).drop_duplicates(['userId', 'movieId']).sort_values(['userId', 'timestamp', 'movieId'])
        counts = ratings.groupby('userId').movieId.transform('size')
        ratings = ratings[counts >= 5].copy()
        rank = ratings.groupby('userId').cumcount(ascending=False)
        parts = {'train': ratings[rank >= 2], 'valid': ratings[rank == 1], 'test': ratings[rank == 0]}
        df = csv_zip(source, 'ml-32m/movies.csv')
        info.update(filas_originales_usuarios=len(users), usuarios_muestreados=len(selected), ratings_muestra=len(ratings), protocolo='Últimas dos valoraciones por usuario para valid/test; positivos rating >= 4. No es un corte temporal global.')
    else:
        raise ValueError(f'Tarea desconocida: {kind}')
    save_frame(project, df.reset_index(drop=True))
    info['filas_preparadas'] = len(df)
    if kind == 'forecast':
        from .temporal import forecast_split
        parts = forecast_split(project)
    if parts is not None:
        info['particiones'] = {}
        for name, part in parts.items():
            save_frame(project, part.reset_index(drop=True), name)
            info['particiones'][name] = {'filas': len(part)}
            if 'label' in part:
                info['particiones'][name]['clases'] = {str(k): int(v) for k, v in part.label.value_counts().items()}
        if 'text_key' in next(iter(parts.values())):
            assert not set(parts['train'].text_key) & set(parts['test'].text_key)
            assert not set(parts['train'].text_key) & set(parts['valid'].text_key)
            info['textos_compartidos'] = 0
    return report(project, 'preparacion', info, f'Se prepararon **{len(df):,} registros**. La fuente y sus huellas se registran en el JSON. '+ ('Se persistieron train, validación y test según el protocolo documentado.' if parts else 'Esta etapa construye un catálogo o una población descriptiva; no implica una evaluación supervisada.'))
