"""EDA visual, baseline lineal y MLP seleccionada exclusivamente en validación."""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.linear_model import SGDClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix
from threadpoolctl import threadpool_limits
from .common import config, report, report_path, save_model, load_model
from .data import LABELS, load, features


def metrics(y, pred):
    return {'casos':len(y), 'accuracy':float(accuracy_score(y,pred)),
            'f1_macro':float(f1_score(y,pred,labels=list(range(10)),average='macro',zero_division=0)),
            'clasificacion':classification_report(y,pred,labels=list(range(10)),target_names=LABELS,zero_division=0,output_dict=True),
            'matriz_confusion':confusion_matrix(y,pred,labels=list(range(10))).tolist()}


def explore(project):
    images, labels, _ = load(project,'train')
    counts = {name:int(np.sum(labels==i)) for i,name in enumerate(LABELS)}
    fig, axes = plt.subplots(2,5,figsize=(10,5))
    for i, ax in enumerate(axes.flat):
        candidates = images[labels==i]
        if len(candidates): ax.imshow(candidates[0],cmap='gray',vmin=0,vmax=255)
        ax.set_title(LABELS[i]); ax.axis('off')
    fig.suptitle('Ejemplos de entrenamiento por clase'); fig.tight_layout()
    fig.savefig(report_path(project,'eda','eda.png'),dpi=130); plt.close(fig)
    fig,axes=plt.subplots(2,5,figsize=(10,5))
    for i,ax in enumerate(axes.flat):
        candidates=images[labels==i]
        if len(candidates):ax.imshow(candidates.mean(axis=0),cmap='gray',vmin=0,vmax=255)
        ax.set_title(LABELS[i]);ax.axis('off')
    fig.suptitle('Imagen media de train por clase');fig.tight_layout()
    fig.savefig(report_path(project,'eda','promedios_clase.png'),dpi=130);plt.close(fig)
    info={'poblacion':'train','filas':len(labels),'alto':28,'ancho':28,'canales':1,'clases':counts,'rango_pixel':[int(images.min()),int(images.max())],'proporcion_pixeles_cero':float(np.mean(images==0))}
    comment=f"El EDA usa solo **{len(labels):,} imágenes de entrenamiento**, de **28×28 píxeles y un canal**. Las clases tienen entre **{min(counts.values())} y {max(counts.values())} ejemplos**; el **{info['proporcion_pixeles_cero']:.2%}** de los píxeles vale cero. Los ejemplos y promedios permiten inspeccionar formas; no prueban separación predictiva ni representan fotos reales."
    return report(project,'eda',info,comment)


def baseline(project):
    cfg=config(project);train,y,_=load(project,'train');valid,target,_=load(project,'valid')
    model=SGDClassifier(loss='log_loss',alpha=0.0001,max_iter=40,tol=0.001,random_state=cfg['seed'])
    with threadpool_limits(limits=cfg['threads']):
        model.fit(features(train),y)
        result=metrics(target,model.predict(features(valid)))
    save_model(project,model,'baseline')
    result['particion']='valid';result['modelo']='SGDClassifier lineal con log_loss'
    return report(project,'baseline',result,f"El baseline lineal obtiene **accuracy {result['accuracy']:.2%}** y **F1 macro {result['f1_macro']:.4f} en validación**. Usa los 784 píxeles normalizados; es una referencia fija, sin seleccionar parámetros con test.")


def train(project):
    cfg=config(project);images,y,_=load(project,'train');valid,target,_=load(project,'valid')
    x,v=features(images),features(valid)
    models=[];candidates=[]
    with threadpool_limits(limits=cfg['threads']):
        for alpha in cfg['alphas']:
            model=MLPClassifier(hidden_layer_sizes=(cfg['hidden_units'],),alpha=alpha,max_iter=cfg['max_iter'],batch_size=128,learning_rate_init=0.001,early_stopping=False,random_state=cfg['seed'])
            model.fit(x,y)
            result=metrics(target,model.predict(v))
            candidates.append({'alpha':alpha,'iteraciones':int(model.n_iter_),'accuracy':result['accuracy'],'f1_macro':result['f1_macro']})
            models.append(model)
    best=max(range(len(models)),key=lambda i:(candidates[i]['f1_macro'],candidates[i]['accuracy']))
    save_model(project,models[best])
    result={'criterio':'f1_macro_validacion; accuracy desempata','alpha_elegido':candidates[best]['alpha'],'neuronas_ocultas':cfg['hidden_units'],'max_iter':cfg['max_iter'],'candidatos':candidates,'particion_seleccion':'valid'}
    comment=f"Se selecciona una **MLP de {cfg['hidden_units']} neuronas ocultas**, con **alpha {result['alpha_elegido']}**, por F1 macro de validación. No se reentrena con validación ni se consulta test para elegir. Es una red densa sobre píxeles aplanados, **no una CNN**; no incorpora convoluciones ni aumento de datos. Las alertas de convergencia deben revisarse, sin asumir que alcanzar el máximo de iteraciones implica convergencia."
    return report(project,'modelado',result,comment)


