"""Descarga verificable e interpretación estricta del formato IDX."""
import gzip
import hashlib
import struct
from pathlib import Path
from urllib.request import Request, urlopen
import shutil
import numpy as np
from sklearn.model_selection import train_test_split
from .common import config, report, sha256

LABELS = ['Camiseta/top', 'Pantalón', 'Jersey', 'Vestido', 'Abrigo', 'Sandalia', 'Camisa', 'Zapatilla', 'Bolso', 'Botín']
FILES = {
    'train-images-idx3-ubyte.gz': '8d4fb7e6c68d591d4c3dfef9ec88bf0d',
    'train-labels-idx1-ubyte.gz': '25c81989df183df01b3e8a0aad5dffbe',
    't10k-images-idx3-ubyte.gz': 'bef4ecab320f06d8554ea6380940ec79',
    't10k-labels-idx1-ubyte.gz': 'bb300cfdad3c16e7a12a480ee83cd310',
}
BASE_URL = 'https://raw.githubusercontent.com/zalandoresearch/fashion-mnist/master/data/fashion/'


def verify(path, expected):
    if hashlib.md5(path.read_bytes()).hexdigest() != expected:
        raise ValueError(f'Checksum incorrecto: {path.name}; conserva el archivo para revisar su procedencia.')


def download(project):
    folder = Path(project) / 'data/raw'
    folder.mkdir(parents=True, exist_ok=True)
    for name, md5 in FILES.items():
        target = folder / name
        if not target.exists():
            partial = target.with_suffix(target.suffix + '.part')
            try:
                with urlopen(Request(BASE_URL + name, headers={'User-Agent': 'portfolio-fashion-mnist'}), timeout=60) as source, partial.open('wb') as dest:
                    shutil.copyfileobj(source, dest)
                verify(partial, md5)
                partial.replace(target)
            finally:
                if partial.exists():
                    partial.unlink()
        verify(target, md5)
    return folder


def read_idx(path):
    with gzip.open(path, 'rb') as stream:
        data = stream.read()
    if len(data) < 8:
        raise ValueError('IDX truncado.')
    magic, count = struct.unpack('>II', data[:8])
    if magic == 2051:
        if len(data) < 16:
            raise ValueError('Cabecera de imágenes truncada.')
        height, width = struct.unpack('>II', data[8:16])
        if (height, width) != (28, 28) or len(data) != 16 + count * 784:
            raise ValueError('Dimensiones o longitud IDX incorrectas.')
        return np.frombuffer(data, dtype=np.uint8, offset=16).reshape(count, 28, 28).copy()
    if magic == 2049 and len(data) == 8 + count:
        labels = np.frombuffer(data, dtype=np.uint8, offset=8).copy()
        if np.any(labels > 9):
            raise ValueError('Etiquetas fuera de 0–9.')
        return labels
    raise ValueError('Tipo o longitud IDX no válidos.')


def fingerprints(images):
    return np.array([hashlib.sha256(image.tobytes()).hexdigest() for image in images])


def partition(images, labels, test_images, cfg):
    hashes, test_hashes = fingerprints(images), set(fingerprints(test_images))
    # Agrupación por contenido: retirar repeticiones y grupos con etiquetas contradictorias.
    groups = {}
    for i, h in enumerate(hashes):
        groups.setdefault(h, []).append(i)
    ambiguous = {h for h, ids in groups.items() if len(set(labels[ids])) > 1}
    ids = np.array([ids[0] for h, ids in groups.items() if h not in ambiguous and h not in test_hashes])
    train, valid = train_test_split(ids, test_size=cfg['valid_fraction'], stratify=labels[ids], random_state=cfg['seed'])
    counts = {'desarrollo_original': len(images), 'repeticiones_retiradas': sum(len(v)-1 for v in groups.values()),
              'grupos_ambiguos': len(ambiguous), 'filas_coincidentes_test': int(sum(h in test_hashes for h in hashes)),
              'desarrollo_deduplicado': len(ids), 'train_antes_muestreo': len(train), 'valid_antes_muestreo': len(valid)}
    for name, current in [('train', train), ('valid', valid)]:
        limit = cfg.get(name + '_limit')
        if limit and limit < len(current):
            current, _ = train_test_split(current, train_size=limit, stratify=labels[current], random_state=cfg['seed'])
        if name == 'train': train = current
        else: valid = current
    return train, valid, counts


def prepare(project):
    folder = Path(project) / 'data/raw'
    for name, md5 in FILES.items():
        if not (folder / name).exists():
            raise FileNotFoundError('Ejecuta 00 o python scripts/download_sources.py para recuperar las fuentes.')
        verify(folder / name, md5)
    images, labels = read_idx(folder/'train-images-idx3-ubyte.gz'), read_idx(folder/'train-labels-idx1-ubyte.gz')
    test, target = read_idx(folder/'t10k-images-idx3-ubyte.gz'), read_idx(folder/'t10k-labels-idx1-ubyte.gz')
    if len(images) != len(labels) or len(test) != len(target) or (len(images), len(test)) != (60000, 10000):
        raise ValueError('Conteos oficiales o correspondencia imagen/etiqueta incorrectos.')
    train_ids, valid_ids, info = partition(images, labels, test, config(project))
    destination = Path(project)/'data/processed'
    destination.mkdir(parents=True, exist_ok=True)
    info['particiones'] = {}
    for name, x, y, ids in [('train', images[train_ids], labels[train_ids], train_ids), ('valid', images[valid_ids], labels[valid_ids], valid_ids), ('test', test, target, np.arange(len(test))+60000)]:
        np.savez_compressed(destination/(name+'.npz'), images=x, labels=y, source_ids=ids)
        info['particiones'][name] = {'filas':len(y),'por_clase':{LABELS[i]:int(np.sum(y==i)) for i in range(10)}}
    info['fuentes'] = [{'archivo':n,'url':BASE_URL+n,'md5':md5,'sha256':sha256(folder/n)} for n,md5 in FILES.items()]
    comment = f"Se preparan **{len(train_ids):,} imágenes de train**, **{len(valid_ids):,} de validación** y el **test oficial completo de {len(test):,} imágenes**. Desarrollo se deduplica por contenido; se retiran grupos ambiguos y coincidencias exactas con test, conservando test intacto. El muestreo estratificado y sus límites se declaran en config.json. Los píxeles se normalizan por la constante 255, sin ajustar transformaciones con test."
    return report(project, 'preparacion', info, comment)


def load(project, name):
    with np.load(Path(project)/'data/processed'/(name+'.npz'), allow_pickle=False) as data:
        return data['images'], data['labels'], data['source_ids']


def features(images):
    if images.ndim != 3 or images.shape[1:] != (28,28) or images.dtype != np.uint8:
        raise ValueError('Se esperan imágenes uint8 de 28×28.')
    return images.reshape(len(images),784).astype(np.float32)/255.0
