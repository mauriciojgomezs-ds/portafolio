"""Efecto promedio de asignación a NSW: muestra experimental Dehejia–Wahba."""
from pathlib import Path
from urllib.request import urlopen
import io
import numpy as np
import pandas as pd
from scipy.stats import t as student_t
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .common import config,report,report_path,write_json,read_json,save_frame,load_frame,sha256

PAGE='https://users.nber.org/~rdehejia/data/.nswdata2.html'
FILES={'treated':'https://www.nber.org/~rdehejia/data/nswre74_treated.txt','control':'https://www.nber.org/~rdehejia/data/nswre74_control.txt'}
COLUMNS=['treatment','age','education','black','hispanic','married','nodegree','re74','re75','re78']
PRE=['age','education','black','hispanic','married','nodegree','re74','re75']

def setup(project):
    path=Path(project)/config(project)['source']
    if not path.exists():
        path.parent.mkdir(parents=True,exist_ok=True);frames=[]
        for arm,url in FILES.items():
            original=path.parent/f'nswre74_{arm}.txt'
            if not original.exists():
                data=urlopen(url,timeout=60).read()
                check=pd.read_csv(io.BytesIO(data),sep=r'\s+',header=None)
                if check.shape[1]!=len(COLUMNS):raise ValueError('Fuente NSW inesperada')
                original.write_bytes(data)
            frames.append(pd.read_csv(original,sep=r'\s+',header=None,names=COLUMNS))
        combined=pd.concat(frames,ignore_index=True);partial=path.with_suffix('.part')
        combined.to_csv(partial,index=False);partial.replace(path)
    return path

def validate(df):
    if list(df.columns)!=COLUMNS or not df.treatment.isin([0,1]).all() or df.treatment.nunique()!=2:raise ValueError('Muestra NSW no válida')
    if not np.isfinite(df.to_numpy()).all():raise ValueError('Valores no finitos en NSW')
    for key in ['treatment','black','hispanic','married','nodegree']:
        if not df[key].isin([0,1]).all():raise ValueError(f'{key} no es binaria')
    if (df[['re74','re75','re78']]<0).any().any():raise ValueError('Ingresos negativos inesperados')

def prepare(project):
    path=setup(project);df=pd.read_csv(path);validate(df);df['source_id']=np.arange(len(df));save_frame(project,df)
    info={'fuente':PAGE,'sha256':sha256(path),'filas':len(df),'asignados_programa':int(df.treatment.sum()),'controles':int(df.treatment.eq(0).sum()),'covariables_pretratamiento':PRE,'resultado':'re78: ingresos anuales de 1978 en USD nominales','muestra':'Submuestra experimental NSW Dehejia–Wahba; no se incluyen controles CPS/PSID','particion_predictiva':'No aplica: estimación causal sobre la muestra experimental completa'}
    return report(project,'preparacion',info,f"Se conservan **{len(df)} participantes**, **{info['asignados_programa']} asignados al programa** y **{info['controles']} controles**, sin deduplicar participantes por atributos. Resultado: ingresos de 1978 en USD nominales. Solo se incluyen covariables previas. Es una submuestra experimental histórica; no se mezclan controles observacionales ni se crean splits predictivos. El estimando es el efecto de **asignación al programa en esta muestra**, no el efecto entre quienes completaron la capacitación.")

def balance(df):
    treated,control=df[df.treatment.eq(1)],df[df.treatment.eq(0)];rows=[]
    for key in PRE:
        denominator=np.sqrt((treated[key].var(ddof=1)+control[key].var(ddof=1))/2)
        difference=treated[key].mean()-control[key].mean()
        rows.append({'variable':key,'media_tratados':treated[key].mean(),'media_control':control[key].mean(),'diferencia_estandarizada':float(difference/denominator) if denominator else 0. if difference==0 else None})
    return pd.DataFrame(rows)

