"""Pronóstico de llamadas de Kaggle y escenarios de dotación con Erlang C."""
from pathlib import Path
from urllib.request import Request,urlopen
import shutil
import zipfile
import io
import math
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error,mean_squared_error
from threadpoolctl import threadpool_limits
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from .common import config,report,report_path,save_frame,load_frame,save_model,load_model,sha256

URL='https://www.kaggle.com/api/v1/datasets/download/akash1vishwakarma/call-center-dataset'
PAGE='https://www.kaggle.com/datasets/akash1vishwakarma/call-center-dataset'

def setup(project):
    path=Path(project)/config(project)['source']
    if not path.exists():
        path.parent.mkdir(parents=True,exist_ok=True);partial=path.with_suffix('.part')
        try:
            with urlopen(Request(URL,headers={'User-Agent':'portfolio-callcenter'}),timeout=60) as src,partial.open('wb') as dst:shutil.copyfileobj(src,dst)
            with zipfile.ZipFile(partial) as z:
                if z.testzip() is not None:raise ValueError('ZIP corrupto')
                if '01 Call-Center-Dataset.xlsx' not in z.namelist():raise ValueError('Fuente Kaggle distinta de la esperada')
            partial.replace(path)
        finally:
            if partial.exists():partial.unlink()
    return path

def seconds(value):
    if pd.isna(value):return np.nan
    if hasattr(value,'hour'):return value.hour*3600+value.minute*60+value.second
    return pd.to_timedelta(str(value)).total_seconds()

def prepare(project):
    cfg=config(project);path=setup(project)
    with zipfile.ZipFile(path) as z:calls=pd.read_excel(io.BytesIO(z.read('01 Call-Center-Dataset.xlsx')),engine='openpyxl')
    if calls['Call Id'].duplicated().any():raise ValueError('Call Id repetido; revisar antes de contar llamadas')
    calls['timestamp']=pd.to_datetime(calls.Date)+pd.to_timedelta(calls.Time.map(seconds),unit='s')
    calls['talk_seconds']=calls.AvgTalkDuration.map(seconds)
    if calls.timestamp.isna().any() or not calls['Answered (Y/N)'].isin(['Y','N']).all():raise ValueError('Fechas o atención no válidas')
    start,end=calls.timestamp.min().normalize(),calls.timestamp.max().normalize()
    dates=pd.date_range(start,end,freq='D');indices=[]
    for day in dates:indices.extend(pd.date_range(day+pd.Timedelta(hours=cfg['open_hour']),day+pd.Timedelta(hours=cfg['close_hour']),freq=f"{cfg['interval_minutes']}min",inclusive='left'))
    index=pd.DatetimeIndex(indices)
    calls['interval']=calls.timestamp.dt.floor(f"{cfg['interval_minutes']}min")
    if not calls['interval'].isin(index).all():raise ValueError('Hay llamadas fuera del horario configurado')
    counts=calls.groupby('interval').size().reindex(index,fill_value=0)
    frame=pd.DataFrame({'timestamp':index,'value':counts.to_numpy()})
    n=len(dates);cuts=[dates[int(.6*n)],dates[int(.8*n)]]
    train_calls=calls[calls.timestamp<cuts[0]].copy()
    answered=train_calls[train_calls['Answered (Y/N)'].eq('Y')]
    talk=answered.talk_seconds.dropna()
    if not len(talk) or (talk<=0).any():raise ValueError('Duraciones atendidas no válidas para estimar AHT')
    estimated_aht=float(talk.mean()+cfg['wrapup_assumed_seconds'])
    save_model(project,{'aht_seconds':estimated_aht,'talk_train_mean':float(talk.mean()),'wrapup_assumed_seconds':cfg['wrapup_assumed_seconds']},'handling')
    for name,part in [('train',frame[frame.timestamp<cuts[0]]),('valid',frame[(frame.timestamp>=cuts[0])&(frame.timestamp<cuts[1])]),('test',frame[frame.timestamp>=cuts[1]])]:save_frame(project,part,name)
    save_frame(project,frame);save_frame(project,calls[['timestamp','talk_seconds','Answered (Y/N)']].rename(columns={'Answered (Y/N)':'answered'}),'calls')
    info={'fuente':PAGE,'sha256':sha256(path),'llamadas':len(calls),'intervalos':len(frame),'intervalo_minutos':cfg['interval_minutes'],'horario_asumido':f"{cfg['open_hour']:02d}:00–{cfg['close_hour']:02d}:00 todos los días",'fecha_min':str(start.date()),'fecha_max':str(end.date()),'aht_estimado_solo_train_segundos':estimated_aht,'wrapup_asumido_segundos':cfg['wrapup_assumed_seconds'],'origen_operativo_no_acreditado':True,'particiones':{name:{'filas':len(load_frame(project,name))} for name in ('train','valid','test')}}
    return report(project,'preparacion',info,f"Se agregan **{len(calls):,} registros de Kaggle** en **{len(frame):,} intervalos de {cfg['interval_minutes']} minutos**. Se incluyen llamadas no atendidas y ceros en el horario operativo configurado, cuya cobertura se asume completa. Split cronológico por días 60/20/20. AHT estimado exclusivamente en train: **{estimated_aht:.1f} segundos**, conversación atendida más **{cfg['wrapup_assumed_seconds']} segundos supuestos de trabajo posterior**. La fuente no acredita cobertura de una operación real completa; no se generan llamadas sintéticas adicionales.")

