"""Informe local reproducible: reúne evidencia sin entrenar ni inventar resultados."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import math
import os
import re

DEFAULT_KIND = "smartfood"


def read(path, default=None):
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else default


def atomic(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(text, encoding='utf-8')
    os.replace(tmp, path)


def registrar_etapa(project, stage, metrics, comment, notebook=None):
    """Exporta cifras y comentarios que ya calculó la celda, sin recalcular modelos."""
    folder = Path(project) / 'reports' / stage
    result = {'fecha_utc': datetime.now(timezone.utc).isoformat(),
              'notebook': notebook, 'metricas': metrics}
    atomic(folder / (stage + '.json'), json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
    atomic(folder / (stage + '.md'), comment + '\n')


def value(v):
    if v is None:
        return 'No disponible'
    if isinstance(v, float):
        return f'{v:.6g}' if math.isfinite(v) else 'No definido'
    if isinstance(v, (list, dict)):
        return json.dumps(v, ensure_ascii=False)
    return str(v).replace('|', '\\|').replace('\n', ' ')


def scalars(obj, prefix='', depth=0):
    if not isinstance(obj, dict):
        return []
    rows = []
    for k, v in obj.items():
        label = f'{prefix} / {k}' if prefix else k
        if k in ('fecha_utc', 'sha256', 'resumen_numerico', 'ejemplos', 'clasificacion'):
            continue
        if isinstance(v, dict) and depth < 2:
            rows.extend(scalars(v, label, depth + 1))
        elif not isinstance(v, (dict, list)):
            rows.append((label, value(v)))
    return rows


def table(rows, headings=('Indicador', 'Valor')):
    return '| ' + ' | '.join(headings) + ' |\n| ' + ' | '.join(['---'] * len(headings)) + ' |\n' + '\n'.join('| ' + ' | '.join(value(v) for v in row) + ' |' for row in rows)


def comparison(metrics, kind):
    """Compara solo indicadores pertinentes; no equipara tareas diferentes."""
    baseline, model = metrics.get('baseline', {}), metrics.get('modelo', {})
    if not isinstance(baseline, dict) or not isinstance(model, dict):
        return ''
    indicators = {'forecast': ('mae', 'rmse'), 'anomaly': ('precision', 'recall', 'f1'),
                  'collaborative': ('hit_rate_at_k', 'ndcg_at_k'),
                  'text_sentiment': ('accuracy', 'f1_macro'),
                  'text_genre': ('f1_micro', 'f1_macro'),
                  'churn': ('accuracy', 'average_precision', 'roc_auc')}.get(kind, ())
    lines = []
    for name in indicators:
        a, b = baseline.get(name), model.get(name)
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            delta = b - a
            status = 'iguala' if delta == 0 else 'mejora' if (delta < 0 if name in ('mae', 'rmse') else delta > 0) else 'no mejora'
            lines.append(f'- `{name}`: baseline **{value(a)}**, modelo **{value(b)}**; el modelo **{status}** este indicador en la evaluación guardada.')
    if kind in ('music_content', 'movie_content'):
        return 'La coincidencia de categorías y la cobertura son diagnósticos descriptivos; no demuestran satisfacción ni relevancia personal.'
    return '\n'.join(lines)


def generar_informe(project):
    project = Path(project).resolve()
    cfg = read(project / 'config.json', {})
    kind = cfg.get('kind', DEFAULT_KIND)
    title = cfg.get('title', project.name)
    summary = read(project / 'reports/ejecucion/resumen.json', {})
    stages = ('preparacion', 'eda', 'baseline', 'modelado', 'evaluacion')
    manifest, stage_data, sections = [], {}, []
    missing = []

    def evidence(path):
        data = path.read_bytes()
        manifest.append({'ruta': path.relative_to(project).as_posix(),
                         'sha256': hashlib.sha256(data).hexdigest(),
                         'modificacion_utc': datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat()})

    for stage in stages:
        folder = project / 'reports' / stage
        files = sorted(folder.glob('*.json')) + sorted(folder.glob('*.md'))
        body = []
        merged = {}
        for path in files:
            evidence(path)
            link = '../../' + path.relative_to(project).as_posix()
            if path.suffix == '.json':
                data = read(path, {})
                if isinstance(data, dict):
                    if path.name != 'auditoria_distribuciones.json':
                        merged.update(data.get('metricas', data))
                    rows = scalars(data.get('metricas', data))
                    if rows:
                        body += [f'Indicadores de [{path.name}]({link}):', table(rows[:24])]
                    if len(rows) > 24:
                        body.append('El archivo enlazado contiene el detalle restante.')
            else:
                # Avoid shifting relative image links when embedding a stage document.
                text = path.read_text(encoding='utf-8').strip()
                text = re.sub(r'(!?\[[^\]]*\])\(([^)]+)\)', lambda m: m[0] if '://' in m[2] or m[2].startswith('#') else m[1] + '(' + '../../' + (path.parent / m[2]).resolve().relative_to(project).as_posix() + ')', text)
                text = re.sub(r'^(#{1,5}) ', r'\1## ', text, flags=re.M)
                body += [text, f'[Reporte de la etapa]({link}).']
        for image in (folder / 'eda.png', folder / 'distribucion_target.png', folder / 'evaluacion.png', folder / 'clusters.png', folder / 'recipes_filtrado/recipes_filtrado_correlacion.png'):
            if image.exists():
                evidence(image)
                body.append('![Figura de ' + stage + '](../../' + image.relative_to(project).as_posix() + ')')
        for csv in sorted(folder.glob('*.csv')):
            evidence(csv)
            body.append('[Detalle: ' + csv.name + '](../../' + csv.relative_to(project).as_posix() + ')')
        if not files:
            missing.append(stage)
            body.append('No hay un reporte exportado de esta etapa. Consulta su notebook; esta ausencia no implica que nunca se haya ejecutado.')
        stage_data[stage] = merged
        sections.append('## ' + {'preparacion':'Datos y preparación', 'eda':'Hallazgos exploratorios', 'baseline':'Baseline', 'modelado':'Modelo y selección', 'evaluacion':'Evaluación y conclusiones'}[stage] + '\n\n' + '\n\n'.join(body))

    notebooks = []
    for path in sorted((project / 'notebooks').glob('0[1-5]*.ipynb')):
        nb = read(path, {})
        code = [c for c in nb.get('cells', []) if c['cell_type'] == 'code' and ''.join(c.get('source', [])).strip()]
        timestamps = [v for c in code for v in c.get('metadata', {}).get('execution', {}).values() if isinstance(v, str)]
        notebooks.append({'notebook': path.name, 'celdas_con_salida': sum(c.get('execution_count') is not None for c in code),
                          'celdas_codigo': len(code), 'ultima_ejecucion_utc': max(timestamps, default=None),
                          'errores_guardados': sum(o.get('output_type') == 'error' for c in code for o in c.get('outputs', []))})
        evidence(path)
    state = summary.get('estado', 'sin_resumen')
    finish = summary.get('fin_utc')
    mixed = bool(finish) and any(datetime.fromisoformat(item['modificacion_utc']) > datetime.fromisoformat(finish.replace('Z', '+00:00')) for item in manifest)
    status = 'ejecucion_no_completada' if state != 'completado' else 'evidencia_parcial' if missing else 'actualizado_por_etapas' if mixed else 'evidencia_disponible'
    if any(n['errores_guardados'] for n in notebooks):
        status = 'evidencia_con_errores'
    labels = {'ejecucion_no_completada': 'Ejecución no completada', 'evidencia_parcial': 'Evidencia parcial', 'actualizado_por_etapas': 'Resultados actualizados por etapas', 'evidencia_disponible': 'Evidencia disponible', 'evidencia_con_errores': 'Evidencia con errores'}
    notes = [f'Estado del informe: **{labels[status]}**. Estado del último maestro: **{state}**.',
             'Este documento reúne los archivos guardados; no ejecuta modelos ni certifica su utilidad. Las fechas y huellas del manifiesto permiten revisar su procedencia.']
    if mixed:
        notes.append('Hay archivos de resultados o notebooks actualizados después de la última ejecución completa del maestro. Los resultados corresponden a actualizaciones por etapa; ejecuta 06 para cerrar una nueva pasada completa.')
    if state != 'completado':
        notes.append('La secuencia no consta como completada. Los resultados de etapas no terminadas pueden proceder de una pasada anterior; no los interpretes como resultados de esta secuencia.')
    if missing:
        notes.append('Etapas sin reporte exportado: **' + ', '.join(missing) + '**.')
    objective = (project / 'README.md').read_text(encoding='utf-8') if (project / 'README.md').exists() else ''
    objective = next((s.strip() for s in objective.split('\n\n')[1:] if s.strip() and not s.startswith(('#', '|', '```', '**'))), 'Consulta el README del proyecto para el contexto y el objetivo.')
    alerts = []
    descriptions = []
    for path in sorted((project / 'reports/alertas').glob('*.json')):
        data = read(path, [])
        records = data if isinstance(data, list) else data.get('alertas', [])
        alerts.append((path.stem, len(records)))
        for item in records:
            if isinstance(item, dict):
                descriptions.append((path.stem, item.get('tipo', 'Aviso'), item.get('apariciones', 1), item.get('descripcion', 'Consulta el detalle original.'), item.get('accion_sugerida', 'Revisar el aviso.')))
        evidence(path)
    limits = {'smartfood': 'Las tareas de reconstrucción, clasificación y ranking tienen protocolos distintos. La accuracy no demuestra personalización. Revisa la disponibilidad temporal de aggregatedrating y reserva validación y test para seleccionar parámetros.',
              'churn': 'La definición del churn y la disponibilidad temporal de las variables deben confirmarse. Revisa recall por clase y posibles diferencias entre train y test; las métricas de proyectos distintos no son directamente comparables.',
              'forecast': 'El protocolo evalúa un paso con valores previos observados; no un pronóstico multisemana. Las compras positivas no representan ventas netas. El histórico corto limita las conclusiones entre temporadas.',
              'anomaly': 'Las métricas se calculan por punto dentro de ventanas; no son la puntuación oficial NAB. Varias alertas pueden pertenecer al mismo evento.',
              'collaborative': 'La muestra y el corte por usuario limitan el alcance. No equivale a una simulación temporal global ni a resultados de una plataforma real.',
              'music_content': 'No hay interacciones ni relevancia personal para evaluar satisfacción. Similitud de contenido no implica preferencias aprendidas.',
              'movie_content': 'Las categorías forman parte del contenido y de los diagnósticos; su coincidencia no constituye una validación independiente.',
              'text_sentiment': 'El alcance es sentimiento de reseñas en inglés. Un resultado en el test disponible no acredita robustez en otros dominios o idiomas.',
              'text_genre': 'Las categorías no aprendidas y la evaluación multietiqueta requieren revisar soportes y recall por clase.',
              'cluster_music': 'Silhouette y estabilidad describen el espacio de atributos; no validan géneros ni utilidad para usuarios.',
              'cluster_customers': 'Los perfiles descriptivos y su estabilidad no demuestran impacto comercial ni beneficios netos.'}.get(kind, 'Revisa el protocolo y la representatividad de los datos antes de generalizar.')
    actions = ['Comprobar procedencia, condiciones de uso y disponibilidad temporal de las variables.',
               'Completar una pasada de 06 y revisar las alertas antes de publicar el informe.']
    if kind in ('music_content', 'movie_content', 'collaborative', 'smartfood'):
        actions.append('Definir relevancia y candidatos, y evaluar ranking con usuarios o interacciones independientes.')
    elif kind.startswith('cluster'):
        actions.append('Validar los perfiles con el uso previsto y estudiar sensibilidad a atributos, escalamiento y muestras.')
    elif kind in ('forecast', 'anomaly'):
        actions.append('Ampliar la evaluación temporal con varios cortes; en anomalías, incorporar métricas por evento.')
    else:
        actions.append('Revisar métricas por clase y errores frecuentes; ajustar decisiones en validación, conservando test independiente.')
    eval_metrics = stage_data['evaluacion']
    conclusion = comparison(eval_metrics, kind)
    if conclusion:
        sections[-1] += '\n\n### Comparación automática\n\n' + conclusion
    env = project / 'reports/entorno/environment.json'
    for path in (project/'README.md', project/'config.json', project/'reports/ejecucion/resumen.json', env):
        if path.exists(): evidence(path)
    created = datetime.now(timezone.utc).isoformat()
    report = f'# Informe integral · {title}\n\nGenerado: {created} (UTC).\n\n' + '\n\n'.join(notes)
    report += '\n\n## Objetivo y configuración\n\n' + objective + '\n\n'
    if cfg: report += table(scalars(cfg)) + '\n\n'
    report += '\n\n'.join(sections)
    report += '\n\n## Alertas y estado de ejecución\n\n'
    report += table(alerts, ('Notebook', 'Tipos de aviso registrados')) if alerts else 'No hay inventarios de alertas disponibles.'
    if descriptions:
        report += '\n\n' + table(descriptions, ('Notebook', 'Tipo', 'Apariciones', 'Significado', 'Acción sugerida'))
    report += '\n\nUna tabla vacía de warnings no demuestra ausencia de errores o validez del modelo. Consulta [alertas](../alertas/) y [resumen del maestro](../ejecucion/resumen.json).\n\n'
    report += table([(n['notebook'], f"{n['celdas_con_salida']}/{n['celdas_codigo']}", n['ultima_ejecucion_utc'], n['errores_guardados']) for n in notebooks], ('Notebook', 'Celdas ejecutadas guardadas', 'Última ejecución UTC', 'Errores guardados'))
    report += '\n\n## Limitaciones y próximos pasos\n\n' + limits + '\n\n' + '\n'.join('- ' + a for a in actions)
    report += '\n\n## Evidencia y reproducción\n\nDesde la carpeta de este proyecto, ejecuta `python scripts/generate_report.py` para reunir los resultados guardados, o 06 para ejecutar los análisis y actualizar el informe.\n\n'
    report += 'Consulta el [README](../../README.md), la [guía del informe](../../docs/informe_final.md) y el [manifiesto con datos y huellas](informe_final.json). El informe conserva una versión vigente por proyecto.\n'
    record = {'proyecto': title, 'generado_utc': created, 'estado': status, 'estado_maestro': state,
              'etapas_sin_reporte': missing, 'notebooks': notebooks, 'resultados': stage_data,
              'fuentes': manifest, 'limitaciones': limits, 'proximos_pasos': actions}
    folder = project / 'reports/informe_final'
    atomic(folder/'informe_final.json', json.dumps(record, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
    atomic(folder/'informe_final.md', report)
    return folder/'informe_final.md'
