"""Build a static portfolio from versioned documentation, without executing projects."""
from pathlib import Path
from html import escape as e
from urllib.parse import urlsplit, unquote, quote
import json
import os
import re
import shutil
import posixpath
from markdown_it import MarkdownIt
from markdown_it.token import Token

SITE = Path(__file__).resolve().parents[1]
ROOT = SITE.parent
OUT = SITE / 'dist'
PROFILE = json.loads((SITE / 'data/perfil.json').read_text(encoding='utf-8'))
REPO = PROFILE['repository_url'].rstrip('/') or ('https://github.com/' + os.environ['GITHUB_REPOSITORY'] if os.environ.get('GITHUB_REPOSITORY') else '')
BRANCH = os.environ.get('GITHUB_REF_NAME') or PROFILE.get('repository_branch', 'main')
pending = {}
assets = set()
project_roots = {}
evidence_pages = {}


def slug(value):
    return re.sub(r'[^a-z0-9]+', '-', value.lower()).strip('-')


def heading_slug(value):
    return re.sub(r'[^\w\-\s]', '', value.lower()).strip().replace(' ', '-')


def href(current, target):
    return posixpath.relpath(str(target).replace('\\', '/'), str(Path(current).parent).replace('\\', '/'))


def public(path):
    try:
        parts = path.resolve().relative_to(ROOT).parts
    except ValueError:
        return False
    return not any(p.lower() in {'data', 'back', 'models', '.venv', '.git', 'runs', '__pycache__'} or p.startswith('.env') for p in parts)


def copy_asset(path):
    path = path.resolve()
    if not public(path) or not path.is_file():
        return None
    relative = path.relative_to(ROOT)
    allowed = path.suffix.lower() in {'.png', '.jpg', '.jpeg', '.svg', '.webp', '.gif', '.csv', '.json', '.pdf'}
    if not allowed or path.stat().st_size > 8_000_000 or not any(p in {'docs', 'reports'} for p in relative.parts):
        return None
    target = Path('evidencia') / relative
    (OUT / target).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, OUT / target)
    assets.add(target.as_posix())
    return target


def doc_route(path):
    path = path.resolve()
    if path not in pending:
        pending[path] = Path('documentos') / path.relative_to(ROOT).with_suffix('.html')
    return pending[path]


def rewrite_url(raw, source, current, image=False):
    parsed = urlsplit(raw)
    if parsed.scheme:
        return raw if parsed.scheme in {'https', 'http', 'mailto'} else None
    if parsed.netloc:
        return None
    if not parsed.path:
        return raw
    path = (source.parent / unquote(parsed.path)).resolve()
    if not public(path):
        return None
    if path.is_file() and path.suffix.lower() == '.md' and not image:
        target = doc_route(path)
    else:
        target = copy_asset(path)
        if target and not image and path.suffix.lower() == '.csv':
            viewer = Path('documentos') / path.relative_to(ROOT).with_suffix(path.suffix + '.html')
            evidence_pages[path] = (viewer, target)
            target = viewer
    if target:
        return href(current, target) + ('#' + parsed.fragment if parsed.fragment else '')
    if REPO and path.exists():
        kind = 'tree' if path.is_dir() else 'blob'
        return f'{REPO}/{kind}/{quote(BRANCH, safe="")}/{quote(path.relative_to(ROOT).as_posix(), safe="/")}' + ('#' + parsed.fragment if parsed.fragment else '')
    return None