def explore(project):
    df=load_frame(project);b=balance(df);b.to_csv(report_path(project,'eda','balance_pretratamiento.csv'),index=False)
    fig,axes=plt.subplots(1,2,figsize=(10,4));axes[0].barh(b.variable,b.diferencia_estandarizada);axes[0].axvline(.1,color='gray',ls='--');axes[0].axvline(-.1,color='gray',ls='--');axes[0].set_title('Balance previo: diferencia estandarizada');axes[1].hist([df[df.treatment.eq(0)].re78,df[df.treatment.eq(1)].re78],bins=25,label=['Control','Programa'],alpha=.6);axes[1].legend();axes[1].set(xlabel='USD nominales · 1978',title='Ingresos observados');fig.tight_layout();fig.savefig(report_path(project,'eda','eda.png'),dpi=130);plt.close(fig)
    info={'max_diferencia_estandarizada_absoluta':float(b.diferencia_estandarizada.abs().max()),'covariables_sobre_01':int(b.diferencia_estandarizada.abs().gt(.1).sum()),'proporcion_ingresos_cero':float(df.re78.eq(0).mean())}
    return report(project,'eda',info,f"Hay **{info['covariables_sobre_01']} covariables** con diferencia estandarizada absoluta > 0,10, una referencia descriptiva. El **{info['proporcion_ingresos_cero']:.2%}** tiene ingresos cero en 1978. El balance finito puede variar por azar; estas cifras no prueban ni invalidan la asignación aleatoria. No se eligen ajustes según su significancia o el resultado observado.")

def difference(df,confidence=.95,outcome='re78'):
    a,b=df.loc[df.treatment.eq(1),outcome].to_numpy(),df.loc[df.treatment.eq(0),outcome].to_numpy()
    if min(len(a),len(b))<2:raise ValueError('Se necesitan dos participantes por brazo')
    va,vb=a.var(ddof=1)/len(a),b.var(ddof=1)/len(b);variance=va+vb
    dof=variance**2/(va**2/(len(a)-1)+vb**2/(len(b)-1)) if variance else len(a)+len(b)-2
    effect=float(a.mean()-b.mean());se=float(np.sqrt(variance));critical=student_t.ppf((1+confidence)/2,dof)
    return {'efecto_usd':effect,'error_estandar':se,'ci_inferior':float(effect-critical*se),'ci_superior':float(effect+critical*se),'confidence_level':confidence}

def adjusted(df,confidence=.95):
    # Lin: covariables centradas y sus interacciones con asignación; coeficiente T = ATE ajustado.
    cov=df[PRE].to_numpy(dtype=float);mean=cov.mean(axis=0);scale=cov.std(axis=0);scale[scale==0]=1;z=(cov-mean)/scale
    treatment=df.treatment.to_numpy();y=df.re78.to_numpy()
    design=np.column_stack([np.ones(len(df)),treatment,z,treatment[:,None]*z])
    if np.linalg.matrix_rank(design)!=design.shape[1]:raise ValueError('Diseño ajustado sin rango completo')
    inv=np.linalg.inv(design.T@design);coef=np.linalg.lstsq(design,y,rcond=None)[0]
    residual=y-design@coef;leverage=np.einsum('ij,jk,ik->i',design,inv,design)
    if np.any(leverage>=1-1e-10):raise ValueError('Leverage extremo impide HC3')
    meat=design.T@(((residual/(1-leverage))**2)[:,None]*design);covariance=inv@meat@inv
    se=float(np.sqrt(max(0,covariance[1,1])));critical=student_t.ppf((1+confidence)/2,len(df)-design.shape[1]);effect=float(coef[1])
    return {'efecto_usd':effect,'error_estandar_hc3':se,'ci_inferior':float(effect-critical*se),'ci_superior':float(effect+critical*se),'confidence_level':confidence,'parametros':design.shape[1],'covariables':PRE,'metodo':'OLS Lin con interacciones y errores HC3'}

def baseline(project):
    cfg=config(project);result=difference(load_frame(project),cfg['confidence_level']);write_json(Path(project)/'models/difference.json',result)
    return report(project,'baseline',result,f"Diferencia de medias programa − control: **{result['efecto_usd']:,.2f} USD**, IC {result['confidence_level']:.0%} **[{result['ci_inferior']:,.2f}, {result['ci_superior']:,.2f}]** mediante Welch. Es una estimación experimental sin ajuste, no un baseline de clasificación o predicción.")