def calendar(frame):
    t=pd.to_datetime(frame.timestamp)
    return np.column_stack([t.dt.dayofweek.to_numpy(),t.dt.hour.to_numpy(),t.dt.minute.to_numpy(),np.sin(2*np.pi*t.dt.dayofweek/7),np.cos(2*np.pi*t.dt.dayofweek/7),np.sin(2*np.pi*(t.dt.hour+t.dt.minute/60)/24),np.cos(2*np.pi*(t.dt.hour+t.dt.minute/60)/24)])

def regression(y,pred):return {'casos':len(y),'mae':float(mean_absolute_error(y,pred)),'rmse':float(np.sqrt(mean_squared_error(y,pred)))}

def explore(project):
    df=load_frame(project,'train');fig,axes=plt.subplots(1,2,figsize=(10,4));daily=df.groupby(df.timestamp.dt.date).value.sum();daily.plot(ax=axes[0]);df.groupby(df.timestamp.dt.hour).value.mean().plot.bar(ax=axes[1]);axes[0].set(title='Llamadas diarias · train',ylabel='Llamadas');axes[1].set(title='Media por hora · train',ylabel='Llamadas/intervalo');fig.tight_layout();fig.savefig(report_path(project,'eda','eda.png'),dpi=130);plt.close(fig)
    info={'intervalos_train':len(df),'media_llamadas_intervalo':float(df.value.mean()),'proporcion_intervalos_cero':float(df.value.eq(0).mean())}
    return report(project,'eda',info,f"Train tiene **{len(df)} intervalos**, con una media de **{info['media_llamadas_intervalo']:.2f} llamadas**. El **{info['proporcion_intervalos_cero']:.2%}** está vacío. La baja carga observada y los ceros dependen de asumir que el archivo cubre todas las llamadas y días del horario definido.")

def profile_predict(bundle,frame):
    return np.array([bundle['profile'].get((t.dayofweek,t.hour,t.minute),bundle['mean']) for t in frame.timestamp])

def baseline(project):
    tr,v=load_frame(project,'train'),load_frame(project,'valid');temp=tr.assign(weekday=tr.timestamp.dt.dayofweek,hour=tr.timestamp.dt.hour,minute=tr.timestamp.dt.minute)
    bundle={'profile':temp.groupby(['weekday','hour','minute']).value.mean().to_dict(),'mean':float(tr.value.mean())};save_model(project,bundle,'baseline');result=regression(v.value,profile_predict(bundle,v))
    return report(project,'baseline',result,f"Baseline de media histórica por día de semana y franja, calculada solo en train. MAE de validación **{result['mae']:.3f} llamadas/intervalo**. No incorpora observaciones reales de validación o test al avanzar.")

def train(project):
    tr,v=load_frame(project,'train'),load_frame(project,'valid');candidates=[];models=[]
    with threadpool_limits(limits=2):
        for leaf in [10,30]:
            model=HistGradientBoostingRegressor(loss='poisson',max_leaf_nodes=leaf,max_iter=120,early_stopping=False,random_state=42);model.fit(calendar(tr),tr.value)
            result=regression(v.value,np.maximum(0,model.predict(calendar(v))));candidates.append({'max_leaf_nodes':leaf,**result});models.append(model)
    best=min(range(len(models)),key=lambda i:candidates[i]['mae']);save_model(project,models[best]);result={'criterio':'mae_validacion','max_leaf_nodes_elegido':candidates[best]['max_leaf_nodes'],'candidatos':candidates,'atributos':'Solo calendario conocido a futuro; sin AHT ni respuestas futuras'}
    return report(project,'modelado',result,f"Se elige HistGradientBoosting con **{result['max_leaf_nodes_elegido']} hojas** por MAE de validación. La pérdida Poisson modela conteos; los atributos son solo calendario. Test se pronostica desde el mismo origen fijo posterior a train, sin actualizar modelos ni usar duraciones o volúmenes reales futuros.")

def service_level(calls,aht,agents,interval_seconds,wait_seconds):
    if calls<0 or aht<=0 or interval_seconds<=0 or wait_seconds<0 or agents<0:raise ValueError('Parámetros Erlang C fuera de rango')
    if calls==0:return 1.0
    traffic=calls*aht/interval_seconds
    if agents<=traffic:return 0.0
    blocking=1.0
    for n in range(1,agents+1):blocking=traffic*blocking/(n+traffic*blocking)
    rho=traffic/agents;delay=blocking/(1-rho+rho*blocking)
    return 1-delay*math.exp(-(agents-traffic)*wait_seconds/aht)

