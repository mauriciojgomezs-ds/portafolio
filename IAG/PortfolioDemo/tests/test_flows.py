"""Verifica la conexión con los tres motores y un CSV distinto a la demo."""
import base64
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("portfolio_server", ROOT / "scripts/serve.py")
server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server)


class Flows(unittest.TestCase):
    def test_data_uses_uploaded_csv(self):
        content = "region,ventas\nNorte,7\nNorte,5\nSur,3\n"
        record = server.query({"project": "data", "question": "total de ventas por region", "files": [{"name": "ventas.csv", "content": base64.b64encode(content.encode()).decode()}]})
        self.assertEqual({key: float(value) for key, value in record["result"]["result"]["value"].items()}, {"Norte": 12, "Sur": 3})
        self.assertTrue((server.RUNS / record["run_id"] / "conversation.json").exists())

    def test_documents_execute_validation(self):
        record = server.query({"project": "documents", "question": "Revisar las facturas y sus importes"})
        self.assertEqual(float(record["result"]["summary"]["validated_total_by_currency"]["CLP"]), 119000)
        self.assertEqual(len(record["result"]["documents"]), 4)

    def test_meetings_returns_evidence(self):
        record = server.query({"project": "meetings", "question": "¿Cuál fue el presupuesto final aprobado?"})
        self.assertEqual(record["result"]["mode"], "retrieval_only")
        self.assertIn("S20", [item["id"] for item in record["result"]["candidates"]])

    def test_rejects_unsupported_requests(self):
        for body in ([], {"project": "other", "question": "hola"}, {"project": "documents", "question": "hola", "provider": "openai"}):
            with self.subTest(body=body), self.assertRaises(ValueError):
                server.query(body)


if __name__ == "__main__":
    unittest.main()
