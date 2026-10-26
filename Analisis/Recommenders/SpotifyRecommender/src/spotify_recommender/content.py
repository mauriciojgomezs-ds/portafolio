"""Recomendación por contenido; diagnóstico descriptivo sin inventar relevancia."""
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler, normalize
from sklearn.neighbors import NearestNeighbors

from .common import config, load_frame, save_model, load_model, report
from .data import MUSIC_FEATURES


def identity(cfg):
    return 'track_id' if cfg['kind'] == 'music_content' else 'show_id'


def baseline(project):
    cfg, df = config(project), load_frame(project)
    column = 'popularity' if cfg['kind'] == 'music_content' else 'release_year'
    order = df.sort_values([column, identity(cfg)], ascending=[False, True]).index.to_numpy()
    save_model(project, {'order':order}, 'baseline')
    return report(project, 'baseline', {'regla':column, 'catalogo':len(df)}, f'El baseline ordena el catálogo por **{column}** y excluye el título consultado. No utiliza interacciones de usuarios.')


def train(project):
    cfg, df = config(project), load_frame(project)
    if cfg['kind'] == 'music_content':
        transformer = StandardScaler()
        matrix = normalize(transformer.fit_transform(df[MUSIC_FEATURES]))
    else:
        transformer = TfidfVectorizer(stop_words='english', max_features=30000, ngram_range=(1,2), min_df=2)
        matrix = transformer.fit_transform(df.text)
    model = {'transformer':transformer, 'matrix':matrix, 'neighbors':NearestNeighbors(metric='cosine', algorithm='brute').fit(matrix)}
    save_model(project, model)
    return report(project, 'modelado', {'filas':matrix.shape[0], 'features':matrix.shape[1], 'metrica':'cosine'}, f'Se construyó un índice de **{matrix.shape[0]:,} elementos** con **{matrix.shape[1]:,} características**. El ajuste usa el catálogo disponible y mide similitud de contenido; no implica aprendizaje de preferencias ni accuracy predictiva.')


def recommend(project, item_id=None, top_n=10, method='modelo', *, _frame=None, _bundle=None):
    if not isinstance(top_n, int) or top_n < 1:
        raise ValueError('top_n debe ser un entero positivo.')
    cfg, df = config(project), load_frame(project) if _frame is None else _frame
    column = identity(cfg)
    item_id = item_id or df.iloc[0][column]
    matches = df.index[df[column].eq(item_id)]
    if not len(matches):
        raise ValueError(f'ID no encontrado: {item_id}')
    index = int(matches[0])
    n = min(top_n, len(df)-1)
    if method == 'baseline':
        bundle = load_model(project, 'baseline') if _bundle is None else _bundle
        indices = [int(i) for i in bundle['order'] if i != index][:n]
        scores = [None]*len(indices)
    else:
        model = load_model(project) if _bundle is None else _bundle
        distances, indices = model['neighbors'].kneighbors(model['matrix'][index:index+1], n_neighbors=min(len(df), n+1))
        pairs = [(int(i), float(1-d)) for d,i in zip(distances[0], indices[0]) if i != index][:n]
        indices, scores = [i for i,_ in pairs], [v for _,v in pairs]
    names = [column, 'track_name', 'artists', 'track_genre'] if cfg['kind']=='music_content' else [column, 'title', 'listed_in', 'description']
    result = df.iloc[indices][names].copy()
    result['similitud'] = scores
    return result.reset_index(drop=True)


def evaluate(project):
    cfg, df = config(project), load_frame(project)
    id_col = identity(cfg)
    query_indices = np.random.default_rng(cfg['seed']).choice(len(df), min(30,len(df)), replace=False)
    n = cfg.get('top_n', 10)
    results, examples = {}, {}
    for method in ('baseline', 'modelo'):
        bundle = load_model(project,method)
        returned, genres, overlaps = set(), [], []
        for index in query_indices:
            recs = recommend(project, df.iloc[index][id_col], n, method, _frame=df, _bundle=bundle)
            returned.update(recs[id_col])
            genre_col = 'track_genre' if cfg['kind']=='music_content' else 'listed_in'
            target_genres = set(str(df.iloc[index][genre_col]).split(', '))
            overlaps.extend(bool(target_genres & set(str(g).split(', '))) for g in recs[genre_col])
            genres.append(int(recs[genre_col].nunique()))
            if method not in examples:
                examples[method] = {'consulta':df.iloc[index][id_col], 'recomendaciones':recs.to_dict('records')}
        results[method] = {'consultas':len(query_indices), 'top_n_solicitado':n, 'cobertura_catalogo':len(returned)/len(df), 'categorias_distintas_promedio':float(np.mean(genres)), 'coincidencia_categoria_descriptiva':float(np.mean(overlaps))}
    results['ejemplos'] = examples
    results['limite'] = 'Sin interacciones ni juicios independientes de relevancia. La coincidencia de categoría no es accuracy ni satisfacción.'
    if cfg['kind']=='movie_content':
        results['limite'] += ' En Netflix las categorías también son entradas: su coincidencia no constituye una validación independiente.'
    coverage = results['modelo']['cobertura_catalogo']
    text = f'Se revisaron **{len(query_indices)} consultas** con top {n}. La cobertura del catálogo fue **{coverage:.2%}**. Esta cifra depende de las consultas muestreadas. '+results['limite']+'\n\nSi el catálogo tiene menos candidatos que el top solicitado, se devuelven los disponibles; se excluye la consulta y los IDs ya se deduplicaron durante preparación.'
    return report(project, 'evaluacion', results, text)