def train(project):
    cfg=config(project);result=adjusted(load_frame(project),cfg['confidence_level']);write_json(Path(project)/'models/adjusted.json',result)
    return report(project,'modelado',result,f"Ajuste preespecificado por covariables previas e interacciones: **{result['efecto_usd']:,.2f} USD**, IC {result['confidence_level']:.0%} HC3 **[{result['ci_inferior']:,.2f}, {result['ci_superior']:,.2f}]**. El coeficiente de asignación se interpreta respecto a covariables centradas en esta muestra. No se selecciona el estimador por producir un efecto mayor o un intervalo que excluya cero.")

def bootstrap(df,repetitions,seed,confidence):
    rng=np.random.default_rng(seed);a=df[df.treatment.eq(1)];b=df[df.treatment.eq(0)];values=[]
    for _ in range(repetitions):
        sample=pd.concat([a.iloc[rng.integers(len(a),size=len(a))],b.iloc[rng.integers(len(b),size=len(b))]],ignore_index=True)
        try:values.append((difference(sample,confidence)['efecto_usd'],adjusted(sample,confidence)['efecto_usd']))
        except ValueError:continue
    if len(values)<.95*repetitions:raise ValueError('Demasiadas réplicas bootstrap sin rango completo')
    return np.array(values)

def evaluate(project):
    cfg=config(project);df=load_frame(project);raw=read_json(Path(project)/'models/difference.json');model=read_json(Path(project)/'models/adjusted.json');samples=bootstrap(df,cfg['bootstrap_repetitions'],cfg['seed'],cfg['confidence_level'])
    tail=(1-cfg['confidence_level'])/2;ci=np.quantile(samples,[tail,1-tail],axis=0)
    rows=[]
    for index,(name,result) in enumerate([('Diferencia experimental',raw),('Ajuste Lin · HC3',model)]):rows.append({'estimador':name,**{k:v for k,v in result.items() if isinstance(v,(float,int))},'bootstrap_inferior':float(ci[0,index]),'bootstrap_superior':float(ci[1,index])})
    pd.DataFrame(rows).to_csv(report_path(project,'evaluacion','estimaciones.csv'),index=False)
    pd.DataFrame(samples,columns=['diferencia_medias','lin_ajustado']).to_csv(report_path(project,'evaluacion','bootstrap.csv'),index=False)
    fig,ax=plt.subplots(figsize=(9,4));ax.hist(samples[:,0],bins=35,alpha=.5,label='Diferencia');ax.hist(samples[:,1],bins=35,alpha=.5,label='Lin');ax.axvline(0,color='black');ax.set(xlabel='Efecto de asignación · USD nominales',title='Bootstrap estratificado por brazo');ax.legend();fig.tight_layout();fig.savefig(report_path(project,'evaluacion','evaluacion.png'),dpi=130);plt.close(fig)
    info={'sin_ajuste':raw,'ajustado':model,'bootstrap_replicas_validas':len(samples),'bootstrap_replicas_solicitadas':cfg['bootstrap_repetitions'],'bootstrap_ci_sin_ajuste':ci[:,0].tolist(),'bootstrap_ci_ajustado':ci[:,1].tolist(),'estimando':'Efecto de asignación al programa en la muestra experimental seleccionada'}
    evidence='excluye cero por el lado positivo' if model['ci_inferior']>0 else 'excluye cero por el lado negativo' if model['ci_superior']<0 else 'incluye cero'
    return report(project,'evaluacion',info,f"El IC ajustado HC3 **{evidence}**. Se contrastan ambas estimaciones con **{len(samples)} réplicas bootstrap**, muestreando participantes dentro de cada brazo y recalculando el centrado. Diferencias entre métodos reflejan ajuste y aproximaciones de incertidumbre; no se comparan mediante accuracy ni se conoce un efecto verdadero con el que medir error. Interpretación causal condicionada a la asignación experimental, consistencia, ausencia de interferencia y selección de la submuestra. No se generaliza a todos los trabajadores, programas actuales ni efectos por cumplimiento.")

def run_stage(project,stage):return {'preparacion':prepare,'eda':explore,'baseline':baseline,'modelado':train,'evaluacion':evaluate}[stage](project)
