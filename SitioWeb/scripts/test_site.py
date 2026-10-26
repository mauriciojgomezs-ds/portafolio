"""Checks for unsafe links, data exposure and Markdown conversion."""
import tempfile
import unittest
from pathlib import Path
import build_site as site


class PublicationTests(unittest.TestCase):
    def test_stage_navigation_stays_with_its_project(self):
        original = site.project_roots.copy()
        try:
            for name in ['BankChurn', 'TelecomChurn']:
                site.project_roots[(site.ROOT / 'Analisis/churn' / name).resolve()] = dict(folder=name, page=f'proyectos/{name.lower()}/index.html', report=f'informes/{name.lower()}/index.html')
            source = site.ROOT / 'Analisis/churn/BankChurn/reports/eda/eda.json'
            current = 'documentos/Analisis/churn/BankChurn/reports/eda/eda.json.html'
            rendered = site.document_navigation(source, current)
            self.assertIn('Volver al informe de BankChurn', rendered)
            self.assertIn('informes/bankchurn/index.html', rendered)
            self.assertNotIn('telecomchurn', rendered)
        finally:
            site.project_roots.clear()
            site.project_roots.update(original)

    def test_evidence_preview_escapes_html_and_limits_long_files(self):
        with tempfile.TemporaryDirectory(dir=site.SITE / 'docs') as directory:
            source = Path(directory) / 'evidence.json'
            source.write_text('{"message": "<script>alert(1)</script>", "rows": ' + str(list(range(300))) + '}', encoding='utf-8')
            rendered = site.evidence_content(source)
            self.assertNotIn('<script>', rendered)
            self.assertIn('&lt;script&gt;', rendered)
            self.assertIn('Vista previa limitada', rendered)

    def test_professional_profile_preserves_training_status(self):
        rendered = site.profile_sections()
        self.assertIn('Egresado.', rendered)
        self.assertIn('Diplomado en Data Science', rendered)
        self.assertIn('Mi recorrido', rendered)
        self.assertIn('mailto:', site.contact_links())

    def test_project_data_and_secrets_are_excluded(self):
        for path in ['back/source.zip', 'Analisis/churn/BankChurn/data/raw/input.csv', 'IAG/DataCopilot/.env', 'SitioWeb/.venv/config.json', 'Analisis/churn/BankChurn/reports/runs/run.json']:
            self.assertFalse(site.public(site.ROOT / path), path)
        self.assertFalse(site.public(site.ROOT.parent / 'private.md'))

    def test_unsafe_urls_cannot_be_rendered(self):
        source = site.ROOT / 'README.md'
        for url in ['javascript:alert(1)', 'file:///C:/private.txt', '//outside.example/file', 'data:text/html,hello']:
            self.assertIsNone(site.rewrite_url(url, source, 'index.html'))

    def test_raw_html_is_escaped_and_relative_links_are_rebased(self):
        with tempfile.TemporaryDirectory(dir=site.SITE / 'docs') as directory:
            source = Path(directory) / 'example.md'
            source.write_text('# Evidencia\n\n<script>alert(1)</script>\n\n[Proyecto](../../../Analisis/Regression/PowerPlantRegression/README.md)', encoding='utf-8')
            rendered = site.markdown(source, 'documentos/example.html')
            self.assertNotIn('<script>', rendered)
            self.assertIn('&lt;script&gt;', rendered)
            self.assertIn('href="', rendered)
            self.assertNotIn('href="/', rendered)

    def test_github_fallback_includes_repository_branch_and_source(self):
        original = site.REPO
        try:
            site.REPO = 'https://github.com/example/portfolio'
            value = site.rewrite_url('SitioWeb/requirements.txt', site.ROOT / 'README.md', 'index.html')
            self.assertEqual(value, f'https://github.com/example/portfolio/blob/{site.BRANCH}/SitioWeb/requirements.txt')
        finally:
            site.REPO = original


if __name__ == '__main__':
    unittest.main()
