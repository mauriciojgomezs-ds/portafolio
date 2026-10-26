"""Comunidades sobre estructura de comunicación; etiquetas reservadas al diagnóstico."""
from pathlib import Path
from urllib.request import urlopen
import gzip,io
import numpy as np
import pandas as pd
import networkx as nx
from sklearn.metrics import adjusted_rand_score,normalized_mutual_info_score
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .common import config,report,report_path,write_json,save_frame,load_frame,sha256

BASE='https://snap.stanford.edu/data/'
def setup(project):
    cfg=config(project)
    for key in ['source','labels_source']:
        path=Path(project)/cfg[key]
        if not path.exists():
            path.parent.mkdir(parents=True,exist_ok=True)
            content=urlopen(BASE+path.name,timeout=60).read()
            decoded=gzip.decompress(content)
            if not decoded.strip():raise ValueError('Fuente vacía')
            temp=path.with_suffix('.part');temp.write_bytes(content);temp.replace(path)
    return Path(project)/cfg['source']

def validate(edges,labels):
    if labels.node.duplicated().any() or labels.empty:raise ValueError('Etiquetas de nodo no válidas')
    for frame in [edges,labels]:
        if not np.isfinite(frame.to_numpy()).all() or (frame.to_numpy()%1!=0).any():raise ValueError('IDs deben ser enteros finitos')
    if not set(edges.to_numpy().ravel()).issubset(set(labels.node)):raise ValueError('Arista con nodo sin etiqueta')

def prepare(project):
    cfg=config(project);setup(project)
    edges=pd.read_csv(Path(project)/cfg['source'],sep=r'\s+',comment='#',header=None,names=['source','target'])
    labels=pd.read_csv(Path(project)/cfg['labels_source'],sep=r'\s+',header=None,names=['node','department'])
    validate(edges,labels);initial=len(edges);edges=edges.drop_duplicates();loops=int(edges.source.eq(edges.target).sum());edges=edges[edges.source.ne(edges.target)]
    save_frame(project,edges,'edges');save_frame(project,labels.sort_values('node'),'nodes')
    info={'nodos':len(labels),'departamentos':labels.department.nunique(),'aristas_originales':initial,'aristas_dirigidas_sin_bucles':len(edges),'bucles_retirados':loops,'duplicados_retirados':initial-loops-len(edges),'fuente_sha256':sha256(Path(project)/cfg['source']),'etiquetas_sha256':sha256(Path(project)/cfg['labels_source']),'particion':'Grafo completo descriptivo; sin partición predictiva'}
    return report(project,'preparacion',info,f"Se conservan **{len(labels)} nodos**, incluidos aislados, y **{len(edges)} aristas dirigidas** después de retirar {loops} bucles y duplicados. Para comunidades se proyecta a grafo no dirigido y sin pesos; una arista significa existencia de comunicación, no volumen. Los departamentos no se utilizan para elegir partición ni parámetros.")

def graphs(project):
    e=load_frame(project,'edges');nodes=load_frame(project,'nodes');g=nx.DiGraph();g.add_nodes_from(nodes.node);g.add_edges_from(e.itertuples(index=False,name=None));return g,g.to_undirected()

def partition_frame(nodes,communities):
    mapping={node:index for index,community in enumerate(sorted(communities,key=lambda c:min(c))) for node in community}
    if len(mapping)!=len(nodes) or set(mapping)!=set(nodes):raise ValueError('Partición debe cubrir todos los nodos una vez')
    if sum(len(c) for c in communities)!=len(nodes):raise ValueError('Comunidades solapadas')
    return pd.DataFrame({'node':nodes,'community':[mapping[n] for n in nodes]})

def explore(project):
    d,g=graphs(project);pr=nx.pagerank(d);nodes=load_frame(project,'nodes').node
    central=pd.DataFrame({'node':nodes,'degree':[g.degree(n) for n in nodes],'in_degree':[d.in_degree(n) for n in nodes],'out_degree':[d.out_degree(n) for n in nodes],'pagerank':[pr[n] for n in nodes]})
    central.sort_values('pagerank',ascending=False).to_csv(report_path(project,'eda','centralidad.csv'),index=False)
    sizes=sorted([len(c) for c in nx.connected_components(g)],reverse=True)
    info={'aristas_no_dirigidas':g.number_of_edges(),'componentes':len(sizes),'componente_mayor':sizes[0],'aislados':nx.number_of_isolates(g),'densidad':nx.density(g),'reciprocidad_dirigida':nx.reciprocity(d)}
    fig,axes=plt.subplots(1,2,figsize=(10,4));axes[0].hist(central.degree,bins=30);axes[0].set(title='Distribución de grado',xlabel='Vecinos distintos');axes[1].bar(range(len(sizes)),sizes);axes[1].set(title='Tamaños de componentes',xlabel='Componente',ylabel='Nodos');fig.tight_layout();fig.savefig(report_path(project,'eda','eda.png'),dpi=130);plt.close(fig)
    return report(project,'eda',info,f"La proyección tiene **{len(sizes)} componentes**, con **{sizes[0]} nodos** en la mayor y **{info['aislados']} aislados**. PageRank describe posición estructural en la red dirigida; no demuestra influencia causal, productividad ni calidad de trabajo.")

