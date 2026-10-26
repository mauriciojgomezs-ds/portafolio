"""Pronóstico semanal a un paso y detección causal de anomalías."""
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, precision_score, recall_score, f1_score, confusion_matrix

from .common import config, load_frame, save_model, load_model, report, save_frame, report_path


def forecast_features(df):
    data = df.copy()
    for lag in (1,2,3,4):
        data[f'lag_{lag}'] = data.value.shift(lag)
    data['media_4'] = data.value.shift(1).rolling(4).mean()
    week = data.timestamp.dt.isocalendar().week.astype(float)
    data['sin_semana'] = np.sin(2*np.pi*week/52)
    data['cos_semana'] = np.cos(2*np.pi*week/52)
    return data.dropna().reset_index(drop=True)


def forecast_split(project):
    frame = forecast_features(load_frame(project))
    n = len(frame)
    if n < 20:
        raise ValueError('Se necesitan al menos 20 semanas con rezagos disponibles.')
    return {name:part for name,part in [('train',frame.iloc[:int(.6*n)]),('valid',frame.iloc[int(.6*n):int(.8*n)]),('test',frame.iloc[int(.8*n):])]}


def regression_metrics(y,pred):
    return {'casos':len(y),'mae':float(mean_absolute_error(y,pred)),'rmse':float(np.sqrt(mean_squared_error(y,pred)))}


def causal_scores(df,window=48):
    previous = df.value.shift(1)
    center = previous.rolling(window,min_periods=window).mean()
    scale = previous.rolling(window,min_periods=window).std(ddof=0)
    residual = (df.value-center).abs()
    # Escala nula + desviación positiva es una anomalía extrema, no dato faltante.
    score = residual / scale.replace(0,np.nan)
    score = score.mask(scale.eq(0) & residual.eq(0),0.)
    score = score.mask(scale.eq(0) & residual.gt(0),1e12)
    return score


def anomaly_metrics(y,pred):
    return {'casos':len(y),'precision':float(precision_score(y,pred,zero_division=0)),'recall':float(recall_score(y,pred,zero_division=0)),'f1':float(f1_score(y,pred,zero_division=0)),'matriz_confusion':confusion_matrix(y,pred,labels=[0,1]).tolist(),'positivos_reales':int(np.sum(y))}


def anomaly_frame(project):
    # Las etiquetas se usan solo para evaluar; el cálculo causal no las consulta.
    df = load_frame(project).copy()
    df['score'] = causal_scores(df,config(project).get('window',48))
    n = len(df)
    df['particion'] = ['train']*int(.6*n)+['valid']*(int(.8*n)-int(.6*n))+['test']*(n-int(.8*n))
    return df.dropna(subset=['score'])


def baseline(project):
    if config(project)['kind']=='forecast':
        parts = forecast_split(project)
        for name,df in parts.items():
            save_frame(project,df,name)
        result = regression_metrics(parts['valid'].value,parts['valid'].lag_1)
        save_model(project,{'rule':'ultima_semana'},'baseline')
        comment = f'El baseline predice el importe de la semana anterior. MAE en validación: **{result["mae"]:.2f}**. Se evalúa a un paso con la semana anterior observada; no es un pronóstico de varias semanas desde un único origen.'
    else:
        df = anomaly_frame(project)
        valid = df[df.particion.eq('valid')]
        result = anomaly_metrics(valid.label,np.zeros(len(valid),dtype=int))
        save_model(project,{'rule':'sin_alertas'},'baseline')
        comment = f'El baseline no genera alertas. Validación contiene **{result["positivos_reales"]} puntos dentro de ventanas anómalas**. Las métricas se calculan por punto, no con el evaluador oficial NAB.'
    return report(project,'baseline',result,comment)


