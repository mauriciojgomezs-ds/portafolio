import copy
import io
import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from app.providers import ProviderError, ask_openai, parse_response
from app.questions import prepare, validate_answer
from ask import run


class MeetingQuestionsTests(unittest.TestCase):
    def setUp(self):
        self.transcript = json.loads((ROOT / "examples/transcript.json").read_text(encoding="utf-8"))
        self.agenda = json.loads((ROOT / "examples/agenda.json").read_text(encoding="utf-8"))
        self.context = prepare("¿Cuál fue el presupuesto final?", self.transcript, self.agenda)[1]
        self.answer = {"status": "answered", "claims": [{"text": "Se aprobó un máximo de 3.200.000 pesos chilenos.", "citations": [{"segment_id": "S07", "quote": "Queda aprobado un máximo de 3.200.000 pesos chilenos para el piloto, sin incluir soporte posterior."}]}], "limitations": []}

    def test_short_meeting_keeps_corrections_and_does_not_load_references(self):
        self.assertEqual(self.context["context_scope"], "full")
        self.assertIn("S20", {segment["id"] for segment in self.context["segments"]})
        self.assertEqual(self.context["gaps"][0]["id"], "G1")
        self.assertNotIn("expected_answer", json.dumps(self.context))
        self.assertNotIn("synthetic_reference", json.dumps(self.context))

    def test_local_search_returns_candidates_without_claiming_generation(self):
        with patch("ask.ask_openai") as provider:
            result = run("¿Cuál fue el presupuesto final aprobado?", self.transcript)
        provider.assert_not_called()
        self.assertEqual(result["mode"], "retrieval_only")
        self.assertNotIn("answer", result)
        self.assertIn("S07", {segment["id"] for segment in result["candidates"]})

    def test_valid_answer_adds_real_times_and_speaker(self):
        result = validate_answer(self.answer, self.context)
        citation = result["claims"][0]["citations"][0]
        self.assertEqual(citation["speaker"], "Ana")
        self.assertEqual(citation["start_seconds"], 245)

    def test_fabricated_quote_is_not_published(self):
        self.answer["claims"][0]["citations"][0]["quote"] = "Se aprobó un presupuesto de 9.000.000."
        with patch("ask.ask_openai", return_value=(self.answer, {"provider": "openai"})):
            with self.assertRaisesRegex(ValueError, "literalmente"):
                run("¿Cuál fue el presupuesto?", self.transcript, provider="openai", model="test-model")

    def test_citations_must_belong_to_context_sent(self):
        context = copy.deepcopy(self.context)
        context["segments"] = [segment for segment in context["segments"] if segment["id"] != "S07"]
        with self.assertRaisesRegex(ValueError, "fuera del contexto"):
            validate_answer(self.answer, context)

    def test_abstention_can_have_no_claims_but_requires_explanation(self):
        answer = {"status": "insufficient_evidence", "claims": [], "limitations": ["Falta el fragmento dedicado al plan de pruebas."]}
        self.assertEqual(validate_answer(answer, self.context)["status"], "insufficient_evidence")
        answer["limitations"] = []
        with self.assertRaisesRegex(ValueError, "explicación"):
            validate_answer(answer, self.context)

    def test_context_limit_stops_before_network(self):
        with patch("ask.ask_openai") as provider:
            with self.assertRaisesRegex(ValueError, "supera el límite"):
                run("presupuesto", self.transcript, provider="openai", max_chars=100)
        provider.assert_not_called()

    def test_wrong_meeting_agenda_is_rejected(self):
        self.agenda["meeting_id"] = "otra-reunion"
        with self.assertRaisesRegex(ValueError, "distintas"):
            prepare("presupuesto", self.transcript, self.agenda)

    def test_missing_credentials_never_calls_network(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "", "OPENAI_MODEL": ""}), patch("app.providers.urllib.request.urlopen") as network:
            with self.assertRaisesRegex(ProviderError, "OPENAI_API_KEY"):
                ask_openai(self.context)
        network.assert_not_called()

    def test_provider_request_schema_and_response_parsing(self):
        response = {"status": "completed", "id": "test-response", "model": "test-model", "usage": {"total_tokens": 10}, "output": [{"type": "message", "content": [{"type": "output_text", "text": json.dumps(self.answer)}]}]}
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-placeholder", "OPENAI_MODEL": "test-model"}), patch("app.providers.urllib.request.urlopen") as network:
            network.return_value.__enter__.return_value = io.BytesIO(json.dumps(response).encode())
            answer, metadata = ask_openai(self.context)
        request = network.call_args.args[0]
        payload = json.loads(request.data)
        self.assertEqual(request.full_url, "https://api.openai.com/v1/responses")
        self.assertFalse(payload["store"])
        self.assertTrue(payload["text"]["format"]["strict"])
        self.assertEqual(payload["text"]["format"]["type"], "json_schema")
        self.assertNotIn("test-placeholder", request.data.decode())
        self.assertEqual(answer, self.answer)
        self.assertEqual(metadata["usage"]["total_tokens"], 10)

    def test_incomplete_and_refused_provider_responses_are_not_answers(self):
        with self.assertRaises(ProviderError):
            parse_response({"status": "incomplete", "output": []})
        with self.assertRaises(ProviderError):
            parse_response({"status": "completed", "output": [{"type": "message", "content": [{"type": "refusal", "refusal": "No"}]}]})


if __name__ == "__main__":
    unittest.main()
