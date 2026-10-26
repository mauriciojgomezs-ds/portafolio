import argparse
import sys
import time
from collections import deque
from pathlib import Path
from urllib.parse import urlparse

from db import connect, init_db, DEFAULT_DB
from scraper import scrape_url
from retrieval import search_documents, search_documents_by_urls, search_validated_qa, search_error_cases, make_simple_answer
from live_discovery import discover_candidate_urls, score_related_link, required_urls_for_question



def get_source(conn, tag: str | None):
    if not tag:
        return None
    return conn.execute("SELECT * FROM sources WHERE tag = ?", (tag,)).fetchone()


def cmd_source_add(args):
    init_db(Path(args.db))
    with connect(Path(args.db)) as conn:
        conn.execute(
            """
            INSERT INTO sources(tag, base_url, include_pattern, exclude_pattern, notes)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(tag) DO UPDATE SET
                base_url=excluded.base_url,
                include_pattern=excluded.include_pattern,
                exclude_pattern=excluded.exclude_pattern,
                notes=excluded.notes
            """,
            (args.tag, args.url, args.include, args.exclude, args.notes),
        )
    print(f"Origen registrado: {args.tag} -> {args.url}")


def cmd_source_list(args):
    init_db(Path(args.db))
    with connect(Path(args.db)) as conn:
        rows = conn.execute("SELECT tag, base_url, include_pattern, exclude_pattern, notes FROM sources ORDER BY tag").fetchall()
    if not rows:
        print("No hay orígenes registrados. Usa `source-add`.")
        return
    for r in rows:
        print(f"- {r['tag']}: {r['base_url']} include={r['include_pattern'] or '*'} exclude={r['exclude_pattern'] or '-'}")
        if r['notes']:
            print(f"  {r['notes']}")

def upsert_page(conn, page, source_tag: str | None = None):
    existing = conn.execute("SELECT id, current_hash FROM documents WHERE url = ?", (page.url,)).fetchone()

    if existing is None:
        cur = conn.execute(
            """
            INSERT INTO documents(url, source_tag, title, domain, last_checked_at, current_hash, status_code, content_type)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, ?, ?, ?)
            """,
            (page.url, source_tag, page.title, page.domain, page.content_hash, page.status_code, page.content_type),
        )
        doc_id = cur.lastrowid
        changed = True
        old_hash = None
    else:
        doc_id = existing["id"]
        old_hash = existing["current_hash"]
        changed = old_hash != page.content_hash
        conn.execute(
            """
            UPDATE documents
            SET source_tag = COALESCE(?, source_tag), title = ?, domain = ?, last_checked_at = CURRENT_TIMESTAMP,
                current_hash = ?, status_code = ?, content_type = ?
            WHERE id = ?
            """,
            (source_tag, page.title, page.domain, page.content_hash, page.status_code, page.content_type, doc_id),
        )

    if changed:
        cur = conn.execute(
            """
            INSERT INTO document_versions(document_id, title, clean_text, content_hash)
            VALUES (?, ?, ?, ?)
            """,
            (doc_id, page.title, page.clean_text, page.content_hash),
        )
        version_id = cur.lastrowid
        conn.execute(
            """
            INSERT INTO document_fts(title, clean_text, url, document_id, version_id)
            VALUES (?, ?, ?, ?, ?)
            """,
            (page.title, page.clean_text, page.url, doc_id, version_id),
        )
        if old_hash is not None:
            conn.execute(
                """
                INSERT INTO change_log(document_id, old_hash, new_hash, summary)
                VALUES (?, ?, ?, ?)
                """,
                (doc_id, old_hash, page.content_hash, "Contenido limpio cambió. Revisar diff semántico en una versión futura."),
            )
    return doc_id, changed


def cmd_init(args):
    init_db(Path(args.db))
    print(f"Base inicializada: {args.db}")


def cmd_ingest_url(args):
    with connect(Path(args.db)) as conn:
        page = scrape_url(args.url)
        doc_id, changed = upsert_page(conn, page, getattr(args, "tag", None))
        print(f"OK: {page.title}")
        print(f"URL: {page.url}")
        print(f"Documento ID: {doc_id}")
        print(f"Hash: {page.content_hash}")
        print(f"Cambió: {'sí' if changed else 'no'}")