def markdown(source, current):
    md = MarkdownIt('commonmark', {'html': False}).enable('table')
    tokens = md.parse(source.read_text(encoding='utf-8-sig'))
    headings = {}
    for i, token in enumerate(tokens):
        if token.type == 'heading_open':
            key = heading_slug(tokens[i + 1].content)
            n = headings.get(key, 0)
            headings[key] = n + 1
            token.attrSet('id', key + (f'-{n}' if n else ''))
        if token.children:
            stack = []
            children = []
            for child in token.children:
                children.append(child)
                if child.type == 'link_open':
                    value = rewrite_url(child.attrGet('href') or '', source, current)
                    json_file = bool(value and not urlsplit(value).scheme and urlsplit(value).path.lower().endswith('.json'))
                    stack.append((bool(value), value if json_file else None))
                    if value:
                        child.attrSet('href', value)
                        if json_file:
                            child.attrSet('target', '_blank')
                            child.attrSet('rel', 'noopener noreferrer')
                            child.attrSet('title', 'Abrir JSON en una nueva pestaña')
                    else:
                        child.tag = 'span'
                        child.attrs = {'class': 'project-file'}
                elif child.type == 'link_close' and stack:
                    valid, download = stack.pop()
                    if not valid:
                        child.tag = 'span'
                    elif download:
                        extra = Token('html_inline', '', 0)
                        filename = unquote(Path(urlsplit(download).path).name)
                        extra.content = f' <span class="evidence-download">· <a href="{e(download, quote=True)}" download aria-label="Descargar {e(filename, quote=True)}">Descargar</a></span>'
                        children.append(extra)
                elif child.type == 'image':
                    value = rewrite_url(child.attrGet('src') or '', source, current, True)
                    if value:
                        child.attrSet('src', value)
                        child.attrSet('loading', 'lazy')
                    else:
                        child.type = 'text'
                        child.content = '[Imagen disponible en el proyecto: ' + child.content + ']'
            token.children = children
    return md.renderer.render(tokens, md.options, {})


