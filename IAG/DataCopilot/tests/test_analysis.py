import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.analysis import execute, local_plan, number, profile, read_table
from app.llm import request_json


class AnalysisTests(unittest.TestCase):
    def setUp(self):
        self.columns, self.rows, _ = read_table(ROOT / "examples/ventas.csv")

    def test_reference_sum_declares_missing_and_invalid(self):
        result = execute(local_plan("total de ventas", self.columns), self.columns, self.rows)
        self.assertEqual(result["value"], "1680000")
        self.assertEqual(result["valid_rows"], 10)
        self.assertEqual(result["missing_line_numbers"], [8])
        self.assertEqual(result["invalid_line_numbers"], [9])

    def test_reference_group_totals(self):
        result = execute(local_plan("total de ventas por region", self.columns), self.columns, self.rows)
        self.assertEqual(result["value"], {"Centro": "310000", "Norte": "530000", "Sur": "840000"})

    def test_mean_uses_valid_values_and_keeps_duplicates(self):
        result = execute(local_plan("promedio de ventas", self.columns), self.columns, self.rows)
        self.assertEqual(result["value"], "168000")
        self.assertEqual(profile(self.columns, self.rows)["duplicate_rows"], 1)

    def test_rejects_unsupported_filters_without_ignoring_them(self):
        for question in ("total de ventas solo en Sur", "por qué bajaron las ventas", "promedio de ventas por region"):
            self.assertEqual(local_plan(question, self.columns)["operation"], "unsupported")

    def test_model_cannot_reference_unknown_columns_or_execute_code(self):
        for plan in ({"operation": "sum", "column": "secreto", "group_by": None}, {"operation": "exec", "column": None, "group_by": None}):
            with self.assertRaises(ValueError):
                execute(plan, self.columns, self.rows)

    def test_nan_infinity_and_thousands_are_not_numbers(self):
        for value in ("NaN", "Infinity", "1,000", "pendiente"):
            self.assertIsNone(number(value))

    def test_credentials_absent_do_not_trigger_network(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "", "OPENAI_MODEL": ""}), patch("app.llm.urllib.request.urlopen") as network:
            with self.assertRaises(RuntimeError):
                request_json("test", {}, {})
        network.assert_not_called()


if __name__ == "__main__":
    unittest.main()