def baseline(project):
    _,g=graphs(project);communities=list(nx.connected_components(g));frame=partition_frame(sorted(g),communities);save_frame(project,frame,'baseline_partition')
    info={'comunidades':len(communities),'modularidad':nx.community.modularity(g,communities,resolution=config(project)['louvain_resolution'])}
    return report(project,'baseline',info,f"Referencia: componentes conexas, **{len(communities)} grupos**. Identifica conectividad, pero una componente grande puede reunir varios departamentos. Modularidad **{info['modularidad']:.3f}**, calculada sobre la proyección no dirigida.")

def train(project):
    cfg=config(project);_,g=graphs(project);communities=nx.community.louvain_communities(g,seed=cfg['seed'],resolution=cfg['louvain_resolution']);frame=partition_frame(sorted(g),communities);save_frame(project,frame,'model_partition')
    info={'comunidades':len(communities),'modularidad':nx.community.modularity(g,communities,resolution=cfg['louvain_resolution']),'resolucion_fija':cfg['louvain_resolution'],'semilla_declarada':cfg['seed'],'criterio':'Louvain con parámetros fijados sin consultar departamentos'}
    return report(project,'modelado',info,f"Louvain produce **{len(communities)} comunidades** y modularidad **{info['modularidad']:.3f}**. Resolución {cfg['louvain_resolution']} y semilla {cfg['seed']} declaradas; la modularidad es el objetivo del método, no evidencia independiente de utilidad ni garantía de óptimo global.")

def evaluate(project):
    cfg=config(project);_,g=graphs(project);nodes=load_frame(project,'nodes');model=load_frame(project,'model_partition');base=load_frame(project,'baseline_partition')
    joined=nodes.merge(model,on='node',validate='one_to_one');reference=joined.community.to_numpy();scores={}
    for name,frame in [('baseline',base),('modelo',model)]:
        aligned=nodes.merge(frame,on='node',validate='one_to_one');scores[name]={'ari_departamentos':float(adjusted_rand_score(aligned.department,aligned.community)),'nmi_departamentos':float(normalized_mutual_info_score(aligned.department,aligned.community))}
    stability=[]
    for seed in cfg['stability_seeds']:
        trial=partition_frame(sorted(g),nx.community.louvain_communities(g,seed=seed,resolution=cfg['louvain_resolution']));aligned=nodes.merge(trial,on='node');stability.append({'semilla':seed,'ari_con_particion_declarada':adjusted_rand_score(reference,aligned.community)})
    rng=np.random.default_rng(cfg['seed']);null=[adjusted_rand_score(rng.permutation(joined.department),reference) for _ in range(cfg['null_permutations'])]
    other=[r['ari_con_particion_declarada'] for r in stability if r['semilla']!=cfg['seed']]
    info={**scores,'ari_estabilidad_medio_otras_semillas':float(np.mean(other)),'ari_nulo_media':float(np.mean(null)),'ari_nulo_percentil95':float(np.quantile(null,.95)),'permutaciones':len(null),'protocolo':'Diagnóstico transductivo en la misma red; no accuracy ni evaluación fuera de muestra'}
    joined.to_csv(report_path(project,'evaluacion','comunidades_departamentos.csv'),index=False);pd.DataFrame(stability).to_csv(report_path(project,'evaluacion','estabilidad_semillas.csv'),index=False);pd.DataFrame({'ari_nulo':null}).to_csv(report_path(project,'evaluacion','referencia_permutada.csv'),index=False)
    fig,axes=plt.subplots(1,2,figsize=(11,4));axes[0].bar([str(r['semilla']) for r in stability],[r['ari_con_particion_declarada'] for r in stability]);axes[0].set(title='Estabilidad respecto a semilla declarada',ylabel='ARI',ylim=(0,1));matrix=pd.crosstab(joined.community,joined.department);im=axes[1].imshow(matrix,aspect='auto',cmap='Blues');axes[1].set(title='Comunidad × departamento',xlabel='Departamento',ylabel='Comunidad');fig.colorbar(im,ax=axes[1],label='Nodos');fig.tight_layout();fig.savefig(report_path(project,'evaluacion','evaluacion.png'),dpi=130);plt.close(fig)
    return report(project,'evaluacion',info,f"Coincidencia con departamentos: ARI **{scores['modelo']['ari_departamentos']:.3f}**, NMI **{scores['modelo']['nmi_departamentos']:.3f}**. Estabilidad media frente a otras semillas: ARI **{info['ari_estabilidad_medio_otras_semillas']:.3f}**. La referencia permutada tiene ARI medio **{info['ari_nulo_media']:.3f}**. Departamentos y comunidades describen agrupaciones distintas; el contraste se realiza en la misma red y no acredita predicción de nuevos nodos. Las permutaciones son una referencia descriptiva, no validación causal.")

def run_stage(project,stage):return {'preparacion':prepare,'eda':explore,'baseline':baseline,'modelado':train,'evaluacion':evaluate}[stage](project)
