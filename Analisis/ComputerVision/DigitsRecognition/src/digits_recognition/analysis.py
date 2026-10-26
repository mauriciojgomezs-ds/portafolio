"""Reconocimiento visual con intensidad y gradientes, sin deep learning."""
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.neighbors import NearestCentroid
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.pipeline import make_pipeline
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, classification_report
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .common import config, report, report_path, save_model, load_model, sha256

def setup(project):
    path=Path(project)/config(project)['source']
    if not path.exists():
        data=load_digits();path.parent.mkdir(parents=True,exist_ok=True)
        np.savez_compressed(path,images=data.images.astype(np.uint8),labels=data.target)
    return path

def features(images):
    normalized=images.astype(np.float32)/16
    gy,gx=np.gradient(normalized,axis=(1,2))
    return np.concatenate([normalized.reshape(len(images),-1),gx.reshape(len(images),-1),gy.reshape(len(images),-1)],axis=1)

def prepare(project):
    path=setup(project)
    with np.load(path,allow_pickle=False) as a:images,labels=a['images'],a['labels']
    if images.shape[1:]!=(8,8) or len(images)!=len(labels) or not np.isin(labels,np.arange(10)).all():raise ValueError('Fuente de dígitos incorrecta')
    _,ids=np.unique(images.reshape(len(images),-1),axis=0,return_index=True)
    seed=config(project)['seed']
    ids=np.sort(ids);train,hold=train_test_split(ids,test_size=.4,stratify=labels[ids],random_state=seed)
    valid,test=train_test_split(hold,test_size=.5,stratify=labels[hold],random_state=seed)
    folder=Path(project)/'data/processed';folder.mkdir(parents=True,exist_ok=True)
    info={'sha256':sha256(path),'filas_originales':len(images),'duplicados_retirados':len(images)-len(ids),'particiones':{}}
    for name,idx in [('train',train),('valid',valid),('test',test)]:
        np.savez_compressed(folder/(name+'.npz'),images=images[idx],labels=labels[idx],source_ids=idx);info['particiones'][name]={'filas':len(idx)}
    return report(project,'preparacion',info,'Se usa la copia **load_digits de scikit-learn: imágenes de 8×8**, no el MNIST de 28×28. Se deduplica contenido y divide 60/20/20 estratificado. No hay IDs de escritor para comprobar independencia por persona. El conjunto procede de una parte del dataset UCI; este split propio no replica su protocolo oficial.')

def load(project,name):
    with np.load(Path(project)/'data/processed'/(name+'.npz'),allow_pickle=False) as a:return a['images'],a['labels'],a['source_ids']

def metrics(y,pred):return {'casos':len(y),'accuracy':float(accuracy_score(y,pred)),'f1_macro':float(f1_score(y,pred,average='macro',labels=list(range(10)),zero_division=0)),'matriz_confusion':confusion_matrix(y,pred,labels=list(range(10))).tolist(),'clasificacion':classification_report(y,pred,labels=list(range(10)),output_dict=True,zero_division=0)}

def explore(project):
    images,y,_=load(project,'train');fig,axes=plt.subplots(2,5,figsize=(9,4))
    for i,ax in enumerate(axes.flat):ax.imshow(images[y==i][0],cmap='gray',vmin=0,vmax=16);ax.set_title(str(i));ax.axis('off')
    fig.tight_layout();fig.savefig(report_path(project,'eda','eda.png'),dpi=130);plt.close(fig)
    info={'filas_train':len(y),'clases':{str(i):int(np.sum(y==i)) for i in range(10)},'alto':8,'ancho':8}
    return report(project,'eda',info,f"EDA sobre **{len(y)} imágenes de train**. Diez categorías de dígitos con resolución 8×8. La baja resolución y la falta de independencia por escritor limitan la generalización a documentos reales.")

def baseline(project):
    images,y,_=load(project,'train');valid,target,_=load(project,'valid')
    model=NearestCentroid().fit(images.reshape(len(images),64)/16,y);save_model(project,model,'baseline')
    result=metrics(target,model.predict(valid.reshape(len(valid),64)/16))
    return report(project,'baseline',result,f"Baseline de centroide más cercano sobre intensidad: F1 macro de validación **{result['f1_macro']:.4f}**. No utiliza gradientes ni consulta test.")

def train(project):
    images,y,_=load(project,'train');valid,target,_=load(project,'valid');candidates=[];models=[]
    for c in config(project)['candidates_C']:
        model=make_pipeline(StandardScaler(),SVC(C=c,kernel='rbf'));model.fit(features(images),y)
        result=metrics(target,model.predict(features(valid)));candidates.append({'C':c,'accuracy':result['accuracy'],'f1_macro':result['f1_macro']});models.append(model)
    best=max(range(len(models)),key=lambda i:candidates[i]['f1_macro']);save_model(project,models[best])
    info={'criterio':'f1_macro_validacion','C_elegido':candidates[best]['C'],'candidatos':candidates,'features':192}
    return report(project,'modelado',info,f"SVM RBF sobre **192 atributos**: intensidad y dos gradientes por píxel. Se elige C **{info['C_elegido']}** en validación; el escalamiento se ajusta solo en train. Es reconocimiento con atributos visuales y SVM, no una CNN ni un sistema OCR completo.")

def evaluate(project):
    images,y,ids=load(project,'test');model,base=load_model(project),load_model(project,'baseline');pred=model.predict(features(images))
    shifted=np.zeros_like(images);shifted[:,:,1:]=images[:,:,:-1]
    result={'baseline':metrics(y,base.predict(images.reshape(len(images),64)/16)),'modelo':metrics(y,pred),'robustez_desplazamiento_1px':metrics(y,model.predict(features(shifted)))}
    pd.DataFrame({'source_id':ids,'real':y,'prediccion':pred}).to_csv(report_path(project,'evaluacion','predicciones_test.csv'),index=False)
    fig,axes=plt.subplots(2,5,figsize=(10,4));errors=np.flatnonzero(y!=pred)
    for ax,i in zip(axes.flat,errors[:10]):ax.imshow(images[i],cmap='gray',vmin=0,vmax=16);ax.set_title(f'Real {y[i]} → {pred[i]}')
    for ax in axes.flat:ax.axis('off')
    fig.suptitle('Primeros errores de test; no muestra aleatoria');fig.tight_layout();fig.savefig(report_path(project,'evaluacion','evaluacion.png'),dpi=130);plt.close(fig)
    return report(project,'evaluacion',result,f"Test: **{len(y)} imágenes**; accuracy **{result['modelo']['accuracy']:.2%}**, F1 macro **{result['modelo']['f1_macro']:.4f}** frente a **{result['baseline']['f1_macro']:.4f}** del baseline. Al desplazar artificialmente un píxel a la derecha, la accuracy es **{result['robustez_desplazamiento_1px']['accuracy']:.2%}**. Este ensayo describe sensibilidad a una perturbación concreta, no robustez general ni una evaluación en documentos reales. No se seleccionan parámetros a partir de test.")

def run_stage(project,stage):return {'preparacion':prepare,'eda':explore,'baseline':baseline,'modelado':train,'evaluacion':evaluate}[stage](project)
