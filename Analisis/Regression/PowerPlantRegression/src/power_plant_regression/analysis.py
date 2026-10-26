"""Regresión tabular y calibración conformal separada de la selección del modelo."""
from pathlib import Path
from urllib.request import urlopen
import io,zipfile,shutil,math
import numpy as np
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error,mean_squared_error,r2_score
from threadpoolctl import threadpool_limits
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .common import config,report,report_path,save_frame,load_frame,save_model,load_model,sha256

URL='https://archive.ics.uci.edu/static/public/294/combined+cycle+power+plant.zip'
FEATURES=['AT','V','AP','RH'];TARGET='PE'

def setup(project):
    path=Path(project)/config(project)['source']
    if not path.exists():
        path.parent.mkdir(parents=True,exist_ok=True);partial=path.with_suffix('.part')
        try:
            with urlopen(URL,timeout=60) as src,partial.open('wb') as dst:shutil.copyfileobj(src,dst)
            with zipfile.ZipFile(partial) as z:
                if z.testzip() is not None or not any(n.endswith('Folds5x2_pp.xlsx') for n in z.namelist()):raise ValueError('ZIP UCI inesperado')
            partial.replace(path)
        finally:
            if partial.exists():partial.unlink()
    return path

def grouped_split(df,seed):
    groups=pd.util.hash_pandas_object(df[FEATURES],index=False).to_numpy()
    train,hold=next(GroupShuffleSplit(n_splits=1,test_size=.4,random_state=seed).split(df,groups=groups))
    selection,test=next(GroupShuffleSplit(n_splits=1,test_size=.5,random_state=seed+1).split(df.iloc[hold],groups=groups[hold]))
    valid,cal=next(GroupShuffleSplit(n_splits=1,test_size=.5,random_state=seed+2).split(df.iloc[hold[selection]],groups=groups[hold[selection]]))
    return {'train':train,'valid':hold[selection[valid]],'calibration':hold[selection[cal]],'test':hold[test]}

def prepare(project):
    cfg=config(project);path=setup(project)
    with zipfile.ZipFile(path) as z:
        member=next(n for n in z.namelist() if n.endswith('Folds5x2_pp.xlsx'));book=pd.ExcelFile(io.BytesIO(z.read(member)),engine='openpyxl');sheet=book.sheet_names[0];df=pd.read_excel(book,sheet_name=sheet)
    if not set(FEATURES+[TARGET]).issubset(df.columns) or not np.isfinite(df[FEATURES+[TARGET]].to_numpy()).all():raise ValueError('Variables de potencia no válidas')
    initial=len(df);df=df[FEATURES+[TARGET]].drop_duplicates().reset_index(drop=True);df['source_id']=np.arange(len(df));parts=grouped_split(df,cfg['seed']);info={'fuente':'https://archive.ics.uci.edu/dataset/294/combined+cycle+power+plant','sha256':sha256(path),'hoja_utilizada':sheet,'hojas_disponibles':book.sheet_names,'filas_hoja':initial,'duplicados_exactos_retirados':initial-len(df),'features':FEATURES,'objetivo_unidad':'Potencia eléctrica PE en MW','particiones':{}}
    for name,idx in parts.items():save_frame(project,df.iloc[idx],name);info['particiones'][name]={'filas':len(idx)}
    return report(project,'preparacion',info,f"Se utiliza **solo la primera hoja ({sheet})**: las otras hojas son reordenamientos del mismo conjunto, no observaciones independientes. Se retiran **{initial-len(df)} duplicados exactos** y se agrupan condiciones idénticas de entrada para que no crucen particiones. Separación aproximada por grupos: **60 % train, 10 % validación, 10 % calibración y 20 % test**. Objetivo: potencia eléctrica en **MW**. No se dispone de fecha para validar un pronóstico temporal.")

def x(df):return df[FEATURES].to_numpy()
def metrics(y,pred):return {'casos':len(y),'mae_mw':float(mean_absolute_error(y,pred)),'rmse_mw':float(np.sqrt(mean_squared_error(y,pred))),'r2':float(r2_score(y,pred))}

def variance_inflation_factors(df,features):
    """VIF por regresión OLS de cada feature contra las demás (sin statsmodels)."""
    from sklearn.linear_model import LinearRegression
    out={}
    for target in features:
        others=[c for c in features if c!=target]
        r2=LinearRegression().fit(df[others],df[target]).score(df[others],df[target])
        out[target]=1e6 if r2>=1 else 1/(1-r2)
    return out

