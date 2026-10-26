"""Detección semisupervisada de anomalías en el benchmark sintético AI4I."""
from pathlib import Path
from urllib.request import urlopen
import shutil
import zipfile
import io
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from sklearn.metrics import precision_score, recall_score, f1_score, average_precision_score, confusion_matrix
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .common import config, report, report_path, save_frame, load_frame, save_model, load_model, sha256

FEATURES=['Air temperature [K]','Process temperature [K]','Rotational speed [rpm]','Torque [Nm]','Tool wear [min]']
EXCLUDED=['UDI','Product ID','Type','Machine failure','TWF','HDF','PWF','OSF','RNF']
URL='https://archive.ics.uci.edu/static/public/601/ai4i+2020+predictive+maintenance+dataset.zip'

def setup(project):
    path=Path(project)/config(project)['source']
    if not path.exists():
        path.parent.mkdir(parents=True,exist_ok=True);partial=path.with_suffix('.part')
        try:
            with urlopen(URL,timeout=60) as src,partial.open('wb') as dst:shutil.copyfileobj(src,dst)
            with zipfile.ZipFile(partial) as z:
                if z.testzip() is not None:raise ValueError('ZIP corrupto')
                if 'ai4i2020.csv' not in z.namelist():raise ValueError('Fuente inesperada')
            partial.replace(path)
        finally:
            if partial.exists():partial.unlink()
    return path

def prepare(project):
    path=setup(project)
    with zipfile.ZipFile(path) as z:df=pd.read_csv(io.BytesIO(z.read('ai4i2020.csv')))
    if not df['Machine failure'].isin([0,1]).all() or df[FEATURES].isna().any().any():raise ValueError('Variables o etiquetas no válidas')
    df=df[FEATURES+['Machine failure','UDI']].rename(columns={'Machine failure':'label','UDI':'source_id'})
    # Una misma combinación de sensores no cruza particiones.
    df=df.drop_duplicates(subset=FEATURES,keep=False).reset_index(drop=True)
    train,hold=train_test_split(df,test_size=.4,stratify=df.label,random_state=config(project)['seed'])
    valid,test=train_test_split(hold,test_size=.5,stratify=hold.label,random_state=config(project)['seed'])
    info={'fuente_sintetica':True,'sha256':sha256(path),'filas_utilizables':len(df),'variables_sensor':FEATURES,'variables_excluidas':EXCLUDED,'particiones':{}}
    for name,part in [('train',train),('valid',valid),('test',test)]:
        save_frame(project,part,name);info['particiones'][name]={'filas':len(part),'fallos':int(part.label.sum())}
    return report(project,'preparacion',info,'AI4I es un **dataset sintético**, no registros de una planta. Se separan filas 60/20/20 de forma estratificada. Se retiran combinaciones de sensores repetidas para evitar solapamientos. Los IDs, tipo de producto y todas las etiquetas de modos de fallo se excluyen como entradas. No hay fecha que permita afirmar validación temporal.')

def explore(project):
    df=load_frame(project,'train')
    fig,axes=plt.subplots(1,2,figsize=(10,4))
    df.label.value_counts().sort_index().plot.bar(ax=axes[0]);axes[0].set(title='Fallos en train',xlabel='Etiqueta',ylabel='Filas')
    axes[1].scatter(df[FEATURES[2]],df[FEATURES[3]],c=df.label,cmap='coolwarm',s=5,alpha=.5);axes[1].set(xlabel='Velocidad rpm',ylabel='Torque Nm',title='Sensores y etiquetas de train')
    fig.tight_layout();fig.savefig(report_path(project,'eda','eda.png'),dpi=130);plt.close(fig)
    info={'filas_train':len(df),'fallos':int(df.label.sum()),'tasa_fallo':float(df.label.mean()),'nulos':int(df.isna().sum().sum())}
    return report(project,'eda',info,f"Train contiene **{len(df):,} filas**, con **{info['tasa_fallo']:.2%} fallos**. La accuracy mayoritaria ocultaría errores sobre eventos raros; se priorizan precision, recall, F1 y average precision.")

def x(df):return df[FEATURES].to_numpy()

def scores(bundle,df):
    scaled=bundle['scaler'].transform(x(df))
    return np.max(np.abs(scaled),axis=1) if bundle['kind']=='zscore' else -bundle['model'].score_samples(scaled)

