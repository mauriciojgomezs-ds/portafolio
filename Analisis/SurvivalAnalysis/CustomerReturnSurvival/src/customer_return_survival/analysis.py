"""Tiempo hasta segunda ocasión de compra, censurado a 90 días o cierre del registro."""
from pathlib import Path
from urllib.request import urlopen
import io,zipfile,shutil
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from lifelines import KaplanMeierFitter,CoxPHFitter
from lifelines.utils import concordance_index
from lifelines.statistics import proportional_hazard_test
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .common import config,report,report_path,save_frame,load_frame,save_model,load_model,sha256

URL='https://archive.ics.uci.edu/static/public/352/online+retail.zip'
FEATURES=['log_basket_gbp','log_items','uk']
def setup(project):
    path=Path(project)/config(project)['source']
    if not path.exists():
        path.parent.mkdir(parents=True,exist_ok=True);temp=path.with_suffix('.part')
        try:
            with urlopen(URL,timeout=60) as src,temp.open('wb') as dst:shutil.copyfileobj(src,dst)
            with zipfile.ZipFile(temp) as z:
                if z.testzip() is not None or not any(n.endswith('.xlsx') for n in z.namelist()):raise ValueError('ZIP inesperado')
            temp.replace(path)
        finally:
            if temp.exists():temp.unlink()
    return path

def build_cohort(raw,horizon):
    if horizon<=0:raise ValueError('Horizonte positivo requerido')
    df=raw.copy();df.InvoiceDate=pd.to_datetime(df.InvoiceDate,errors='raise');end=df.InvoiceDate.max()
    df=df[df.CustomerID.notna() & df.Quantity.gt(0) & df.UnitPrice.gt(0) & ~df.InvoiceNo.astype(str).str.upper().str.startswith('C')].copy()
    df['amount']=df.Quantity*df.UnitPrice
    if not np.isfinite(df.amount).all():raise ValueError('Importes no finitos')
    # Same timestamp is one purchasing occasion, even if there are multiple invoices.
    occasions=df.groupby(['CustomerID','InvoiceDate']).agg(basket_gbp=('amount','sum'),items=('StockCode','nunique'),country=('Country','first')).reset_index().sort_values(['CustomerID','InvoiceDate'])
    occasions['order']=occasions.groupby('CustomerID').cumcount()
    first=occasions[occasions.order.eq(0)].copy();second=occasions[occasions.order.eq(1)][['CustomerID','InvoiceDate']].rename(columns={'InvoiceDate':'second_date'})
    cohort=first.merge(second,on='CustomerID',how='left',validate='one_to_one')
    followup=(end-cohort.InvoiceDate).dt.total_seconds()/86400;next_time=(cohort.second_date-cohort.InvoiceDate).dt.total_seconds()/86400
    available=np.minimum(horizon,followup);event=next_time.notna() & next_time.le(available)
    cohort['event']=event.astype(int);cohort['duration_days']=np.where(event,next_time,available)
    zero=int(cohort.duration_days.le(0).sum());cohort=cohort[cohort.duration_days.gt(0)].copy()
    cohort['log_basket_gbp']=np.log1p(cohort.basket_gbp);cohort['log_items']=np.log1p(cohort['items']);cohort['uk']=cohort.country.eq('United Kingdom').astype(int)
    cohort['first_date']=cohort.InvoiceDate;cohort['customer_id']=cohort.CustomerID.astype(str)
    if cohort.customer_id.duplicated().any() or not np.isfinite(cohort[FEATURES+['duration_days']]).all().all():raise ValueError('Cohorte no válida')
    return cohort[['customer_id','first_date',*FEATURES,'duration_days','event']],{'cierre_observacion':end.isoformat(),'filas_originales':len(raw),'filas_compras_positivas_identificadas':len(df),'ocasiones_compra':len(occasions),'clientes_sin_seguimiento_excluidos':zero}