def explore(project):
    df=load_frame(project,'train');corr=df[FEATURES+[TARGET]].corr();corr.to_csv(report_path(project,'eda','correlaciones.csv'))
    vif=variance_inflation_factors(df,FEATURES);vif_max_feature=max(vif,key=vif.get);vif_max=vif[vif_max_feature]
    pd.Series(vif,name='vif').to_csv(report_path(project,'eda','vif.csv'))
    fig,axes=plt.subplots(1,2,figsize=(10,4));axes[0].hist(df.PE,bins=30);axes[0].set(xlabel='Potencia MW',title='Distribución · train');axes[1].scatter(df.AT,df.PE,s=4,alpha=.3);axes[1].set(xlabel='Temperatura °C',ylabel='Potencia MW',title='Asociación · train');fig.tight_layout();fig.savefig(report_path(project,'eda','eda.png'),dpi=130);plt.close(fig)
    value=float(corr.loc['AT','PE']);strength='fuerte' if abs(value)>=.7 else 'moderada' if abs(value)>=.4 else 'débil'
    multicolinealidad='alta' if vif_max>=10 else 'moderada' if vif_max>=5 else 'baja'
    info={'filas_train':len(df),'potencia_media_mw':float(df.PE.mean()),'correlacion_temperatura_potencia':value,'criterios_correlacion':'|r| >=0.7 fuerte; >=0.4 moderada; resto débil; criterio descriptivo','vif':vif,'vif_maximo':vif_max,'vif_variable_maxima':vif_max_feature,'multicolinealidad':multicolinealidad}
    return report(project,'eda',info,f"Train contiene **{len(df)} observaciones**. Correlación temperatura–potencia **{value:.3f}**, asociación **{strength}** bajo la regla declarada. Esta clasificación se actualiza con los datos y no implica causalidad. Multicolinealidad entre AT, V, AP y RH: VIF máximo **{vif_max:.2f}** en **{vif_max_feature}**, nivel **{multicolinealidad}** (umbral descriptivo VIF>=10 alta, >=5 moderada). Un VIF alto afecta la interpretación de coeficientes en Ridge, no la capacidad predictiva del modelo elegido por MAE. El dataset corresponde a operación a plena carga; no acredita desempeño en otros regímenes.")

def baseline(project):
    tr,v=load_frame(project,'train'),load_frame(project,'valid');model=DummyRegressor(strategy='mean').fit(x(tr),tr.PE);save_model(project,model,'baseline');result=metrics(v.PE,model.predict(x(v)))
    return report(project,'baseline',result,f"Referencia: media de potencia de train, constante para validación. MAE **{result['mae_mw']:.3f} MW** y RMSE **{result['rmse_mw']:.3f} MW**. Test y calibración no intervienen.")

def conformal_quantile(residuals,alpha):
    values=np.asarray(residuals,dtype=float)
    if not len(values) or not np.isfinite(values).all() or (values<0).any() or not 0<alpha<1:raise ValueError('Calibración no válida')
    rank=math.ceil((len(values)+1)*(1-alpha))
    if rank>len(values):raise ValueError('Calibración insuficiente para un radio finito al nivel solicitado')
    return float(np.sort(values)[rank-1])

def train(project):
    cfg=config(project);tr,v,cal=[load_frame(project,n) for n in ('train','valid','calibration')];candidates=[];models=[]
    options=[(f'Ridge_alpha_{a}',make_pipeline(StandardScaler(),Ridge(alpha=a))) for a in [1.,10.,100.]]+[(f'HGB_hojas_{leaves}',HistGradientBoostingRegressor(max_leaf_nodes=leaves,max_iter=150,early_stopping=False,random_state=cfg['seed'])) for leaves in [15,31]]
    with threadpool_limits(limits=2):
        for name,model in options:model.fit(x(tr),tr.PE);candidates.append({'modelo':name,**metrics(v.PE,model.predict(x(v)))});models.append(model)
        best=min(range(len(models)),key=lambda i:candidates[i]['mae_mw']);model=models[best];radius=conformal_quantile(np.abs(cal.PE.to_numpy()-model.predict(x(cal))),cfg['interval_alpha'])
    save_model(project,{'model':model,'radius_mw':radius,'name':candidates[best]['modelo'],'alpha':cfg['interval_alpha']})
    info={'criterio':'MAE de validación','modelo_elegido':candidates[best]['modelo'],'candidatos':candidates,'calibracion_filas':len(cal),'radio_intervalo_mw':radius,'cobertura_nominal':1-cfg['interval_alpha']}
    return report(project,'modelado',info,f"Se elige **{info['modelo_elegido']}** por MAE de validación, entre Ridge y boosting. El modelo se ajusta exclusivamente en train y no se reentrena con validación. Una partición de calibración separada de **{len(cal)} casos** fija un radio conformal de **±{radius:.3f} MW**, con cobertura nominal **{1-cfg['interval_alpha']:.0%}**. Test permanece reservado. La cobertura marginal requiere intercambiabilidad; no garantiza cobertura condicional ni temporal.")

