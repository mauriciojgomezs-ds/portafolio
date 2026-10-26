"""Ranking por vecinos de usuarios sobre una muestra reproducible de MovieLens."""
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.preprocessing import normalize

from .common import config, load_frame, save_model, load_model, report


def build(project):
    train = load_frame(project,'train')
    users = sorted(train.userId.unique().tolist())
    movies = sorted(train.movieId.unique().tolist())
    ui, mi = {v:i for i,v in enumerate(users)}, {v:i for i,v in enumerate(movies)}
    positive = train[train.rating >= 4]
    likes = csr_matrix((np.ones(len(positive)),(positive.userId.map(ui),positive.movieId.map(mi))),shape=(len(users),len(movies)))
    seen = csr_matrix((np.ones(len(train)),(train.userId.map(ui),train.movieId.map(mi))),shape=likes.shape)
    normalized = normalize(likes)
    similarity = (normalized @ normalized.T).toarray()
    np.fill_diagonal(similarity,0)
    popularity = np.asarray(likes.sum(axis=0)).ravel()
    return {'users':users,'movies':movies,'user_index':ui,'movie_index':mi,'likes':likes,'seen':seen,'similarity':similarity,'popularity':popularity}


def recommend_ids(bundle,user,neighbors=None,top_n=10):
    index = bundle['user_index'].get(int(user))
    if index is None:
        raise ValueError('Usuario fuera de la muestra de entrenamiento.')
    if neighbors is None:
        scores = bundle['popularity'].copy()
    else:
        weights = bundle['similarity'][index]
        selected = np.argsort(-weights,kind='stable')[:neighbors]
        scores = np.asarray(bundle['likes'][selected].T @ weights[selected]).ravel()
    seen = bundle['seen'][index].indices
    scores[seen] = -np.inf
    # Sin señal positiva no se inventan recomendaciones de vecinos.
    candidates = np.flatnonzero(np.isfinite(scores) & (scores > 0))
    order = candidates[np.argsort(-scores[candidates],kind='stable')[:top_n]]
    return [bundle['movies'][i] for i in order]


def ranking_metrics(bundle,holdout,neighbors,top_n):
    positive = holdout[holdout.rating >= 4]
    hits, ndcg, lengths, returned = [], [], [], set()
    cold = 0
    for row in positive.itertuples():
        recs = recommend_ids(bundle,row.userId,neighbors,top_n)
        cold += int(row.movieId not in bundle['movie_index'])
        hit = int(row.movieId in recs)
        hits.append(hit)
        ndcg.append(1/np.log2(recs.index(row.movieId)+2) if hit else 0.)
        lengths.append(len(recs))
        returned.update(recs)
    return {'usuarios_con_objetivo_positivo':len(positive),'objetivos_sin_historial_item':cold,'hit_rate_at_k':float(np.mean(hits)) if hits else None,'ndcg_at_k':float(np.mean(ndcg)) if hits else None,'recomendaciones_promedio':float(np.mean(lengths)) if lengths else None,'cobertura_items_train':len(returned)/len(bundle['movies']),'k':top_n}


def baseline(project):
    bundle = build(project)
    save_model(project,bundle,'baseline')
    result = ranking_metrics(bundle,load_frame(project,'valid'),None,config(project).get('top_n',10))
    return report(project,'baseline',result,'El baseline recomienda películas con más valoraciones positivas de train, excluyendo las ya valoradas por cada usuario. La evaluación cuenta un único objetivo positivo retenido por usuario; los objetivos sin historial también cuentan como fallos.')


def train(project):
    bundle = load_model(project,'baseline')
    valid = load_frame(project,'valid')
    k = config(project).get('top_n',10)
    candidates = [{'vecinos':n,**ranking_metrics(bundle,valid,n,k)} for n in (10,30)]
    if candidates[0]['ndcg_at_k'] is None:
        raise ValueError('Validación sin objetivos positivos: no se puede seleccionar por NDCG.')
    best = max(candidates,key=lambda c:c['ndcg_at_k'])
    bundle['neighbors'] = best['vecinos']
    save_model(project,bundle)
    result = {'criterio':'ndcg_validacion','vecinos_elegidos':best['vecinos'],'candidatos':candidates}
    return report(project,'modelado',result,f'Se eligieron **{best["vecinos"]} vecinos** por NDCG@{k} en validación. La similitud usa únicamente valoraciones positivas de train; se excluyen todas las películas ya valoradas en train, incluso las negativas. No se reentrena con validación.')


def evaluate(project):
    bundle = load_model(project)
    test = load_frame(project,'test')
    k = config(project).get('top_n',10)
    results = {name:ranking_metrics(bundle,test,n,k) for name,n in [('baseline',None),('modelo',bundle['neighbors'])]}
    model, base = results['modelo'],results['baseline']
    if model['ndcg_at_k'] is None:
        comment = 'No hay objetivos positivos en test; NDCG y hit rate no están definidos.'
    else:
        relation = 'supera' if model['ndcg_at_k'] > base['ndcg_at_k'] else 'no supera'
        comment = f'El modelo {relation} el baseline por NDCG@{k}: **{model["ndcg_at_k"]:.4f}** frente a **{base["ndcg_at_k"]:.4f}**, en **{model["usuarios_con_objetivo_positivo"]} objetivos positivos**. Hay **{model["objetivos_sin_historial_item"]} objetivos sin historial del ítem** en train.'
    comment += '\n\nSe evalúa una muestra de usuarios existentes con un objetivo retenido por usuario; no mide satisfacción real ni usuarios nuevos. Los cortes son temporales por usuario, no un corte global: las interacciones de otros usuarios pueden ser posteriores al objetivo de un usuario. Un top solicitado puede quedar incompleto si no hay suficientes candidatos con señal positiva.'
    movies = load_frame(project)
    example_user = bundle['users'][0]
    recommendations = recommend_ids(bundle,example_user,bundle['neighbors'],k)
    results['ejemplo'] = {'usuario':example_user,'movie_ids':recommendations,'titulos':movies.set_index('movieId').reindex(recommendations).title.tolist()}
    return report(project,'evaluacion',results,comment)
