"""Persistencia, diagnóstico y comentarios basados en resultados calculados."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import importlib
import importlib.util
import json
import subprocess
import sys


def root_for(project):
    """Base de rutas: la carpeta del proyecto, no un paquete global."""
    return Path(project).resolve()


def config(project):
    return json.loads((Path(project) / 'config.json').read_text(encoding='utf-8'))


def write_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False, default=str) + '\n', encoding='utf-8')


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def report_path(project, stage, filename):
    """Ruta local de un reporte; crea la carpeta de su etapa antes de escribir."""
    folder = Path(project) / 'reports' / stage
    folder.mkdir(parents=True, exist_ok=True)
    return folder / filename


def report(project, stage, metrics, comment):
    path = report_path(project, stage, stage)
    write_json(path.with_suffix('.json'), metrics)
    markdown = f'# {config(project)["title"]}: {stage.replace("_", " ")}\n\n{comment}\n'
    path.with_suffix('.md').write_text(markdown, encoding='utf-8')
    return metrics, markdown


def environment(project, install=True):
    modules = ['numpy', 'pandas', 'scipy', 'sklearn', 'pyarrow', 'matplotlib', 'joblib', 'IPython', 'ipykernel', 'nbclient', 'nbformat']
    missing = [m for m in modules if importlib.util.find_spec(m) is None]
    if missing:
        if not install:
            raise RuntimeError(f'Faltan dependencias: {missing}')
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', str(root_for(project) / 'requirements.txt')], cwd=root_for(project))
        raise RuntimeError('Dependencias instaladas. Reinicia el kernel y repite 00.')
    versions = {m: getattr(importlib.import_module(m), '__version__', 'no declarada') for m in modules}
    check = subprocess.run([sys.executable, '-m', 'pip', 'check'], capture_output=True, text=True)
    result = {'fecha_utc': datetime.now(timezone.utc).isoformat(), 'python': sys.executable, 'versiones': versions, 'pip_check_ok': check.returncode == 0, 'pip_check': check.stdout + check.stderr}
    write_json(report_path(project, 'entorno', 'environment.json'), result)
    if check.returncode:
        raise RuntimeError('pip check detectó incompatibilidades; revisa reports/entorno/environment.json.')
    return result


def data_path(project, name='catalogo'):
    return Path(project) / 'data/processed' / f'{name}.parquet'


def save_frame(project, frame, name='catalogo'):
    path = data_path(project, name)
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(path, index=False)


def load_frame(project, name='catalogo'):
    import pandas as pd
    return pd.read_parquet(data_path(project, name))


def save_model(project, obj, name='modelo'):
    import joblib
    path = Path(project) / 'models' / f'{name}.joblib'
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(obj, path)


def load_model(project, name='modelo'):
    import joblib
    return joblib.load(Path(project) / 'models' / f'{name}.joblib')