def staffing(calls,aht,cfg):
    if not 0<cfg['max_occupancy']<1 or not 0<=cfg['shrinkage']<1 or not 0<cfg['target_service_level']<1:raise ValueError('Ocupación, shrinkage o SLA fuera de rango')
    if calls<0:raise ValueError('Llamadas negativas')
    if calls==0:return 0,0
    traffic=calls*aht/(cfg['interval_minutes']*60)
    agents=max(1,math.ceil(traffic/cfg['max_occupancy']))
    while service_level(calls,aht,agents,cfg['interval_minutes']*60,cfg['target_wait_seconds'])<cfg['target_service_level']:
        agents+=1
        if agents>10000:raise ValueError('Carga excesiva para el cálculo')
    return agents,math.ceil(agents/(1-cfg['shrinkage']))

def evaluate(project):
    cfg=config(project);test=load_frame(project,'test');aht=load_model(project,'handling')['aht_seconds']
    with threadpool_limits(limits=2):pred=np.maximum(0,load_model(project).predict(calendar(test)))
    base=profile_predict(load_model(project,'baseline'),test);result={'baseline':regression(test.value,base),'modelo':regression(test.value,pred),'aht_estimado_train_segundos':aht,'target_service_level':cfg['target_service_level'],'target_wait_seconds':cfg['target_wait_seconds'],'max_occupancy':cfg['max_occupancy'],'shrinkage':cfg['shrinkage']}
    rows=[]
    for timestamp,actual,forecast in zip(test.timestamp,test.value,pred):
        net,gross=staffing(float(forecast),aht,cfg);actual_net,_=staffing(float(actual),aht,cfg);_,stress=staffing(float(forecast)*1.2,aht,cfg)
        rows.append({'timestamp':timestamp,'llamadas_observadas':int(actual),'llamadas_pronosticadas':float(forecast),'agentes_netos':net,'agentes_programables':gross,'agentes_requeridos_segun_observado':actual_net,'agentes_programables_mas20pct':stress,'sl_teorico_segun_observado':service_level(float(actual),aht,net,cfg['interval_minutes']*60,cfg['target_wait_seconds'])})
    out=pd.DataFrame(rows);out.to_csv(report_path(project,'evaluacion','dotacion_intervalos.csv'),index=False)
    result.update(agentes_programables_maximo=int(out.agentes_programables.max()),proporcion_intervalos_sl_teorico_bajo_objetivo=float(out.sl_teorico_segun_observado.lt(cfg['target_service_level']).mean()),escenario_mas20pct_maximo=int(out.agentes_programables_mas20pct.max()))
    # Cortar las líneas fuera del horario: no interpolar volumen o dotación durante cierres.
    full=pd.date_range(test.timestamp.min(),test.timestamp.max(),freq=f"{cfg['interval_minutes']}min")
    plot=out.set_index('timestamp').reindex(full)
    fig,axes=plt.subplots(2,1,figsize=(11,7),sharex=True)
    axes[0].plot(plot.index,plot.llamadas_observadas,label='Observado',alpha=.5)
    axes[0].plot(plot.index,plot.llamadas_pronosticadas,label='Pronóstico')
    axes[0].legend();axes[0].set_ylabel('Llamadas/intervalo')
    axes[1].step(plot.index,plot.agentes_programables,label='Base',where='post')
    axes[1].step(plot.index,plot.agentes_programables_mas20pct,label='+20 % volumen',where='post')
    axes[1].legend();axes[1].set_ylabel('Agentes programables')
    axes[1].xaxis.set_major_locator(mdates.DayLocator(interval=3))
    axes[1].xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
    fig.tight_layout();fig.savefig(report_path(project,'evaluacion','evaluacion.png'),dpi=130);plt.close(fig)
    relation='mejora' if result['modelo']['mae']<result['baseline']['mae'] else 'no mejora'
    return report(project,'evaluacion',result,f"En **{len(test)} intervalos de test**, MAE **{result['modelo']['mae']:.3f}**, frente a **{result['baseline']['mae']:.3f}** del baseline: el modelo **{relation}** ese error. Erlang C estima hasta **{result['agentes_programables_maximo']} agentes programables por intervalo**, y **{result['escenario_mas20pct_maximo']}** bajo +20 % de volumen. El **{result['proporcion_intervalos_sl_teorico_bajo_objetivo']:.2%}** de intervalos queda bajo el objetivo teórico al sustituir el volumen por el observado. Eso es un diagnóstico del modelo de colas, **no un SLA medido**. AHT fijo, horario y shrinkage son supuestos; no se optimizan turnos, descansos ni rutas por habilidad. Erlang C no incluye abandono, aunque el archivo contiene llamadas no atendidas.")

def run_stage(project,stage):return {'preparacion':prepare,'eda':explore,'baseline':baseline,'modelado':train,'evaluacion':evaluate}[stage](project)
