import io
import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.llm import request_json


class ProviderContractTests(unittest.TestCase):
    def test_structured_request_and_response_without_live_call(self):
        response = {"status": "completed", "output": [{"type": "message", "content": [{"type": "output_text", "text": '{"value": "demo"}'}]}]}
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-placeholder", "OPENAI_MODEL": "test-model"}), patch("app.llm.urllib.request.urlopen") as network:
            network.return_value.__enter__.return_value = io.BytesIO(json.dumps(response).encode())
            result = request_json("instructions", {"example": "data"}, {"type": "object"})
        self.assertEqual(result, {"value": "demo"})
        payload = json.loads(network.call_args.args[0].data)
        self.assertFalse(payload["store"])
        self.assertTrue(payload["text"]["format"]["strict"])
        self.assertNotIn("test-placeholder", network.call_args.args[0].data.decode())

    def test_incomplete_provider_response_is_rejected(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-placeholder", "OPENAI_MODEL": "test-model"}), patch("app.llm.urllib.request.urlopen") as network:
            network.return_value.__enter__.return_value = io.BytesIO(b'{"status":"incomplete"}')
            with self.assertRaisesRegex(RuntimeError, "incompleta"):
                request_json("instructions", {}, {})