def should_crawl_link(url: str, allowed_domain: str, include: str = "", exclude: str = "") -> bool:
    parsed = urlparse(url)
    if parsed.netloc != allowed_domain:
        return False
    if include and include not in url:
        return False
    if exclude and exclude in url:
        return False
    return True


def cmd_crawl(args):
    """Crawling controlado: parte desde una o más URLs y sigue enlaces internos."""
    seeds = []
    for item in args.urls:
        p = Path(item)
        if p.exists():
            seeds.extend([line.strip() for line in p.read_text(encoding="utf-8").splitlines() if line.strip() and not line.startswith("#")])
        else:
            seeds.append(item)

    if not seeds:
        print("No hay URLs semilla para rastrear.", file=sys.stderr)
        sys.exit(1)

    first_domain = urlparse(seeds[0]).netloc
    queue = deque((url, 0) for url in seeds)
    seen = set()
    saved = 0

    with connect(Path(args.db)) as conn:
        while queue and saved < args.max_pages:
            url, depth = queue.popleft()
            if url in seen:
                continue
            seen.add(url)

            if not should_crawl_link(url, first_domain, args.include, args.exclude):
                continue

            try:
                page = scrape_url(url)
                _, changed = upsert_page(conn, page, getattr(args, "tag", None))
                saved += 1
                print(f"OK depth={depth} {'[nuevo/cambio]' if changed else '[sin cambio]'} {url}")

                if depth < args.depth:
                    for link in page.links:
                        if link not in seen and should_crawl_link(link, first_domain, args.include, args.exclude):
                            queue.append((link, depth + 1))

                if args.delay > 0:
                    time.sleep(args.delay)

            except Exception as exc:
                print(f"ERROR {url}: {exc}")

    print(f"\nResumen: páginas revisadas/guardadas={saved}, URLs vistas={len(seen)}, pendientes={len(queue)}")


def cmd_ingest_file(args):
    path = Path(args.file)
    if not path.exists():
        print(f"No existe el archivo: {path}", file=sys.stderr)
        sys.exit(1)

    urls = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip() and not line.startswith("#")]
    with connect(Path(args.db)) as conn:
        for url in urls:
            try:
                page = scrape_url(url)
                _, changed = upsert_page(conn, page, getattr(args, "tag", None))
                print(f"OK {'[nuevo/cambio]' if changed else '[sin cambio]'} {url}")
            except Exception as exc:
                print(f"ERROR {url}: {exc}")


def cmd_ask(args):
    with connect(Path(args.db)) as conn:
        validated = search_validated_qa(conn, args.question, limit=3)
        errors = search_error_cases(conn, args.question, limit=3)
        docs = search_documents(conn, args.question, limit=args.limit, tag=getattr(args, "tag", None))
        answer = make_simple_answer(args.question, docs, validated, errors)
        print(answer)
        if docs:
            print("\nFuentes candidatas:")
            for d in docs:
                print(f"- {d['url']}")


