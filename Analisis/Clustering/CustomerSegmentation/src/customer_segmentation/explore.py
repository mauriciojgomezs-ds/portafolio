"""EDA sobre train cuando hay particiones, sobre la población en tareas descriptivas."""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from .common import config, load_frame, data_path, report, report_path
from .data import MUSIC_FEATURES


def explore(project):
    cfg = config(project)
    name = 'train' if data_path(project, 'train').exists() else 'catalogo'
    df = load_frame(project, name)
    info = {'poblacion': name, 'filas': len(df), 'columnas': len(df.columns), 'nulos': {k: int(v) for k, v in df.isna().sum().items()}}
    numeric = df.select_dtypes(include='number').replace([np.inf, -np.inf], np.nan)
    info['resumen_numerico'] = numeric.describe().round(4).to_dict() if len(numeric.columns) else {}
    info['resumen_numerico'] = {k: {m: (None if not np.isfinite(v) else float(v)) for m, v in values.items()} for k, values in info['resumen_numerico'].items()}
    comment = f'El análisis utiliza **{len(df):,} registros de {name}**, con **{int(df.isna().sum().sum()):,} valores ausentes**. '
    fig, ax = plt.subplots(figsize=(8, 4))
    if cfg['kind'] in ('music_content', 'cluster_music'):
        corr = df[MUSIC_FEATURES].corr()
        pairs = [(abs(corr.loc[a,b]), a, b, corr.loc[a,b]) for i,a in enumerate(corr.columns) for b in corr.columns[i+1:] if np.isfinite(corr.loc[a,b])]
        strength, a, b, value = max(pairs)
        category = 'alta' if strength >= .7 else 'moderada' if strength >= .3 else 'baja'
        info['correlacion_destacada'] = {'variables': [a,b], 'pearson': float(value), 'categoria_descriptiva': category, 'umbrales': {'moderada': .3, 'alta': .7}}
        comment += f'La mayor correlación absoluta es {a} / {b}: **r={value:.3f}**, asociación {category} según los umbrales descriptivos del proyecto. No demuestra causalidad ni significancia estadística.'
        image = ax.imshow(corr, vmin=-1, vmax=1, cmap='coolwarm')
        ax.set_xticks(range(len(corr)), corr.columns, rotation=90)
        ax.set_yticks(range(len(corr)), corr.columns)
        fig.colorbar(image, ax=ax)
    elif 'label' in df and cfg['kind'] != 'anomaly':
        counts = df.label.value_counts().sort_index()
        info['balance'] = {str(k):int(v) for k,v in counts.items()}
        largest = counts.max()/len(df)
        comment += f'La clase mayoritaria representa **{largest:.2%}** de esta partición. Las métricas finales deben acompañarse de resultados por clase.'
        counts.plot.bar(ax=ax)
    elif 'value' in df:
        ax.plot(df.timestamp, df.value)
        ax.set_ylabel('Valor de la serie')
        comment += 'Los cortes y rezagos deben respetar el orden temporal.'
    elif 'labels' in df:
        from collections import Counter
        counts = Counter(label for row in df.labels for label in row)
        info['etiquetas'] = dict(counts)
        labels = sorted(counts, key=counts.get, reverse=True)[:12]
        ax.barh(labels[::-1], [counts[l] for l in labels[::-1]])
        comment += 'Una película puede tener varias categorías; las frecuencias no suman el número de películas.'
    elif 'monetary' in df:
        ax.hist(np.log1p(df.monetary), bins=30)
        ax.set_xlabel('log(1 + importe de compras)')
        comment += 'RFM describe compras positivas observadas y no beneficios ni ingresos netos de devoluciones.'
    elif 'rating' in df:
        df.rating.value_counts().sort_index().plot.bar(ax=ax)
        comment += 'La muestra de usuarios limita el alcance. Las valoraciones posteriores no participan en el ajuste.'
    else:
        df.type.value_counts().plot.bar(ax=ax)
        comment += 'Las categorías son metadatos del catálogo; no hay evidencia de preferencias personales.'
    ax.set_title(cfg['title'])
    fig.tight_layout()
    fig.savefig(report_path(project, 'eda', 'eda.png'), dpi=130)
    plt.close(fig)
    return report(project, 'eda', info, comment)
