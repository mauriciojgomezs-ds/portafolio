import io
import sqlite3
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

import main
from db import SCHEMA
from live_discovery import build_discovery_queries, discover_candidate_urls, fallback_urls
from retrieval import intent_profile, make_simple_answer
from scraper import ScrapedPage


class GenericSourcesTests(unittest.TestCase):
    def test_generic_discovery_uses_configured_domain_without_seeds(self):
        question = "Cómo configurar seguimiento web"
        queries = build_discovery_queries(question, "https://docs.example.org/guide/", tag="docs")
        self.assertTrue(all(query.startswith("site:docs.example.org/guide/") for query in queries))
        self.assertEqual(fallback_urls(question, tag="docs"), [])
        with patch("live_discovery.search_duckduckgo", return_value=["https://docs.example.org/guide/tracking"]) as search:
            urls = discover_candidate_urls(question, base_url="https://docs.example.org/guide/", tag="docs")
        self.assertEqual(urls, ["https://docs.example.org/guide/tracking"])
        self.assertEqual(search.call_args.kwargs["allowed_domain"], "docs.example.org")

    def test_live_query_without_source_stops_before_discovery(self):
        args = main.build_parser().parse_args(["ask-live", "configurar seguimiento web"])
        with patch("main.discover_candidate_urls") as discovery, redirect_stderr(io.StringIO()) as output:
            with self.assertRaises(SystemExit) as exit_info:
                main.cmd_ask_live(args)
        self.assertEqual(exit_info.exception.code, 1)
        self.assertIn("--tag", output.getvalue())
        discovery.assert_not_called()

    def test_live_query_passes_registered_source_to_discovery(self):
        conn = sqlite3.connect(":memory:")
        self.addCleanup(conn.close)
        conn.row_factory = sqlite3.Row
        conn.executescript(SCHEMA)
        conn.execute("INSERT INTO sources(tag, base_url) VALUES (?, ?)", ("docs", "https://docs.example.org/"))
        conn.commit()
        url = "https://docs.example.org/tracking"
        page = ScrapedPage(url, "Seguimiento web", "docs.example.org", "Configuración y validación del seguimiento web con eventos y reglas de acción.", "hash-demo", 200, "text/html", [])
        args = main.build_parser().parse_args(["ask-live", "configurar seguimiento web", "--tag", "docs", "--depth", "0"])
        with patch("main.connect", return_value=conn), patch("main.discover_candidate_urls", return_value=[url]) as discovery, patch("main.scrape_url", return_value=page), redirect_stdout(io.StringIO()) as output:
            main.cmd_ask_live(args)
        self.assertEqual(discovery.call_args.kwargs["base_url"], "https://docs.example.org/")
        self.assertEqual(discovery.call_args.kwargs["tag"], "docs")
        self.assertIn(url, output.getvalue())
        self.assertEqual(conn.execute("SELECT source_tag FROM documents").fetchone()[0], "docs")

    def test_generic_action_rules_have_no_product_specific_ui_paths(self):
        question = "Cómo configurar reglas de acción"
        self.assertEqual(intent_profile(question)["intent"], "web_tracking_action_rules")
        docs = [{"title": "Reglas de acción", "url": "https://docs.example.org/actions", "clean_text": "Configurar reglas de acción requiere revisar permisos y validar los eventos de seguimiento web."}]
        answer = make_simple_answer(question, docs, [], [])
        self.assertIn("Guía orientativa", answer)
        self.assertIn("canal de mensajería", answer)
        self.assertNotIn("Admin >", answer)


if __name__ == "__main__":
    unittest.main()
