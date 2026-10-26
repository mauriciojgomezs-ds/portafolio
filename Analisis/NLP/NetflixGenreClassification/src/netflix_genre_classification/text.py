"""Clasificación de texto con vocabulario y etiquetas ajustados solo en train."""
import numpy as np
from sklearn.dummy import DummyClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.multiclass import OneVsRestClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix

from .common import config, load_frame, save_model, load_model, report


def targets(df, labels=None):
    if labels is None:
        return df.label.to_numpy(), 0
    mapping = {label:i for i,label in enumerate(labels)}
    values = np.zeros((len(df),len(labels)),dtype=int)
    unseen = 0
    for row, labs in enumerate(df.labels):
        unseen += sum(label not in mapping for label in labs)
        for label in labs:
            if label in mapping:
                values[row,mapping[label]] = 1
    return values, unseen


def metrics(y, pred, labels=None, unseen=0):
    detail = classification_report(y,pred,output_dict=True,zero_division=0,**({'target_names':labels} if labels is not None else {'labels':[0,1],'target_names':['negativo','positivo']}))
    result = {'casos':len(y), 'accuracy' if labels is None else 'exact_match_etiquetas_conocidas':float(accuracy_score(y,pred)), 'f1_macro':float(f1_score(y,pred,average='macro',zero_division=0)), 'clasificacion':detail, 'etiquetas_fuera_vocabulario_train':unseen}
    if labels is None:
        result['matriz_confusion'] = confusion_matrix(y,pred,labels=[0,1]).tolist()
    else:
        result['etiquetas_train'] = labels
        result['f1_micro'] = float(f1_score(y,pred,average='micro',zero_division=0))
        result['categorias_con_soporte_sin_deteccion'] = [label for label in labels if detail[label]['support'] > 0 and detail[label]['recall'] == 0]
    return result


def baseline(project):
    train, valid = load_frame(project,'train'), load_frame(project,'valid')
    labels = sorted({l for row in train.labels for l in row}) if config(project)['kind']=='text_genre' else None
    y, _ = targets(train,labels)
    model = DummyClassifier(strategy='most_frequent').fit(np.zeros((len(train),1)),y)
    save_model(project, {'model':model, 'labels':labels},'baseline')
    val, unseen = targets(valid,labels)
    result = metrics(val, model.predict(np.zeros((len(valid),1))), labels, unseen)
    return report(project,'baseline',result,f'El baseline predice la clase mayoritaria o las categorías más frecuentes de train. Su F1 macro en validación es **{result["f1_macro"]:.4f}**. No se ajustó con textos de validación o test.')


def train(project):
    cfg = config(project)
    train_df, valid = load_frame(project,'train'), load_frame(project,'valid')
    labels = load_model(project,'baseline')['labels']
    y, _ = targets(train_df,labels)
    vy, unseen = targets(valid,labels)
    candidates, fitted = [], []
    for c in (.5,2.):
        classifier = LogisticRegression(C=c,max_iter=1000,random_state=cfg['seed'])
        if labels is not None:
            classifier = OneVsRestClassifier(classifier)
        pipeline = Pipeline([('tfidf',TfidfVectorizer(stop_words='english',max_features=20000,ngram_range=(1,2),min_df=2,preprocessor=None)),('classifier',classifier)])
        # La limpieza HTML se hace sin aprender parámetros del corpus.
        x = train_df.text.str.replace(r'<[^>]+>',' ',regex=True)
        pipeline.fit(x,y)
        pred = pipeline.predict(valid.text.str.replace(r'<[^>]+>',' ',regex=True))
        result = metrics(vy,pred,labels,unseen)
        candidates.append({'C':c, **result})
        fitted.append(pipeline)
    best = max(range(len(candidates)),key=lambda i:candidates[i]['f1_macro'])
    save_model(project,{'model':fitted[best],'labels':labels})
    result = {'criterio':'f1_macro_validacion','C_elegido':candidates[best]['C'],'candidatos':candidates}
    return report(project,'modelado',result,f'Se compararon dos valores de C y se eligió **{result["C_elegido"]}** por F1 macro de validación. TF-IDF y los clasificadores se ajustaron solo con train; no se reentrena con validación. Las categorías ausentes de train se contabilizan por separado.')


def evaluate(project):
    test = load_frame(project,'test')
    results = {}
    for name in ('baseline','modelo'):
        bundle = load_model(project,name)
        y, unseen = targets(test,bundle['labels'])
        x = np.zeros((len(test),1)) if name=='baseline' else test.text.str.replace(r'<[^>]+>',' ',regex=True)
        results[name] = metrics(y,bundle['model'].predict(x),bundle['labels'],unseen)
    model, base = results['modelo'], results['baseline']
    delta = model['f1_macro'] - base['f1_macro']
    relation = 'supera' if delta > 1e-6 else 'queda por debajo de' if delta < -1e-6 else 'iguala'
    comment = f'En **{model["casos"]:,} textos de test**, el modelo obtiene **F1 macro {model["f1_macro"]:.4f}** y {relation} el baseline ({base["f1_macro"]:.4f}). '
    if config(project)['kind']=='text_genre':
        comment += f'Hay **{model["etiquetas_fuera_vocabulario_train"]} asignaciones de categorías fuera del vocabulario de train** y **{len(model["categorias_con_soporte_sin_deteccion"])} categorías presentes en test con recall cero**. Las métricas solo cubren categorías conocidas; deben interpretarse junto con esos conteos y el detalle por categoría. Superar el baseline no acredita que el modelo detecte adecuadamente todas las categorías. Las entradas contienen exclusivamente sinopsis.'
    else:
        comment += 'Consulta la matriz de confusión y las métricas por clase; el desempeño mide sentimiento de reseñas en inglés, no gusto personal por películas.'
    return report(project,'evaluacion',results,comment)