def cmd_ask_live(args):
    """Busca URLs primarias en la web, hace scraping dirigido y luego responde desde SQLite.

    Este modo es más lento que `ask`, pero sirve cuando la KB local no tiene el tema correcto.
    """
    t0 = time.perf_counter()
    
    if not args.tag:
        print("Indica un origen con --tag. Regístralo primero con source-add.", file=sys.stderr)
        sys.exit(1)
    with connect(Path(args.db)) as conn:
        source = get_source(conn, args.tag)
    if source is None:
        print(f"No existe el origen con tag '{args.tag}'. Regístralo con source-add.", file=sys.stderr)
        sys.exit(1)
    base_url = source["base_url"]
    include_pattern = args.include if args.include is not None else source["include_pattern"]
    exclude_pattern = args.exclude if args.exclude is not None else source["exclude_pattern"]
    discovered = discover_candidate_urls(args.question, limit=args.search_limit, base_url=base_url, include=include_pattern, tag=args.tag)
    # Agregar fuentes obligatorias por tema. Esto corrige casos donde la búsqueda
    # encuentra la configuración principal, pero omite componentes relacionados.
    for url in required_urls_for_question(args.question, tag=args.tag):
        if url not in discovered:
            discovered.append(url)
    t_discovery = time.perf_counter() - t0

    if args.verbose:
        print("URLs primarias candidatas:")
        for url in discovered:
            print(f"- {url}")
        print()

    saved = 0
    crawled = []
    related_queue = deque()
    seen = set()

    with connect(Path(args.db)) as conn:
        # 1) Ingerir candidatas primarias.
        for url in discovered:
            if saved >= args.max_pages:
                break
            if url in seen:
                continue
            seen.add(url)
            try:
                page = scrape_url(url)
                upsert_page(conn, page, getattr(args, "tag", None))
                saved += 1
                crawled.append(url)

                # 2) Encolar enlaces correlacionados desde la URL primaria.
                scored = []
                for link in page.links:
                    if include_pattern and include_pattern not in link:
                        continue
                    if exclude_pattern and exclude_pattern in link:
                        continue
                    score = score_related_link(args.question, link, page.title)
                    if score >= args.min_link_score:
                        scored.append((score, link))
                for _score, link in sorted(scored, reverse=True)[: args.related_per_page]:
                    related_queue.append((link, 1))
            except Exception as exc:
                if args.verbose:
                    print(f"ERROR URL primaria {url}: {exc}")

        # 3) Crawl controlado de enlaces relacionados.
        while related_queue and saved < args.max_pages:
            url, depth = related_queue.popleft()
            if url in seen or depth > args.depth:
                continue
            seen.add(url)
            try:
                page = scrape_url(url)
                upsert_page(conn, page, getattr(args, "tag", None))
                saved += 1
                crawled.append(url)

                if depth < args.depth:
                    scored = []
                    for link in page.links:
                        if include_pattern and include_pattern not in link:
                            continue
                        if exclude_pattern and exclude_pattern in link:
                            continue
                        score = score_related_link(args.question, link, page.title)
                        if score >= args.min_link_score:
                            scored.append((score, link))
                    for _score, link in sorted(scored, reverse=True)[: args.related_per_page]:
                        related_queue.append((link, depth + 1))

                if args.delay > 0:
                    time.sleep(args.delay)
            except Exception as exc:
                if args.verbose:
                    print(f"ERROR enlace relacionado {url}: {exc}")

        # 4) Responder usando la KB ya actualizada.
        validated = search_validated_qa(conn, args.question, limit=3)
        errors = search_error_cases(conn, args.question, limit=3)
        # En modo discover, primero respondemos con el contexto recién descubierto.
        # Esto evita contaminación entre temas dentro del mismo origen documental.
        docs = search_documents_by_urls(conn, args.question, crawled, limit=max(args.limit, 8))
        if not docs:
            docs = search_documents(conn, args.question, limit=args.limit, pool_size=max(20, args.limit * 5), tag=args.tag)

        # Forzar que fuentes obligatorias ingeridas aparezcan en el contexto final
        # si el ranking FTS no las seleccionó, especialmente referencias técnicas complementarias.
        must_have = required_urls_for_question(args.question, tag=args.tag)
        existing_urls = {d["url"] for d in docs}
        for url in must_have:
            if url in existing_urls:
                continue
            row = conn.execute(
                """
                SELECT title, clean_text, url, document_id, version_id, 0 AS score
                FROM document_fts
                WHERE url = ?
                ORDER BY version_id DESC
                LIMIT 1
                """,
                (url,),
            ).fetchone()
            if row is not None:
                docs.append(row)
                existing_urls.add(url)

        answer = make_simple_answer(args.question, docs, validated, errors)

    print(answer)
    print("\nURLs descubiertas/ingeridas en esta ejecución:")
    for url in crawled:
        print(f"- {url}")
    if docs:
        print("\nFuentes candidatas finales:")
        for d in docs:
            print(f"- {d['url']}")

    if args.timing:
        total = time.perf_counter() - t0
        print(f"\nTiempo discovery: {t_discovery:.3f} segundos")
        print(f"Tiempo ask-live total: {total:.3f} segundos")