def metrics(y,score,threshold):
    pred=score>threshold
    return {'casos':len(y),'precision':float(precision_score(y,pred,zero_division=0)),'recall':float(recall_score(y,pred,zero_division=0)),'f1':float(f1_score(y,pred,zero_division=0)),'average_precision':float(average_precision_score(y,score)) if len(np.unique(y))==2 else None,'matriz_confusion':confusion_matrix(y,pred,labels=[0,1]).tolist(),'alertas':int(pred.sum()),'fallos_reales':int(np.sum(y))}

def baseline(project):
    train,valid=load_frame(project,'train'),load_frame(project,'valid');normal=train[train.label.eq(0)]
    bundle={'scaler':StandardScaler().fit(x(normal)),'kind':'zscore'}
    threshold=float(np.quantile(scores(bundle,normal),.99));bundle['threshold']=threshold
    save_model(project,bundle,'baseline');result=metrics(valid.label,scores(bundle,valid),threshold)
    return report(project,'baseline',result,f"Baseline: máximo z-score absoluto, ajustado **solo con {len(normal):,} filas normales de train**. Umbral fijo en su cuantil 0,99. F1 de validación: **{result['f1']:.4f}**.")

def train(project):
    tr,valid=load_frame(project,'train'),load_frame(project,'valid');normal=tr[tr.label.eq(0)]
    scaler=StandardScaler().fit(x(normal));model=IsolationForest(n_estimators=150,random_state=config(project)['seed'],n_jobs=1).fit(scaler.transform(x(normal)))
    bundle={'scaler':scaler,'model':model,'kind':'isolation_forest'}
    train_score=scores(bundle,normal);valid_score=scores(bundle,valid)
    candidates=[{'quantile':q,'threshold':float(np.quantile(train_score,q)),**metrics(valid.label,valid_score,float(np.quantile(train_score,q)))} for q in config(project)['threshold_quantiles']]
    best=max(candidates,key=lambda c:c['f1']);bundle['threshold']=best['threshold'];save_model(project,bundle)
    info={'criterio':'f1_validacion','threshold_elegido':best['threshold'],'quantile_elegido':best['quantile'],'normales_entrenamiento':len(normal),'candidatos':candidates}
    return report(project,'modelado',info,f"Isolation Forest se ajusta solo con filas normales. Se elige el umbral **{best['threshold']:.4f}** por F1 de validación; test no interviene. Esta cadena es **semisupervisada**: utiliza etiquetas para definir normalidad y seleccionar umbrales, aunque el detector no aprende una clasificación supervisada de fallos.")

def evaluate(project):
    df=load_frame(project,'test');base,model=load_model(project,'baseline'),load_model(project)
    a,b=scores(base,df),scores(model,df)
    result={'baseline':metrics(df.label,a,base['threshold']),'modelo':metrics(df.label,b,model['threshold'])}
    pd.DataFrame({'source_id':df.source_id,'label':df.label,'score':b,'alerta':b>model['threshold']}).to_csv(report_path(project,'evaluacion','predicciones_test.csv'),index=False)
    fig,axes=plt.subplots(1,2,figsize=(9,4));axes[0].hist(b[df.label.eq(0)],bins=35,alpha=.6,label='Normal');axes[0].hist(b[df.label.eq(1)],bins=20,alpha=.6,label='Fallo');axes[0].axvline(model['threshold'],color='red');axes[0].legend();axes[0].set_title('Scores y umbral fijado')
    matrix=np.array(result['modelo']['matriz_confusion']);axes[1].imshow(matrix,cmap='Blues');axes[1].set(xlabel='Predicción',ylabel='Real',title='Matriz de confusión');axes[1].set_xticks([0,1]);axes[1].set_yticks([0,1])
    for i in range(2):
        for j in range(2):axes[1].text(j,i,str(matrix[i,j]),ha='center',color='red')
    fig.tight_layout();fig.savefig(report_path(project,'evaluacion','evaluacion.png'),dpi=130);plt.close(fig)
    relation='supera' if result['modelo']['f1']>result['baseline']['f1'] else 'no supera'
    return report(project,'evaluacion',result,f"En **{len(df):,} filas de test**, Isolation Forest obtiene F1 **{result['modelo']['f1']:.4f}**, precision **{result['modelo']['precision']:.2%}** y recall **{result['modelo']['recall']:.2%}**; **{relation}** el F1 del baseline. Average precision resume el ranking sin depender del umbral. La fuente es sintética y no demuestra anticipación de averías ni eficacia en producción.")

def run_stage(project,stage):return {'preparacion':prepare,'eda':explore,'baseline':baseline,'modelado':train,'evaluacion':evaluate}[stage](project)
