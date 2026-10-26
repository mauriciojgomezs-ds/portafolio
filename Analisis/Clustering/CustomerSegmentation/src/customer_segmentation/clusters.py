"""Segmentación descriptiva con selección de k y estabilidad entre semillas."""
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, adjusted_rand_score
from sklearn.decomposition import PCA
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from .common import config, load_frame, save_model, load_model, report, save_frame, report_path
from .data import MUSIC_FEATURES


def features(project):
    df = load_frame(project)
    cols = ['recency','frequency','monetary'] if config(project)['kind']=='cluster_customers' else MUSIC_FEATURES
    x = df[cols].to_numpy()
    if config(project)['kind']=='cluster_customers':
        x = np.log1p(x)
    return df, cols, x


def baseline(project):
    df, cols, x = features(project)
    if config(project)['kind']=='cluster_customers':
        # Regla explícita de comparación: grupos de importe por cuantiles.
        labels = pd.qcut(df.monetary.rank(method='first'),3,labels=False).to_numpy()
        rule = 'Tres grupos por terciles de importe (desempates por orden de cliente).'
    else:
        labels = pd.cut(df.energy,[-np.inf,.33,.66,np.inf],labels=False).to_numpy()
        rule = 'Tres grupos por energía: <=0.33, (0.33,0.66], >0.66.'
    scaler = StandardScaler().fit(x)
    score = float(silhouette_score(scaler.transform(x),labels,sample_size=min(2000,len(x)),random_state=42)) if len(np.unique(labels))>1 else None
    save_model(project,{'labels':labels,'rule':rule,'silhouette':score},'baseline')
    return report(project,'baseline',{'regla':rule,'silhouette':score},f'Baseline descriptivo: {rule} La silhouette mide separación en el espacio estandarizado; no valida por sí sola la utilidad de los grupos.')


def train(project):
    df, cols, x = features(project)
    seed = config(project)['seed']
    scaler = StandardScaler().fit(x)
    transformed = scaler.transform(x)
    candidates, models = [], []
    for k in (3,4,5):
        if k >= len(x):
            continue
        model = KMeans(n_clusters=k,n_init=10,random_state=seed).fit(transformed)
        score = float(silhouette_score(transformed,model.labels_,sample_size=min(2000,len(x)),random_state=seed))
        candidates.append({'k':k,'silhouette':score,'inercia':float(model.inertia_)})
        models.append(model)
    best = max(range(len(candidates)),key=lambda i:candidates[i]['silhouette'])
    save_model(project,{'model':models[best],'scaler':scaler,'columns':cols})
    result = {'criterio':'silhouette_descriptiva','k_elegido':candidates[best]['k'],'candidatos':candidates}
    return report(project,'modelado',result,f'Se eligió **k={result["k_elegido"]}** por silhouette en la población descriptiva. Este análisis no utiliza etiquetas de verdad ni representa validación predictiva fuera de muestra.')


def evaluate(project):
    df, cols, x = features(project)
    bundle = load_model(project)
    model = bundle['model']
    transformed = bundle['scaler'].transform(x)
    alternate = KMeans(n_clusters=model.n_clusters,n_init=10,random_state=config(project)['seed']+1).fit_predict(transformed)
    stability = float(adjusted_rand_score(model.labels_,alternate))
    df['cluster'] = model.labels_
    profiles = df.groupby('cluster')[cols].mean().round(4)
    profiles['registros'] = df.groupby('cluster').size()
    save_frame(project,df,'segmentos')
    profiles.to_csv(report_path(project, 'evaluacion', 'perfiles_clusters.csv'))
    pca = PCA(n_components=2,random_state=42)
    projected = pca.fit_transform(transformed)
    fig,ax = plt.subplots(figsize=(8,5))
    points = ax.scatter(projected[:,0],projected[:,1],c=model.labels_,s=5,alpha=.4,cmap=plt.get_cmap('tab10',model.n_clusters),vmin=-.5,vmax=model.n_clusters-.5)
    fig.colorbar(points,ax=ax,ticks=range(model.n_clusters),label='Cluster')
    ax.set(xlabel='Componente 1',ylabel='Componente 2',title='Proyección PCA de los grupos')
    fig.tight_layout()
    fig.savefig(report_path(project, 'evaluacion', 'clusters.png'),dpi=130)
    plt.close(fig)
    result = {'k':model.n_clusters,'ari_entre_semillas':stability,'varianza_pca_2d':float(pca.explained_variance_ratio_.sum()),'perfiles':profiles.reset_index().to_dict('records'),'baseline':load_model(project,'baseline')['silhouette']}
    qualifier = 'similar' if stability >= .8 else 'sensible a la inicialización'
    comment = f'La segmentación es **{qualifier}** entre las dos semillas revisadas (ARI **{stability:.4f}**; corte descriptivo 0,8). La proyección de dos componentes conserva **{result["varianza_pca_2d"]:.2%}** de la varianza. Los perfiles están expresados en las unidades originales. Los números de cluster no tienen significado ordinal ni equivalen a segmentos de negocio validados.'
    return report(project,'evaluacion',result,comment)