def cmd_validate(args):
    with connect(Path(args.db)) as conn:
        cur = conn.execute(
            """
            INSERT INTO validated_qa(question, answer, sources, notes)
            VALUES (?, ?, ?, ?)
            """,
            (args.question, args.answer, args.sources, args.notes),
        )
        qa_id = cur.lastrowid
        conn.execute(
            """
            INSERT INTO validated_qa_fts(question, answer, sources, qa_id)
            VALUES (?, ?, ?, ?)
            """,
            (args.question, args.answer, args.sources, qa_id),
        )
        if args.successful_query:
            conn.execute(
                """
                INSERT INTO search_strategies(question, query, worked, notes)
                VALUES (?, ?, 1, ?)
                """,
                (args.question, args.successful_query, args.notes),
            )
        print(f"Respuesta validada guardada. QA ID: {qa_id}")


def cmd_mark_error(args):
    with connect(Path(args.db)) as conn:
        cur = conn.execute(
            """
            INSERT INTO error_cases(question, bad_answer, reason, better_query)
            VALUES (?, ?, ?, ?)
            """,
            (args.question, args.bad_answer, args.reason, args.better_query),
        )
        error_id = cur.lastrowid
        conn.execute(
            """
            INSERT INTO error_cases_fts(question, bad_answer, reason, better_query, error_id)
            VALUES (?, ?, ?, ?, ?)
            """,
            (args.question, args.bad_answer, args.reason, args.better_query, error_id),
        )
        if args.better_query:
            conn.execute(
                """
                INSERT INTO search_strategies(question, query, worked, notes)
                VALUES (?, ?, 0, ?)
                """,
                (args.question, args.better_query, args.reason),
            )
        print(f"Caso erróneo guardado. Error ID: {error_id}")


def cmd_check_changes(args):
    with connect(Path(args.db)) as conn:
        docs = conn.execute("SELECT url FROM documents ORDER BY id").fetchall()
        if not docs:
            print("No hay documentos para revisar.")
            return
        for row in docs:
            url = row["url"]
            try:
                page = scrape_url(url)
                _, changed = upsert_page(conn, page, getattr(args, "tag", None))
                print(f"{'CAMBIÓ' if changed else 'sin cambio'}: {url}")
            except Exception as exc:
                print(f"ERROR {url}: {exc}")


def cmd_stats(args):
    with connect(Path(args.db)) as conn:
        tables = ["documents", "document_versions", "validated_qa", "error_cases", "search_strategies", "change_log"]
        for t in tables:
            n = conn.execute(f"SELECT COUNT(*) AS n FROM {t}").fetchone()["n"]
            print(f"{t}: {n}")


