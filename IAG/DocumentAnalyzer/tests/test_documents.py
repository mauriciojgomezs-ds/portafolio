import copy
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.documents import amount, convert, extract_rules, summarize, validate_fields, validate_invoice


class DocumentTests(unittest.TestCase):
    def record(self, name):
        document = convert(ROOT / "examples" / name)
        fields = validate_fields(document, extract_rules(document))
        return {"document": document, "fields": fields, "validation": validate_invoice(fields)}

    def test_valid_invoice(self):
        record = self.record("factura_001.md")
        self.assertEqual(record["validation"]["issues"], [])
        self.assertEqual(record["validation"]["amounts"]["total"], "119000")

    def test_discrepancy_is_not_silently_corrected(self):
        record = self.record("factura_002_error.md")
        self.assertIn("total_mismatch", record["validation"]["issues"])
        self.assertEqual(record["validation"]["total_discrepancy"], "500")

    def test_missing_tax_remains_unknown(self):
        record = self.record("factura_003_faltante.md")
        self.assertIsNone(record["fields"]["tax"])
        self.assertIsNone(record["validation"]["total_discrepancy"])

    def test_duplicates_and_invalid_documents_are_excluded(self):
        records = [self.record(path.name) for path in sorted((ROOT / "examples").glob("*.md"))]
        summary = summarize(records)
        self.assertEqual(summary["validated_total_by_currency"], {"CLP": "119000"})
        self.assertEqual(summary["included_count"], 1)
        self.assertEqual(records[-1]["duplicate_of"], "factura_001.md")

    def test_fabricated_field_is_rejected(self):
        record = self.record("factura_001.md")
        record["fields"]["total"]["value"] = "999.000"
        with self.assertRaises(ValueError):
            validate_fields(record["document"], record["fields"])

    def test_amount_convention_rejects_ambiguous_format(self):
        self.assertEqual(str(amount("1.234,50")), "1234.50")
        for value in ("NaN", "1,234.50", "1.23", "mil"):
            with self.assertRaises(ValueError):
                amount(value)

    def test_ocr_contract_preserves_page_and_recognition(self):
        engine = MagicMock()
        engine.predict.return_value = [types.SimpleNamespace(json={"res": {"page_index": 0, "rec_texts": ["Total: 119.000"], "rec_scores": [0.98]}})]
        module = types.SimpleNamespace(PaddleOCR=MagicMock(return_value=engine))
        with patch.dict(sys.modules, {"paddleocr": module}):
            document = convert(ROOT / "examples/factura_imagen.png")
        self.assertEqual(document["method"], "paddleocr")
        self.assertEqual(document["pages"][0]["page"], 1)
        self.assertEqual(document["pages"][0]["ocr_details"]["rec_scores"], [0.98])

    def test_markitdown_contract_uses_local_conversion_without_plugins(self):
        from app import documents
        instance = MagicMock()
        instance.convert_local.return_value = types.SimpleNamespace(markdown="Total: 119.000")
        factory = MagicMock(return_value=instance)
        with patch.dict(sys.modules, {"markitdown": types.SimpleNamespace(MarkItDown=factory)}), patch.object(Path, "read_bytes", return_value=b"fake-pdf"):
            document = convert(Path("example.pdf"))
        factory.assert_called_once_with(enable_plugins=False)
        instance.convert_local.assert_called_once_with("example.pdf")
        self.assertEqual(document["pages"][0]["page"], None)


if __name__ == "__main__":
    unittest.main()