def prepare(project):
    cfg=config(project);path=setup(project)
    with zipfile.ZipFile(path) as z:
        member=next(n for n in z.namelist() if n.endswith('.xlsx'));raw=pd.read_excel(io.BytesIO(z.read(member)),engine='openpyxl')
    cohort,info=build_cohort(raw,cfg['horizon_days']);train,test=train_test_split(cohort,test_size=.2,stratify=cohort.event,random_state=cfg['seed']);train,valid=train_test_split(train,test_size=.25,stratify=train.event,random_state=cfg['seed'])
    for name,frame in [('train',train),('valid',valid),('test',test)]:save_frame(project,frame,name)
    info.update(fuente_sha256=sha256(path),clientes=len(cohort),eventos=int(cohort.event.sum()),censurados=int(cohort.event.eq(0).sum()),horizonte_dias=cfg['horizon_days'],features=FEATURES,particiones={name:len(frame) for name,frame in [('train',train),('valid',valid),('test',test)]})
    return report(project,'preparacion',info,f"Se construye una cohorte de **{len(cohort)} clientes**: **{info['eventos']} segundas ocasiones de compra** y **{info['censurados']} casos censurados**. Seguimiento hasta {cfg['horizon_days']} días o cierre del registro. Compras al mismo instante se agrupan; se excluyen {info['clientes_sin_seguimiento_excluidos']} casos sin seguimiento positivo. Features derivadas exclusivamente de la primera ocasión observada. Particiones por cliente 60/20/20, aleatorias y estratificadas por evento; no constituyen una validación temporal.")

def explore(project):
    df=load_frame(project,'train');km=KaplanMeierFitter().fit(df.duration_days,df.event)
    info={'clientes_train':len(df),'eventos_train':int(df.event.sum()),'censura_train':float(df.event.eq(0).mean()),'sin_segunda_compra_a_30_dias_km':float(km.predict(30))}
    fig,axes=plt.subplots(1,2,figsize=(10,4));km.plot_survival_function(ax=axes[0]);axes[0].set(title='Kaplan–Meier · train',xlabel='Días',ylabel='P(sin segunda compra)');axes[1].hist(df.duration_days,bins=30);axes[1].set(title='Duración observada · train',xlabel='Días');fig.tight_layout();fig.savefig(report_path(project,'eda','eda.png'),dpi=130);plt.close(fig)
    km.event_table.to_csv(report_path(project,'eda','tabla_riesgo.csv'))
    return report(project,'eda',info,f"Train tiene **{info['censura_train']:.2%} de censura**. Kaplan–Meier estima **{info['sin_segunda_compra_a_30_dias_km']:.2%} sin segunda compra a 30 días**, bajo censura no informativa. La duración de un caso censurado no es su tiempo real de retorno. Primera compra observada puede corresponder a un cliente ya existente.")

def baseline(project):
    df=load_frame(project,'train');km=KaplanMeierFitter().fit(df.duration_days,df.event);save_model(project,km,'baseline')
    info={'c_index_referencia':.5,'sin_segunda_compra_30_dias':float(km.predict(30)),'tipo':'Curva común Kaplan–Meier ajustada en train; ranking de riesgo constante'}
    return report(project,'baseline',info,'Referencia: Kaplan–Meier común ajustada exclusivamente en train. No diferencia clientes; para pares comparables, un ranking constante tiene C-index 0,5. La curva incorpora los casos censurados.')

def concordance(frame,risk):return float(concordance_index(frame.duration_days,-np.asarray(risk),frame.event))

def train(project):
    cfg=config(project);tr,v=[load_frame(project,n) for n in ['train','valid']];candidates=[];models=[]
    for penalty in cfg['cox_penalties']:
        model=CoxPHFitter(penalizer=penalty).fit(tr[FEATURES+['duration_days','event']],duration_col='duration_days',event_col='event')
        candidates.append({'penalizacion':penalty,'c_index_validacion':concordance(v,model.predict_partial_hazard(v[FEATURES]))});models.append(model)
    chosen=max(range(len(models)),key=lambda i:candidates[i]['c_index_validacion']);model=models[chosen];save_model(project,model)
    # Diagnostics only in train, explicitly exploratory (unadjusted p values).
    diagnostic=proportional_hazard_test(model,tr[FEATURES+['duration_days','event']],time_transform='rank').summary;diagnostic.to_csv(report_path(project,'modelado','diagnostico_riesgos_proporcionales.csv'))
    model.summary.to_csv(report_path(project,'modelado','coeficientes_cox.csv'))
    ph_violations=int(diagnostic.p.lt(.05).sum())
    info={'candidatos':candidates,'penalizacion_elegida':candidates[chosen]['penalizacion'],'c_index_validacion':candidates[chosen]['c_index_validacion'],'variables_ph_p_menor_005':ph_violations,'criterio':'C-index de validación; sin reentrenar con validación ni usar test'}
    ph_comment=("sin evidencia exploratoria de violación del supuesto de riesgos proporcionales (no certifica el supuesto por falta de ajuste de multiplicidad)" if ph_violations==0 else f"puede señalar limitaciones del supuesto de riesgos proporcionales en {ph_violations} variable(s)")
    return report(project,'modelado',info,f"Cox penalizado elegido por C-index en validación: **{info['c_index_validacion']:.3f}**, penalización **{info['penalizacion_elegida']}**. Diagnóstico exploratorio en train: **{info['variables_ph_p_menor_005']} variables con p < 0,05**, sin ajuste por multiplicidad; {ph_comment}. Los coeficientes describen asociaciones y no efectos causales.")