def evaluate(project):
    df=load_frame(project,'test');bundle=load_model(project);base=load_model(project,'baseline')
    with threadpool_limits(limits=2):pred=bundle['model'].predict(x(df))
    radius=bundle['radius_mw'];residual=df.PE.to_numpy()-pred;covered=np.abs(residual)<=radius
    result={'baseline':metrics(df.PE,base.predict(x(df))),'modelo':metrics(df.PE,pred),'modelo_elegido':bundle['name'],'cobertura_nominal':1-bundle['alpha'],'cobertura_empirica_test':float(covered.mean()),'ancho_medio_intervalo_mw':2*radius}
    pd.DataFrame([{'estimador':key,**result[key]} for key in ['baseline','modelo']]).to_csv(report_path(project,'evaluacion','metricas_test.csv'),index=False)
    pd.DataFrame({'source_id':df.source_id,'real_mw':df.PE,'prediccion_mw':pred,'inferior_mw':pred-radius,'superior_mw':pred+radius,'cubierto':covered}).to_csv(report_path(project,'evaluacion','predicciones_test.csv'),index=False)
    fig,axes=plt.subplots(1,2,figsize=(10,4));axes[0].scatter(pred,residual,s=4,alpha=.3);axes[0].axhline(0,color='black');axes[0].set(xlabel='Potencia predicha MW',ylabel='Residuo real − predicho',title='Residuos · test');idx=np.argsort(pred)[:80];axes[1].errorbar(np.arange(len(idx)),pred[idx],yerr=radius,fmt='.',alpha=.5,label='Intervalo');axes[1].scatter(np.arange(len(idx)),df.PE.to_numpy()[idx],s=8,label='Real');axes[1].legend();axes[1].set_title('80 predicciones menores · test');fig.tight_layout();fig.savefig(report_path(project,'evaluacion','evaluacion.png'),dpi=130);plt.close(fig)
    heterocedasticidad=float(np.corrcoef(pred,np.abs(residual))[0,1])
    sesgo_residuos=float(pd.Series(residual).skew())
    result['residuos_corr_pred_abs']=heterocedasticidad;result['residuos_sesgo']=sesgo_residuos
    heter_label='posible heterocedasticidad' if abs(heterocedasticidad)>=.2 else 'sin señal clara de heterocedasticidad'
    relation='mejora' if result['modelo']['mae_mw']<result['baseline']['mae_mw'] else 'no mejora'
    return report(project,'evaluacion',result,f"En **{len(df)} casos de test**, MAE **{result['modelo']['mae_mw']:.3f} MW**, frente a **{result['baseline']['mae_mw']:.3f} MW**: **{relation}** el baseline. R² **{result['modelo']['r2']:.4f}**. Cobertura empírica **{result['cobertura_empirica_test']:.2%}**, nominal **{result['cobertura_nominal']:.0%}**, con ancho **{2*radius:.3f} MW**. Se reporta la cobertura observada sin reajustar el intervalo con test. Diagnóstico de residuos: correlación entre residuo absoluto y predicción **{heterocedasticidad:.3f}** ({heter_label}); sesgo (skewness) **{sesgo_residuos:.3f}**. La galería representa las 80 predicciones menores, no una muestra aleatoria. No se demuestra generalización a plantas distintas, otros regímenes ni futuros periodos.")

def run_stage(project,stage):return {'preparacion':prepare,'eda':explore,'baseline':baseline,'modelado':train,'evaluacion':evaluate}[stage](project)