def shell(title, body, current='index.html', script=False):
    home = href(current, 'index.html')
    script_path = 'assets/app.js' if script is True else script
    brand = e(PROFILE.get('brand', 'Mauricio Gómez S'))
    brand_mark = e(PROFILE.get('brand_mark', 'MG'))
    return f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(title)} · Portafolio</title><meta name="description" content="{e(PROFILE['description'])}"><link rel="stylesheet" href="{href(current, 'assets/styles.css')}"></head><body><a class="skip" href="#contenido">Ir al contenido</a><header class="topbar"><nav class="container nav" aria-label="Principal"><a class="brand" href="{home}"><span class="brand-mark">{brand_mark}</span>{brand}</a><div class="nav-links"><a href="{home}#proyectos">Proyectos</a><a href="{href(current, 'informes/index.html')}"{chr(32) + 'aria-current="page"' if current == 'informes/index.html' else ''}>Informes</a><a href="{href(current, 'demos/index.html')}"{chr(32) + 'aria-current="page"' if current == 'demos/index.html' else ''}>Demos</a><a class="github-link" href="{e(PROFILE['github_url'])}">GitHub ↗</a></div></nav></header>{body}<footer class="footer"><div class="container footer-inner"><span>Ciencia de datos · Evidencia · Aplicaciones</span><a href="{e(PROFILE['github_url'])}">@mauriciojgomezs-ds ↗</a></div></footer>{f'<script src="{href(current, script_path)}" defer></script>' if script else ''}</body></html>'''


def write(target, content):
    (OUT / target).parent.mkdir(parents=True, exist_ok=True)
    (OUT / target).write_text(content, encoding='utf-8')


def document_navigation(source, current):
    owner = next((project for root, project in sorted(project_roots.items(), key=lambda item: len(item[0].parts), reverse=True) if source.resolve().is_relative_to(root)), None)
    links = []
    if owner:
        if owner['report'] and str(current).replace('\\', '/') != owner['report']:
            links.append((owner['report'], f'← Volver al informe de {owner["folder"]}'))
        if str(current).replace('\\', '/') != owner['page']:
            links.append((owner['page'], 'Ver proyecto'))
        if str(current).replace('\\', '/') == owner['report']:
            links.insert(0, ('informes/index.html', '← Todos los informes'))
    if not links:
        links.append(('index.html#proyectos', '← Volver a los proyectos'))
    buttons = ''.join(f'<a class="button secondary" {"data-return-report " if label.startswith("← Volver al informe") else ""}href="{href(current, target.split("#")[0])}{"#" + target.split("#", 1)[1] if "#" in target else ""}">{e(label)}</a>' for target, label in links)
    return f'<nav class="document-actions return-navigation" aria-label="Volver al informe o proyecto">{buttons}</nav>'


def evidence_content(source):
    text = source.read_text(encoding='utf-8-sig', errors='replace')
    if source.suffix.lower() == '.json':
        try:
            text = json.dumps(json.loads(text), ensure_ascii=False, indent=2)
        except ValueError:
            pass
    lines = text.splitlines()
    preview = '\n'.join(lines[:200])[:30000]
    note = '<p>Vista previa limitada. Descarga el archivo para consultar todo el contenido.</p>' if len(lines) > 200 or len(text) > 30000 else ''
    return f'<h1>{e(source.name)}</h1><p>Evidencia generada por el proyecto. Puedes regresar a su informe usando los botones de navegación.</p>{note}<pre><code>{e(preview)}</code></pre>'


def profile_sections():
    expertise = ''.join(f'<article class="card"><div class="card-body"><h3>{e(item["title"])}</h3><p class="card-description">{e(item["description"])}</p><p class="tech">{e(item["tools"])}</p></div></article>' for item in PROFILE.get('expertise', []))
    experience = ''.join(f'<article class="career-item"><p class="eyebrow">{e(item["period"])}</p><h3>{e(item["role"])}</h3><p>{e(item["description"])}</p>' + (f'<p class="career-achievement"><span>Aporte destacado</span>{e(item["achievement"])}</p>' if item.get('achievement') else '') + '</article>' for item in PROFILE.get('experience', []))
    education = ''.join(f'<article class="education-item"><h3>{e(item["title"])}</h3><p>{e(item["institution"])} · {e(item["period"])}</p><p>{e(item["detail"])}</p></article>' for item in PROFILE.get('education', []))
    skills_section = f'<section class="container section profile-section"><div class="section-head"><div><p class="eyebrow">04 / Áreas de trabajo</p><h2>Áreas de trabajo</h2></div><p>Una trayectoria que combina operación, tecnología y diseño de soluciones orientadas al negocio.</p></div><div class="grid expertise-grid">{expertise}</div></section>' if expertise else ''
    career_section = f'<section class="container section profile-section" id="trayectoria"><p class="eyebrow">05 / Trayectoria y formación</p><div class="career-layout"><div><h2>Mi recorrido</h2><p class="career-intro">Del análisis de la operación al diseño de soluciones de datos e IA. Cuatro etapas que resumen cómo han evolucionado mis responsabilidades y aportes.</p>{experience}<p class="profile-note">Síntesis de mi trayectoria y logros recogidos en el CV de octubre de 2026. Estas cifras corresponden a experiencias laborales, con un alcance distinto al de los proyectos de este portafolio.</p></div><div><h2>Formación seleccionada</h2>{education}</div></div></section>' if experience or education else ''
    return skills_section + career_section


def contact_links():
    links = f'<a href="{e(PROFILE["github_url"])}">Ver mi perfil en GitHub ↗</a>'
    if PROFILE.get('email'):
        links += f'<a href="mailto:{e(PROFILE["email"])}">Contactar por correo ↗</a>'
    linkedin = PROFILE.get('linkedin_url', '')
    if linkedin and urlsplit(linkedin).scheme == 'https':
        links += f'<a href="{e(linkedin)}">LinkedIn ↗</a>'
    return links


def build():
    pending.clear()
    assets.clear()
    project_roots.clear()
    evidence_pages.clear()
    OUT.mkdir(exist_ok=True)
    # Only remove generated output after checking its exact workspace location.
    if OUT.resolve() != (ROOT / 'SitioWeb/dist').resolve():
        raise RuntimeError('Unexpected output directory')
    for item in OUT.iterdir():
        shutil.rmtree(item) if item.is_dir() else item.unlink()
    (OUT / 'assets').mkdir()
    for name in ['styles.css', 'app.js', 'reports.js', 'demos.js', 'navigation.js']:
        shutil.copy2(SITE / 'src' / name, OUT / 'assets' / name)
    questions = {}
    for line in (ROOT / 'Analisis/README.md').read_text(encoding='utf-8').splitlines():
        match = re.match(r'\|\s*\[([^]]+)\]\([^)]+README.md\)\s*\|\s*([^|]+)', line)
        if match:
            questions[match[1]] = match[2].strip()
    projects = []
    app_questions = {
        'SalesAccess': '¿Cómo consultar ventas respetando el rol y el segmento de cada usuario?',
        'knowledge_base_mvp': '¿Cómo recuperar documentación relevante desde una base de conocimiento local?',
        'MeetingCopilot': '¿Cómo encontrar decisiones y compromisos con evidencia en una reunión?',
        'DataCopilot': '¿Cómo responder preguntas sobre una tabla con cálculos verificables?',
        'DocumentAnalyzer': '¿Cómo extraer campos y detectar discrepancias con evidencia documental?',
    }
    for line in (ROOT / 'README.md').read_text(encoding='utf-8').splitlines():
        match = re.match(r'\|\s*([^|]+)\|\s*\[([^]]+)\]\(([^)]+README.md)\)\s*\|\s*([^|]+)\|\s*([^|]+)\|', line)
        if not match:
            continue
        area, name, path, techniques, status = [x.strip() for x in match.groups()]
        source = ROOT / path
        if not source.exists():
            raise FileNotFoundError(source)
        folder = source.parent
        project_id = slug(folder.name)
        family = 'analisis' if path.startswith('Analisis/') else 'iag' if path.startswith('IAG/') else 'bi'
        route = Path('proyectos') / project_id / 'index.html'
        pending[source.resolve()] = route
        report = folder / 'reports/informe_final/informe_final.md'
        report_route = Path('informes') / project_id / 'index.html' if report.exists() else None
        if report_route:
            pending[report.resolve()] = report_route
        question = questions.get(name, app_questions.get(folder.name, techniques))
        project = dict(id=project_id, name=name, folder=folder.name, area=area, family=family, question=question, techniques=techniques, status=status, page=route.as_posix(), report=report_route.as_posix() if report_route else None)
        projects.append(project)
        project_roots[folder.resolve()] = project
    if len({p['id'] for p in projects}) != len(projects):
        raise ValueError('Duplicate project identifiers')
    demos = json.loads((SITE / 'data/demos.json').read_text(encoding='utf-8'))
    screenshots = {d['project']: copy_asset(ROOT / d['screenshot']) for d in demos}

    def card(p, featured=False):
        image = screenshots.get(p['folder'])
        if featured and not image:
            original = next(s for s, target in pending.items() if target.as_posix() == p['page'])
            figures = sorted(original.parent.glob('reports/evaluation/*.png')) + sorted(original.parent.glob('reports/eda/*.png'))
            if figures:
                image = copy_asset(figures[0])
        visual = f'<div class="card-visual"><img src="{image.as_posix()}" alt="Figura del proyecto {e(p["name"])}" loading="lazy"></div>' if image else ''
        links = f'<a href="{p["page"]}">Ver proyecto →</a>'
        if p['report']:
            links += f'<a href="{p["report"]}">Leer informe</a>'
        if REPO:
            original = next(s for s, target in pending.items() if target.as_posix() == p['page'])
            links += f'<a href="{REPO}/tree/{quote(BRANCH, safe="")}/{quote(original.parent.relative_to(ROOT).as_posix(), safe="/")}">Código ↗</a>'
        return f'<article class="card" data-project="{p["id"]}">{visual}<div class="card-body"><p class="eyebrow">{e(p["area"])}</p><h3>{e(p["name"])}</h3><p class="card-description">{e(p["question"])}</p><p class="tech">{e(p["techniques"])}</p><p class="status">{e(p["status"])}</p><div class="card-links">{links}</div></div></article>'

    analysis = [p for p in projects if p['family'] == 'analisis']
    themes = len({s.relative_to(ROOT).parts[1] for s, target in pending.items() if s.relative_to(ROOT).parts[0] == 'Analisis' and target.parts[0] == 'proyectos'})
    featured = ''.join(card(p, True) for key in PROFILE['featured'] for p in projects if p['folder'] == key)
    demo_html = ''
    for d in demos:
        image = screenshots[d['project']]
        route = doc_route(ROOT / d['walkthrough'])
        media = f'<img class="demo-image" src="{href("demos/index.html", image)}" alt="{e(d["title"])}" loading="lazy">' if image else ''
        video_file = d.get('video_file', '')
        video_url = d.get('video_url', '')
        if video_file and video_url:
            raise ValueError('Configura video_file o video_url, no ambos en una misma demo')
        if video_file:
            video = (SITE / video_file).resolve()
            if not video.is_relative_to((SITE / 'assets/media').resolve()) or video.suffix.lower() != '.mp4' or not video.is_file():
                raise ValueError('El video debe ser un MP4 existente dentro de SitioWeb/assets/media')
            target = Path('assets/media') / video.name
            (OUT / target).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(video, OUT / target)
            media = f'<div class="video-container"><video controls preload="metadata" poster="{href("demos/index.html", image) if image else ""}"><source src="{href("demos/index.html", target)}" type="video/mp4"></video></div>'
        elif video_url:
            parsed = urlsplit(video_url)
            from urllib.parse import parse_qs
            video_id = parsed.path.strip('/') if parsed.hostname == 'youtu.be' else parse_qs(parsed.query).get('v', [''])[0] if parsed.hostname in {'youtube.com', 'www.youtube.com'} else ''
            if not re.fullmatch(r'[A-Za-z0-9_-]{11}', video_id):
                raise ValueError('Usa una URL de YouTube watch?v= o youtu.be válida')
            media = f'<div class="video-container"><button type="button" data-video-embed="https://www.youtube-nocookie.com/embed/{video_id}?rel=0" data-video-title="{e(d["title"])}"><span class="play-symbol">▶</span>Reproducir demo en YouTube</button></div>'
        demo_html += f'<article class="card">{media}<div class="card-body"><p class="eyebrow">{e(d["project"])}</p><h2 class="demo-title">{e(d["title"])}</h2><p>{e(d["description"])}</p><p class="demo-caption">{e(d["caption"])}</p><a href="{href("demos/index.html", route)}">Ver el recorrido →</a></div></article>'
    options = ''.join(f'<option value="{e(a)}">{e(a)}</option>' for a in sorted({p['area'] for p in projects}))
    payload = json.dumps({'projects': projects}, ensure_ascii=False).replace('<', '\\u003c')
    visual = f'''<aside class="hero-note" aria-label="Índice del portafolio"><div class="note-top"><span>PORTAFOLIO / 2026</span><span>MG—01</span></div><p class="note-claim">Trabajo en la intersección de <em>datos, software y operación.</em></p><a class="note-row" href="informes/index.html"><span>01 / Análisis</span><strong>{len(analysis):02d} proyectos ↗</strong></a><a class="note-row" href="#proyectos"><span>02 / Aplicaciones</span><strong>{len(projects)-len(analysis):02d} proyectos ↗</strong></a><a class="note-row" href="demos/index.html"><span>03 / Demos</span><strong>{len(demos):02d} recorridos ↗</strong></a><p class="note-foot">Métodos, resultados y límites: cada proyecto documenta su propio recorrido.</p></aside>'''
    body = f'''<main id="contenido"><section class="container hero"><div><p class="eyebrow">Portafolio · Ciencia de datos e IA</p><h1>{e(PROFILE['headline'])}</h1><p class="lead">{e(PROFILE['description'])}</p><div class="actions"><a class="button" href="#proyectos">Explorar proyectos ↗</a><a class="button secondary" href="informes/index.html">Leer los informes</a></div></div>{visual}</section><div class="container stat-row"><div class="stat"><strong>{len(analysis)}</strong><span>proyectos de análisis</span></div><div class="stat"><strong>{themes}</strong><span>áreas de exploración</span></div><div class="stat"><strong>{len(projects)-len(analysis)}</strong><span>aplicaciones y MVP</span></div></div><section class="container section"><div class="section-head"><div><p class="eyebrow">01 / Selección de proyectos</p><h2>Proyectos destacados</h2></div><p>Distintas preguntas, métodos y resultados. Cada proyecto conserva su evidencia y sus límites.</p></div><div class="grid featured-grid">{featured}</div></section><section class="catalog-section" id="proyectos"><div class="container section"><div class="section-head"><div><p class="eyebrow">02 / Archivo de proyectos</p><h2>Explora por pregunta o área</h2></div><p>De los notebooks a las aplicaciones: documentación propia y resultados consultables.</p></div><div class="filters"><div class="family-tabs" aria-label="Línea de proyectos"><button class="filter-button" data-family="all" aria-pressed="true">Todos</button><button class="filter-button" data-family="analisis" aria-pressed="false">Análisis</button><button class="filter-button" data-family="bi" aria-pressed="false">Business Intelligence</button><button class="filter-button" data-family="iag" aria-pressed="false">IA y MVP</button></div><div class="filter-fields"><div class="field"><label for="project-search">Buscar</label><input id="project-search" type="search" placeholder="Proyecto, tema o técnica"></div><div class="field"><label for="project-area">Área</label><select id="project-area"><option value="all">Todas las áreas</option>{options}</select></div><button class="reset" id="reset-filters">Limpiar filtros</button></div></div><p class="results-info" id="results-info" role="status">{len(projects)} proyectos</p><noscript><p class="noscript">Se muestran todos los proyectos. Activa JavaScript para usar los filtros.</p></noscript><div class="grid" id="project-grid">{''.join(card(p) for p in projects)}</div><p class="empty" id="empty-results" hidden>No hay proyectos que coincidan. Prueba otra búsqueda o limpia los filtros.</p><div class="more"><button class="button secondary" id="load-more" hidden>Mostrar más proyectos</button></div></div></section><section class="container section"><div class="report-callout"><div><p class="eyebrow">03 / Evidencia y resultados</p><h2>La conclusión también forma parte del proyecto.</h2><p>Consulta los informes integrales: metodología, métricas, alertas y limitaciones de cada análisis.</p></div><a class="button" href="informes/index.html">Consultar informes →</a></div></section><section class="container section about"><div><p class="eyebrow">06 / Perfil y contacto</p><h2>Aprender, construir y documentar.</h2></div><div><p class="lead">{e(PROFILE['about'])}</p><div class="contact-links"><a href="{e(PROFILE['github_url'])}">Ver mi perfil en GitHub ↗</a></div></div></section></main><script id="portfolio-data" type="application/json">{payload}</script>'''
    if PROFILE.get('name'):
        identity = f'<p class="eyebrow">{e(PROFILE["name"])}</p><p class="profile-role">{e(PROFILE.get("role", "Ciencia de datos e IA"))}</p>'
        body = body.replace('<p class="eyebrow">Portafolio · Ciencia de datos e IA</p>', identity, 1)
    body = body.replace('<section class="container section about">', profile_sections() + '<section class="container section about">', 1)
    body = body.replace('Aprender, construir y documentar.', 'Conectar datos con necesidades reales.', 1)
    body = body.replace(f'<div class="contact-links"><a href="{e(PROFILE["github_url"])}">Ver mi perfil en GitHub ↗</a></div>', f'<div class="contact-links">{contact_links()}</div>', 1)
    write('index.html', shell(PROFILE.get('name') or 'Ciencia de datos e IA', body, script=True))
    demos_body = f'<main class="container document demos-page" id="contenido"><div class="document-hero"><p class="eyebrow">Aplicaciones en práctica</p><h1>Demos de los MVP</h1><p class="lead">Explora capturas de consultas ejecutadas con ejemplos ficticios y su recorrido documentado. Cada demo explica su alcance actual.</p></div><div class="grid">{demo_html}</div></main>'
    write('demos/index.html', shell('Demos', demos_body, 'demos/index.html', script='assets/demos.js'))
    reports = [p for p in projects if p['report']]
    report_groups = ''
    report_buttons = '<button class="filter-button" data-report-family="all" aria-pressed="true">Todos</button>'
    for family, label in [('analisis', 'Análisis'), ('bi', 'Business Intelligence'), ('iag', 'IA y MVP')]:
        group = [p for p in reports if p['family'] == family]
        report_buttons += f'<button class="filter-button" data-report-family="{family}" aria-pressed="false">{label} ({len(group)})</button>'
        listing = ''.join(f'<li><div><a href="{href("informes/index.html", p["report"])}">{e(p["name"])}</a><small>{e(p["area"])} · {e(p["status"])}</small></div><span>→</span></li>' for p in group)
        if listing:
            content = f'<ul class="report-list">{listing}</ul>'
        else:
            docs = ''.join(f'<li><a href="{href("informes/index.html", p["page"])}">{e(p["name"])} →</a></li>' for p in projects if p['family'] == family)
            content = f'<div class="report-empty"><p>Aún no hay informes integrales disponibles en esta línea.</p><p>Puedes consultar la documentación de sus proyectos:</p><ul>{docs}</ul></div>'
        report_groups += f'<section class="report-group" data-report-group="{family}" data-report-count="{len(group)}"><h2>{label}</h2>{content}</section>'
    reports_body = f'<main class="container document" id="contenido"><div class="document-hero"><p class="eyebrow">Evidencia y límites</p><h1>Informes por tipo de proyecto</h1><p class="lead">Consulta los informes disponibles en cada línea. Los resultados pertenecen a fuentes y protocolos distintos; sus métricas no son directamente comparables.</p></div><div class="family-tabs" aria-label="Tipo de informe">{report_buttons}</div><p id="report-results" class="results-info" role="status">{len(reports)} informes disponibles</p><noscript><p class="noscript">Se muestran las tres líneas. Activa JavaScript para filtrarlas.</p></noscript>{report_groups}</main>'
    write('informes/index.html', shell('Informes por tipo', reports_body, 'informes/index.html', script='assets/reports.js'))
    done = set()
    while len(done) < len(pending):
        source = next(s for s in pending if s not in done)
        current = pending[source]
        title = source.parent.parent.parent.name if current.parts[0] == 'informes' else source.parent.name if source.name == 'README.md' else source.stem.replace('_', ' ')
        content = markdown(source, current)
        source_link = f'<a href="{REPO}/blob/{quote(BRANCH, safe="")}/{quote(source.relative_to(ROOT).as_posix(), safe="/")}">Documento en GitHub ↗</a>' if REPO else ''
        navigation = document_navigation(source, current)
        body = f'<main class="container document" id="contenido"><div class="breadcrumbs"><a href="{href(current, "index.html")}">Portafolio</a> / {e(title)}</div>{navigation}<div class="document-actions">{source_link}</div><article class="reading">{content}</article>{navigation}</main>'
        write(current, shell(title, body, current.as_posix(), script='assets/navigation.js'))
        done.add(source)
    for source, (current, original) in evidence_pages.items():
        navigation = document_navigation(source, current)
        download = f'<div class="document-actions"><a href="{href(current, original)}" download>Descargar {e(source.name)}</a></div>'
        body = f'<main class="container document" id="contenido">{navigation}{download}<article class="reading">{evidence_content(source)}</article>{navigation}</main>'
        write(current, shell(source.name, body, current.as_posix(), script='assets/navigation.js'))
    write('catalogo.json', json.dumps({'projects': projects}, ensure_ascii=False, indent=2))
    write('build-summary.json', json.dumps({'projects': len(projects), 'analyses': len(analysis), 'themes': themes, 'reports': len(reports), 'documents': len(done), 'evidence_pages': len(evidence_pages), 'evidence_files': len(assets), 'repository_links': bool(REPO)}, indent=2))
    print((OUT / 'build-summary.json').read_text())


if __name__ == '__main__':
    build()