def bootstrap_concordance(frame,risk,seed,repetitions):
    rng=np.random.default_rng(seed);values=[]
    for _ in range(repetitions):
        ix=rng.integers(0,len(frame),size=len(frame))
        try:values.append(concordance(frame.iloc[ix],np.asarray(risk)[ix]))
        except ZeroDivisionError:pass
    if len(values)<.95*repetitions:raise ValueError('Demasiadas réplicas sin pares comparables')
    return values

def evaluate(project):
    cfg=config(project);test=load_frame(project,'test');model=load_model(project);risk=model.predict_partial_hazard(test[FEATURES]).to_numpy();score=concordance(test,risk);boot=bootstrap_concordance(test,risk,cfg['seed'],cfg['bootstrap_repetitions']);low,high=np.quantile(boot,[.025,.975]);km=load_model(project,'baseline')
    info={'clientes_test':len(test),'eventos_test':int(test.event.sum()),'baseline_c_index':.5,'modelo_c_index':score,'ci_bootstrap95_inferior':float(low),'ci_bootstrap95_superior':float(high),'replicas_validas':len(boot),'diagnostico':'Discriminación con censura; no mide calibración ni retorno comercial'}
    pd.DataFrame({'replica':np.arange(len(boot)),'c_index':boot}).to_csv(report_path(project,'evaluacion','bootstrap_concordancia.csv'),index=False)
    times=np.arange(0,cfg['horizon_days']+1);observed=KaplanMeierFitter().fit(test.duration_days,test.event);mean_curve=model.predict_survival_function(test[FEATURES],times=times).mean(axis=1)
    pd.DataFrame({'dias':times,'km_train':km.predict(times).to_numpy(),'promedio_cox_test':mean_curve.to_numpy(),'km_test_descriptivo':observed.predict(times).to_numpy()}).to_csv(report_path(project,'evaluacion','curvas_agregadas.csv'),index=False)
    fig,axes=plt.subplots(1,2,figsize=(11,4));axes[0].plot(times,km.predict(times),label='KM train');axes[0].plot(times,mean_curve,label='Cox promedio test');axes[0].plot(times,observed.predict(times),label='KM test descriptivo');axes[0].set(xlabel='Días',ylabel='P(sin segunda compra)',title='Curvas agregadas; no prueba de calibración');axes[0].legend();axes[1].hist(boot,bins=25);axes[1].axvline(.5,color='black',ls='--');axes[1].set(title='Bootstrap test · modelo fijo',xlabel='C-index');fig.tight_layout();fig.savefig(report_path(project,'evaluacion','evaluacion.png'),dpi=130);plt.close(fig)
    relation='supera' if score>.5 else 'no supera'
    return report(project,'evaluacion',info,f"C-index de test **{score:.3f}**, IC bootstrap 95 % **[{low:.3f}, {high:.3f}]**: {relation} la referencia de ranking constante 0,5. Se usan **{len(test)} clientes** y **{int(test.event.sum())} eventos**. Bootstrap con modelo fijo; no incluye incertidumbre del ajuste o selección. Las curvas agregadas son un diagnóstico visual, no una prueba de calibración. El protocolo no acredita desempeño futuro, causalidad ni pérdida de clientes. La censura administrativa puede relacionarse con estacionalidad y fecha de entrada.")

def run_stage(project,stage):return {'preparacion':prepare,'eda':explore,'baseline':baseline,'modelado':train,'evaluacion':evaluate}[stage](project)