def evaluate(project):
    cfg=config(project);images,y,ids=load(project,'test')
    model,base=load_model(project),load_model(project,'baseline')
    with threadpool_limits(limits=cfg['threads']):
        x=features(images);pred=model.predict(x);base_pred=base.predict(x)
    result={'particion':'test_oficial','baseline':metrics(y,base_pred),'modelo':metrics(y,pred)}
    frame=pd.DataFrame({'source_id':ids,'clase_real':y,'baseline':base_pred,'modelo':pred})
    frame.to_csv(report_path(project,'evaluacion','predicciones_test.csv'),index=False)
    matrix=np.array(result['modelo']['matriz_confusion'])
    fig,ax=plt.subplots(figsize=(9,8))
    im=ax.imshow(matrix,cmap='Blues');fig.colorbar(im,ax=ax)
    ax.set_xticks(range(10),LABELS,rotation=70);ax.set_yticks(range(10),LABELS)
    ax.set(xlabel='Predicción MLP',ylabel='Clase real',title='Matriz de confusión · test oficial')
    for i in range(10):
        for j in range(10):ax.text(j,i,str(matrix[i,j]),ha='center',va='center',fontsize=7,color='white' if matrix[i,j]>matrix.max()/2 else 'black')
    fig.tight_layout();fig.savefig(report_path(project,'evaluacion','evaluacion.png'),dpi=130);plt.close(fig)
    wrong=np.flatnonzero(pred!=y)
    fig,axes=plt.subplots(3,4,figsize=(11,8))
    for ax,idx in zip(axes.flat,wrong[:12]):
        ax.imshow(images[idx],cmap='gray',vmin=0,vmax=255)
        ax.set_title(f'Real: {LABELS[y[idx]]}\nMLP: {LABELS[pred[idx]]}',fontsize=9)
    for ax in axes.flat:ax.axis('off')
    fig.suptitle('Primeros errores según el orden oficial; no muestra aleatoria');fig.tight_layout()
    fig.savefig(report_path(project,'evaluacion','errores_visuales.png'),dpi=130);plt.close(fig)
    off=matrix.copy();np.fill_diagonal(off,0)
    pairs=sorted([(int(off[i,j]),LABELS[i],LABELS[j]) for i in range(10) for j in range(10) if i!=j],reverse=True)
    result['confusiones_principales']=[{'casos':n,'real':a,'prediccion':b} for n,a,b in pairs[:5]]
    change=result['modelo']['f1_macro']-result['baseline']['f1_macro']
    relation='supera' if change>0 else 'iguala' if change==0 else 'queda por debajo de'
    recalls=result['modelo']['clasificacion'];weak=min(LABELS,key=lambda name:recalls[name]['recall'])
    comment=f"En el **test oficial de {len(y):,} imágenes**, la MLP obtiene **accuracy {result['modelo']['accuracy']:.2%}** y **F1 macro {result['modelo']['f1_macro']:.4f}**: **{relation}** el F1 macro del baseline (**{result['baseline']['f1_macro']:.4f}**). La clase con menor recall es **{weak}: {recalls[weak]['recall']:.2%}**. Hay **{len(wrong):,} errores**. La confusión más frecuente es **{pairs[0][1]} → {pairs[0][2]} ({pairs[0][0]} casos)**. Estos resultados describen un benchmark de prendas pequeñas en gris; no acreditan desempeño con fotografías reales. Test se usa para evaluación y diagnóstico, no para elegir alpha ni iteraciones."
    if len(wrong)==0:comment += ' No hay errores en esta evaluación; la lista de confusiones no indica fallos efectivos.'
    return report(project,'evaluacion',result,comment)