def build_parser():
    parser = argparse.ArgumentParser(description="Asistente de investigación documental")
    parser.add_argument("--db", default=str(DEFAULT_DB), help="Ruta a SQLite")
    sub = parser.add_subparsers(required=True)


    p = sub.add_parser("source-add", help="Registrar o actualizar un origen documental")
    p.add_argument("--tag", required=True, help="Etiqueta corta del origen, por ejemplo docs")
    p.add_argument("--url", required=True, help="URL base del origen, por ejemplo https://docs.python.org/3/")
    p.add_argument("--include", default="", help="Patrón recomendado para seguir enlaces, por ejemplo /articles/")
    p.add_argument("--exclude", default="", help="Patrón para excluir enlaces")
    p.add_argument("--notes", default="")
    p.add_argument("--timing", action="store_true", help="Mostrar tiempo total del comando")
    p.set_defaults(func=cmd_source_add)

    p = sub.add_parser("source-list", help="Listar orígenes documentales registrados")
    p.add_argument("--timing", action="store_true", help="Mostrar tiempo total del comando")
    p.set_defaults(func=cmd_source_list)

    p = sub.add_parser("init", help="Inicializar base SQLite")
    p.add_argument("--timing", action="store_true", help="Mostrar tiempo total del comando")
    p.set_defaults(func=cmd_init)

    p = sub.add_parser("ingest-url", help="Cargar una URL")
    p.add_argument("url")
    p.add_argument("--tag", default=None, help="Etiqueta del origen documental")
    p.add_argument("--timing", action="store_true", help="Mostrar tiempo total del comando")
    p.set_defaults(func=cmd_ingest_url)

    p = sub.add_parser("ingest-file", help="Cargar URLs desde archivo")
    p.add_argument("file")
    p.add_argument("--tag", default=None, help="Etiqueta del origen documental")
    p.add_argument("--timing", action="store_true", help="Mostrar tiempo total del comando")
    p.set_defaults(func=cmd_ingest_file)

    p = sub.add_parser("crawl", help="Cargar una o más URLs y seguir enlaces internos con profundidad controlada")
    p.add_argument("urls", nargs="+", help="URLs semilla o archivos .txt con URLs")
    p.add_argument("--tag", default=None, help="Etiqueta del origen documental")
    p.add_argument("--depth", type=int, default=1, help="Profundidad de enlaces a seguir. 0 = solo semillas")
    p.add_argument("--max-pages", type=int, default=25, help="Límite total de páginas a revisar")
    p.add_argument("--delay", type=float, default=0.5, help="Pausa entre requests en segundos")
    p.add_argument("--include", default="", help="Solo seguir URLs que contengan este texto")
    p.add_argument("--exclude", default=None, help="No seguir URLs que contengan este texto")
    p.add_argument("--timing", action="store_true", help="Mostrar tiempo total del comando")
    p.set_defaults(func=cmd_crawl)

    p = sub.add_parser("ask", help="Preguntar sobre la KB local")
    p.add_argument("question")
    p.add_argument("--tag", default=None, help="Limitar la búsqueda a un origen documental")
    p.add_argument("--limit", type=int, default=5)
    p.add_argument("--timing", action="store_true", help="Mostrar tiempo total del comando")
    p.set_defaults(func=cmd_ask)

    p = sub.add_parser("ask-live", help="Buscar URL primaria, hacer scraping dirigido y responder")
    p.add_argument("question")
    p.add_argument("--tag", default=None, help="Origen documental a consultar, por ejemplo docs")
    p.add_argument("--discover", action="store_true", help="Permite exploración genérica cuando no hay playbook específico")
    p.add_argument("--limit", type=int, default=5, help="Cantidad de fuentes finales para usar en la respuesta")
    p.add_argument("--search-limit", type=int, default=6, help="Cantidad de URLs primarias candidatas")
    p.add_argument("--depth", type=int, default=1, help="Profundidad para seguir enlaces relacionados")
    p.add_argument("--max-pages", type=int, default=12, help="Máximo de páginas a ingerir en esta ejecución")
    p.add_argument("--related-per-page", type=int, default=8, help="Máximo de enlaces relacionados a seguir por página")
    p.add_argument("--min-link-score", type=float, default=2.0, help="Score mínimo de correlación para seguir un enlace")
    p.add_argument("--delay", type=float, default=0.3, help="Pausa entre requests en segundos")
    p.add_argument("--include", default=None, help="Solo seguir URLs que contengan este texto")
    p.add_argument("--exclude", default="", help="No seguir URLs que contengan este texto")
    p.add_argument("--verbose", action="store_true", help="Mostrar URLs candidatas y errores de búsqueda")
    p.add_argument("--timing", action="store_true", help="Mostrar tiempos de discovery y total")
    p.set_defaults(func=cmd_ask_live)

    p = sub.add_parser("validate", help="Guardar respuesta validada")
    p.add_argument("--question", required=True)
    p.add_argument("--answer", required=True)
    p.add_argument("--sources", default="")
    p.add_argument("--notes", default="")
    p.add_argument("--successful-query", default="")
    p.add_argument("--timing", action="store_true", help="Mostrar tiempo total del comando")
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("mark-error", help="Guardar caso erróneo")
    p.add_argument("--question", required=True)
    p.add_argument("--bad-answer", default="")
    p.add_argument("--reason", required=True)
    p.add_argument("--better-query", default="")
    p.add_argument("--timing", action="store_true", help="Mostrar tiempo total del comando")
    p.set_defaults(func=cmd_mark_error)

    p = sub.add_parser("check-changes", help="Revisar cambios en URLs guardadas")
    p.add_argument("--timing", action="store_true", help="Mostrar tiempo total del comando")
    p.set_defaults(func=cmd_check_changes)

    p = sub.add_parser("stats", help="Ver conteos")
    p.add_argument("--timing", action="store_true", help="Mostrar tiempo total del comando")
    p.set_defaults(func=cmd_stats)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    start = time.perf_counter()
    args.func(args)
    elapsed = time.perf_counter() - start
    if getattr(args, "timing", False) and getattr(args, "func", None) is not cmd_ask_live:
        print(f"\nTiempo total: {elapsed:.3f} segundos")



if __name__ == "__main__":
    main()
