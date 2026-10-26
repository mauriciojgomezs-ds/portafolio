"""Visualización compacta de las métricas y errores calculados."""
import pandas as pd
from IPython.display import display, Image

def display_evaluation(project, metrics):
    display(pd.DataFrame({name:{k:metrics[name][k] for k in ('casos','accuracy','f1_macro')} for name in ('baseline','modelo')}))
    display(pd.DataFrame(metrics['modelo']['clasificacion']).T)
    display(pd.DataFrame(metrics['confusiones_principales']))
    for name in ('evaluacion.png','errores_visuales.png'):
        display(Image(filename=str(project/'reports/evaluacion'/name)))
