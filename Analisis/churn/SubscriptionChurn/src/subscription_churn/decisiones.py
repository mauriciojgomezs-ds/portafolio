"""Modelo adicional para calibración y umbrales; test reservado y costes ilustrativos."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import joblib
from sklearn.base import clone
from sklearn.model_selection import train_test_split,GroupShuffleSplit
from sklearn.calibration import CalibratedClassifierCV
from sklearn.frozen import FrozenEstimator
from sklearn.metrics import average_precision_score,brier_score_loss,log_loss,confusion_matrix

def split_calibration(train,cfg):
    if cfg['split']=='temporal':
        dates=pd.to_datetime(train[cfg['date']]);last=dates.max();fit=train[dates.lt(last)].copy();cal=train[dates.eq(last)].copy();kind='Última fecha de train para calibración; ajuste solo fechas anteriores'
    elif cfg.get('id'):
        groups=train[cfg['id']].astype(str)
        if train[cfg['id']].isna().any():raise ValueError('IDs requeridos para separación por cliente')
        for seed in range(42,62):
            ix,jx=next(GroupShuffleSplit(n_splits=1,test_size=.25,random_state=seed).split(train,groups=groups))
            fit,cal=train.iloc[ix].copy(),train.iloc[jx].copy()
            if fit[cfg['target']].nunique()==cal[cfg['target']].nunique()==2:break
        kind='Separación 75/25 por ID de cliente dentro de train'
    else:
        fit,cal=train_test_split(train,test_size=.25,stratify=train[cfg['target']],random_state=42);kind='Separación estratificada 75/25 dentro de train; sin ID no se comprueba independencia por persona'
    if fit.empty or cal.empty or fit[cfg['target']].nunique()!=2 or cal[cfg['target']].nunique()!=2:raise ValueError('Ajuste y calibración requieren ambas clases')
    return fit,cal,kind

def probability(model,X):
    classes=list(model.classes_)
    if 1 not in classes:raise ValueError('Modelo necesita clase positiva 1')
    return model.predict_proba(X)[:,classes.index(1)]

def reliability(y,p,bins=10):
    y=np.asarray(y);p=np.asarray(p)
    if len(y)!=len(p) or not len(y) or not np.isfinite(p).all() or ((p<0)|(p>1)).any():raise ValueError('Probabilidades no válidas')
    groups=np.minimum((p*bins).astype(int),bins-1);rows=[]
    for b in range(bins):
        mask=groups==b
        if mask.any():rows.append({'bin':b,'casos':int(mask.sum()),'probabilidad_media':float(p[mask].mean()),'frecuencia_evento':float(y[mask].mean())})
    table=pd.DataFrame(rows);ece=float((table.casos*(table.probabilidad_media-table.frecuencia_evento).abs()).sum()/len(y))
    return table,ece

def decision_metrics(y,p,threshold,fn_cost,fp_cost):
    if fn_cost<=0 or fp_cost<=0:raise ValueError('Costes deben ser positivos')
    pred=np.asarray(p)>=threshold;tn,fp,fn,tp=confusion_matrix(y,pred,labels=[0,1]).ravel();n=len(y)
    return {'umbral':float(threshold),'casos':n,'priorizados':int(pred.sum()),'tp':int(tp),'fp':int(fp),'fn':int(fn),'tn':int(tn),'precision':float(tp/(tp+fp)) if tp+fp else 0.,'recall':float(tp/(tp+fn)) if tp+fn else 0.,'coste_error_total':float(fn_cost*fn+fp_cost*fp),'coste_error_por_caso':float((fn_cost*fn+fp_cost*fp)/n)}

def threshold_table(y,p,fn_cost,fp_cost):
    # Include threshold >1 to represent prioritizing nobody even if some p equal 1.
    rows=[decision_metrics(y,p,t,fn_cost,fp_cost) for t in np.r_[np.linspace(0,1,101),np.nextafter(1.,2.)]]
    frame=pd.DataFrame(rows);best=frame.sort_values(['coste_error_total','priorizados','umbral'],ascending=[True,True,False]).iloc[0]
    return frame,float(best.umbral)

def write(project,folder,name,obj):
    path=Path(project)/'reports'/folder/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')

def entrenar_decisiones(project):
    from .flujo import configuracion,cargar,features
    project=Path(project);cfg=configuracion(project);train,valid=cargar(project,'train'),cargar(project,'valid');fit,cal,protocol=split_calibration(train,cfg)
    source=joblib.load(project/'models/modelo.joblib');models=[];candidates=[]
    for weight in [None,'balanced']:
        model=clone(source).set_params(clf__class_weight=weight);model.fit(features(fit,cfg),fit[cfg['target']]);score=average_precision_score(valid[cfg['target']],probability(model,features(valid,cfg)));models.append(model);candidates.append({'class_weight':weight,'average_precision_validacion':float(score)})
    chosen=max(range(len(models)),key=lambda i:candidates[i]['average_precision_validacion']);raw=models[chosen]
    calibrated=CalibratedClassifierCV(FrozenEstimator(raw),method='sigmoid').fit(features(cal,cfg),cal[cfg['target']])
    p=probability(calibrated,features(valid,cfg));costs=cfg.get('decision_costs',{'false_negative':5.,'false_positive':1.});fn_cost=costs['false_negative'];fp_cost=costs['false_positive'];table,threshold=threshold_table(valid[cfg['target']],p,fn_cost,fp_cost)
    table.to_csv(project/'reports/modelado/umbrales_validacion.csv',index=False)
    bundle={'raw':raw,'calibrated':calibrated,'threshold':threshold,'false_negative_cost':fn_cost,'false_positive_cost':fp_cost}
    joblib.dump(bundle,project/'models/decision_model.joblib')
    split_record=pd.DataFrame({'indice_train':train.index,'rol':np.where(train.index.isin(fit.index),'ajuste','calibracion')});split_record.to_csv(project/'reports/modelado/particion_calibracion.csv',index=False)
    info={'decision_protocol':protocol,'decision_fit_cases':len(fit),'decision_calibration_cases':len(cal),'decision_validation_cases':len(valid),'decision_threshold':threshold,'decision_false_negative_cost':fn_cost,'decision_false_positive_cost':fp_cost,'decision_candidates':candidates,'decision_criterion':'AP validación para modelo; sigmoid fijo en calibración; coste FN/FP en validación para umbral','decision_test_used_for_selection':False}
    write(project,'modelado','decisiones_validacion.json',info)
    text=f"# Calibración y política de decisión\n\nModelo adicional: **{len(fit)} filas para ajuste** y **{len(cal)} para calibración**. {protocol}. Se comparan dos ponderaciones por AP de validación; calibración sigmoid fijada de antemano. El umbral **{threshold:.2f}** minimiza coste ilustrativo FN={fn_cost}, FP={fp_cost} en la grilla de validación. Se conserva el modelo original para su comparación histórica; las métricas de decisiones corresponden a este ajuste adicional. Validación selecciona modelo y umbral: su rendimiento es optimista y el test queda reservado.\n"
    (project/'reports/modelado/decisiones.md').write_text(text,encoding='utf-8')
    return info

def evaluar_decisiones(project):
    from .flujo import configuracion,cargar,features
    project=Path(project);cfg=configuracion(project);test=cargar(project,'test');y=test[cfg['target']].to_numpy();bundle=joblib.load(project/'models/decision_model.joblib');X=features(test,cfg);raw=probability(bundle['raw'],X);cal=probability(bundle['calibrated'],X)
    scores=[];curves=[]
    for name,p in [('sin_calibrar',raw),('sigmoid',cal)]:
        curve,ece=reliability(y,p);curve['modelo']=name;curves.append(curve);scores.append({'modelo':name,'brier':float(brier_score_loss(y,p)),'log_loss':float(log_loss(y,p,labels=[0,1])),'ece_10_bins':ece})
    fn_cost,fp_cost=bundle['false_negative_cost'],bundle['false_positive_cost']
    policies=[{'politica':name,**decision_metrics(y,p,t,fn_cost,fp_cost)} for name,p,t in [('sin_calibrar_05',raw,.5),('sigmoid_05',cal,.5),('umbral_validacion',cal,bundle['threshold']),('priorizar_todos',cal,0),('priorizar_ninguno',cal,np.nextafter(1.,2.))]]
    folder=project/'reports/evaluacion';pd.DataFrame(scores).to_csv(folder/'calibracion_test.csv',index=False);pd.concat(curves).to_csv(folder/'fiabilidad_bins.csv',index=False);pd.DataFrame(policies).to_csv(folder/'politicas_test.csv',index=False)
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,2,figsize=(11,4))
    for curve in curves:axes[0].plot(curve.probabilidad_media,curve.frecuencia_evento,'o-',label=curve.modelo.iloc[0])
    axes[0].plot([0,1],[0,1],'k--');axes[0].set(xlabel='Probabilidad media',ylabel='Frecuencia observada',title='Fiabilidad · 10 bins de ancho fijo');axes[0].legend();axes[1].bar([r['politica'] for r in policies],[r['coste_error_por_caso'] for r in policies]);axes[1].tick_params(axis='x',rotation=35);axes[1].set(title='Coste ilustrativo en test',ylabel='Unidades por caso');fig.tight_layout();fig.savefig(folder/'decisiones.png',dpi=130);plt.close(fig)
    info={'decision_probability_scores':scores,'decision_test_policies':policies,'decision_cost_scope':'Penalizaciones ilustrativas de clasificación, no coste real de campaña ni ahorro medido'};write(project,'evaluacion','decisiones_test.json',info)

    prep_path=project/'reports/preparacion/preparacion.json'
    prep_info=json.loads(prep_path.read_text(encoding='utf-8')) if prep_path.exists() else {}
    shared_ids=prep_info.get('ids_compartidos_train_test')
    if shared_ids is None:
        nota_independencia=prep_info.get('limitacion_identidad',f"{project.name} no dispone de ID de cliente; la independencia por persona no puede acreditarse.")
    elif shared_ids>0:
        nota_independencia=f"{project.name} registra {shared_ids} IDs compartidos entre train y test; la independencia por persona sigue pendiente de confirmar."
    else:
        nota_independencia=f"{project.name} no encontró IDs compartidos entre train y test; esto por sí solo no acredita independencia por persona."
    selected=policies[2];relation='menor' if scores[1]['brier']<scores[0]['brier'] else 'igual' if scores[1]['brier']==scores[0]['brier'] else 'mayor'
    text=f"## Probabilidades y decisiones\n\nBrier sigmoid **{scores[1]['brier']:.4f}**, {relation} que sin calibrar **{scores[0]['brier']:.4f}**. Brier y log loss combinan calibración y discriminación; ECE depende de los bins. Las tablas de fiabilidad incluyen soporte y omiten bins vacíos. Con umbral fijado en validación **{bundle['threshold']:.2f}**, se priorizan **{selected['priorizados']} de {len(y)} casos**: recall **{selected['recall']:.2%}**, precisión **{selected['precision']:.2%}**, coste de error **{selected['coste_error_por_caso']:.3f} unidades por caso**. FN={fn_cost}, FP={fp_cost} son supuestos ilustrativos, no importes reales ni ahorro de retención. Se muestran todas las políticas sin elegir una nueva con test. {nota_independencia}\n"
    (folder/'decisiones.md').write_text(text,encoding='utf-8')
    return text