def train(project):
    cfg = config(project)
    if cfg['kind']=='forecast':
        parts = forecast_split(project)
        columns = [c for c in parts['train'].columns if c not in ('timestamp','value')]
        candidates, models = [], []
        for alpha in (1.,10.,100.):
            model = make_pipeline(StandardScaler(),Ridge(alpha=alpha))
            model.fit(parts['train'][columns],parts['train'].value)
            candidates.append({'alpha':alpha,**regression_metrics(parts['valid'].value,model.predict(parts['valid'][columns]))})
            models.append(model)
        best = min(range(len(candidates)),key=lambda i:candidates[i]['mae'])
        save_model(project,{'model':models[best],'columns':columns})
        result = {'criterio':'mae_validacion','alpha_elegido':candidates[best]['alpha'],'candidatos':candidates}
        comment = f'Se eligió alpha **{result["alpha_elegido"]}** por MAE de validación. Los rezagos y medias móviles se desplazan antes de calcularse; el escalamiento se ajusta solo en train. El histórico es corto para aprender estacionalidad anual.'
    else:
        df = anomaly_frame(project)
        train_df,valid = df[df.particion.eq('train')],df[df.particion.eq('valid')]
        thresholds = [float(train_df.score.quantile(q)) for q in (.95,.975,.99)]
        if not len(valid) or not valid.label.any():
            raise ValueError('Validación no contiene anomalías evaluables: no se puede seleccionar por F1.')
        candidates = [{'quantile_train':q,'threshold':t,**anomaly_metrics(valid.label,valid.score.gt(t).astype(int))} for q,t in zip((.95,.975,.99),thresholds)]
        best = max(candidates,key=lambda c:c['f1'])
        save_model(project,{'threshold':best['threshold'],'window':cfg.get('window',48)})
        result = {'criterio':'f1_validacion_por_punto','threshold_elegido':best['threshold'],'candidatos':candidates}
        comment = f'Se eligió un umbral **{best["threshold"]:.4f}** por F1 de validación. Los candidatos provienen de cuantiles de los scores de train; el detector utiliza solo observaciones anteriores para calcular media y escala. Las ventanas anómalas de test no intervienen en esta elección.'
    return report(project,'modelado',result,comment)


def evaluate(project):
    bundle = load_model(project)
    if config(project)['kind']=='forecast':
        test = forecast_split(project)['test']
        pred = bundle['model'].predict(test[bundle['columns']])
        results = {'baseline':regression_metrics(test.value,test.lag_1),'modelo':regression_metrics(test.value,pred),'periodo_test':[str(test.timestamp.min()),str(test.timestamp.max())]}
        relation = 'mejora' if results['modelo']['mae'] < results['baseline']['mae'] else 'no mejora'
        comment = f'El modelo **{relation}** el MAE del baseline: **{results["modelo"]["mae"]:.2f}** frente a **{results["baseline"]["mae"]:.2f}**, en **{len(test)} semanas de test**. El protocolo es a un paso; incorpora ventas reales previas al avanzar. Mide compras positivas, no ventas netas ni beneficios. Un único bloque corto no permite concluir robustez entre temporadas.'
        output = test[['timestamp','value']].copy()
        output['prediccion_modelo'],output['prediccion_baseline'] = pred,test.lag_1.to_numpy()
    else:
        df = anomaly_frame(project)
        test = df[df.particion.eq('test')].copy()
        pred = test.score.gt(bundle['threshold']).astype(int)
        results = {'baseline':anomaly_metrics(test.label,np.zeros(len(test),dtype=int)),'modelo':anomaly_metrics(test.label,pred),'threshold':bundle['threshold'],'protocolo':'Métricas por punto dentro de ventanas; no puntuación NAB oficial.'}
        comment = f'En test se obtiene **F1 {results["modelo"]["f1"]:.4f}**, precisión **{results["modelo"]["precision"]:.2%}** y recall **{results["modelo"]["recall"]:.2%}**. Hay **{results["modelo"]["positivos_reales"]} puntos etiquetados como anómalos**. '+results['protocolo']+' La ventana móvil avanza con datos observados, sin consultar etiquetas; un evento puede generar múltiples alertas. Si test no tiene anomalías, recall y F1 se representan como cero por convención y no acreditan capacidad de detección.'
        output = test[['timestamp','value','label','score']].copy()
        output['prediccion_modelo'] = pred
    output.to_csv(report_path(project, 'evaluacion', 'predicciones_test.csv'),index=False)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,ax = plt.subplots(figsize=(10,4))
    ax.plot(output.timestamp,output.value,label='Observado',linewidth=1)
    if config(project)['kind']=='forecast':
        ax.plot(output.timestamp,output.prediccion_modelo,label='Modelo',linewidth=1)
        ax.plot(output.timestamp,output.prediccion_baseline,label='Baseline',linewidth=1,alpha=.6)
        ax.set(xlabel='Semana (domingo)',ylabel='Importe de compras positivas')
    else:
        alerts = output[output.prediccion_modelo.eq(1)]
        ax.scatter(alerts.timestamp,alerts.value,s=8,c='red',label='Alertas')
        truth = output[output.label.eq(1)]
        ax.scatter(truth.timestamp,truth.value,s=16,facecolors='none',edgecolors='orange',label='Ventanas etiquetadas')
        ax.set(xlabel='Fecha',ylabel='Temperatura (unidad de la fuente)')
    ax.set_title('Evaluación sobre el bloque de test')
    ax.legend()
    fig.tight_layout()
    fig.savefig(report_path(project, 'evaluacion', 'evaluacion.png'),dpi=130)
    plt.close(fig)
    return report(project,'evaluacion',results,comment)
