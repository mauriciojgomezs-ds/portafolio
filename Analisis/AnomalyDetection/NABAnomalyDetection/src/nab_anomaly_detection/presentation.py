"""Tablas y figuras de evaluación visibles sin imprimir reportes extensos."""
import pandas as pd
from IPython.display import display, Image
from .common import config


def display_evaluation(project,metrics):
    kind = config(project)['kind']
    if 'baseline' in metrics and isinstance(metrics['baseline'],dict) and 'modelo' in metrics:
        table = {name:{k:v for k,v in metrics[name].items() if isinstance(v,(int,float)) or v is None} for name in ('baseline','modelo')}
        display(pd.DataFrame(table))
    if kind in ('text_genre','text_sentiment'):
        display(pd.DataFrame(metrics['modelo']['clasificacion']).T)
    elif kind in ('cluster_music','cluster_customers'):
        display(pd.DataFrame(metrics['perfiles']))
        display(Image(filename=str(project/'reports/evaluacion/clusters.png')))
    elif kind in ('music_content','movie_content'):
        for name,example in metrics['ejemplos'].items():
            print(f'{name}: consulta {example["consulta"]}')
            display(pd.DataFrame(example['recomendaciones']))
    elif kind == 'collaborative':
        print(f'Usuario del ejemplo: {metrics["ejemplo"]["usuario"]}')
        display(pd.DataFrame({'movieId':metrics['ejemplo']['movie_ids'],'title':metrics['ejemplo']['titulos']}))
    elif kind in ('forecast','anomaly'):
        display(pd.read_csv(project/'reports/evaluacion/predicciones_test.csv').head(10))
        display(Image(filename=str(project/'reports/evaluacion/evaluacion.png')))
