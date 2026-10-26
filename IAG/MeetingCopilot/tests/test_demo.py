import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from demo import ROOT, calculate, load, validate


class AgendaEvaluationTests(unittest.TestCase):
    def setUp(self):
        self.agenda = load(ROOT / "examples/agenda.json")
        self.transcript = load(ROOT / "examples/transcript.json")
        self.review = load(ROOT / "examples/reference_review.json")
        self.qa = load(ROOT / "examples/reference_qa.json")

    def test_reference_metrics_separate_missing_evidence(self):
        validate(self.agenda, self.transcript, self.review, self.qa)
        result = calculate(self.agenda, self.review)
        self.assertEqual(result["fulfillment_evaluable_pct"], 69.44)
        self.assertEqual(result["evaluable_weight_pct"], 90)
        self.assertEqual(result["coverage_known_weight_pct"], 83.33)
        self.assertEqual(result["coverage_known_count_pct"], 75)
        self.assertEqual(result["full_agenda_sensitivity_pct"], [62.5, 72.5])

    def test_all_unknown_is_not_zero_fulfillment(self):
        review = copy.deepcopy(self.review)
        for row in review["objectives"]:
            row.update(coverage="unknown", fulfillment="not_evaluable")
        validate(self.agenda, self.transcript, review, self.qa)
        result = calculate(self.agenda, review)
        self.assertIsNone(result["fulfillment_evaluable_pct"])
        self.assertIsNone(result["coverage_known_weight_pct"])
        self.assertEqual(result["evaluable_weight_pct"], 0)
        self.assertEqual(result["full_agenda_sensitivity_pct"], [0, 100])

    def test_discussion_does_not_imply_fulfillment(self):
        review = copy.deepcopy(self.review)
        review["objectives"][0]["fulfillment"] = "not_fulfilled"
        validate(self.agenda, self.transcript, review, self.qa)
        result = calculate(self.agenda, review)
        self.assertEqual(result["coverage_known_weight_pct"], 83.33)
        self.assertEqual(result["fulfillment_evaluable_pct"], 36.11)

    def test_fabricated_quote_is_rejected(self):
        self.review["objectives"][0]["evidence"][0]["quote"] = "Un acuerdo inventado que no aparece en la reunión."
        with self.assertRaisesRegex(ValueError, "cita"):
            validate(self.agenda, self.transcript, self.review, self.qa)

    def test_missing_objective_is_rejected(self):
        self.review["objectives"].pop()
        with self.assertRaisesRegex(ValueError, "incompleta"):
            validate(self.agenda, self.transcript, self.review, self.qa)

    def test_unknown_topic_cannot_be_fulfilled(self):
        self.review["objectives"][-1]["fulfillment"] = "fulfilled"
        with self.assertRaises(ValueError):
            validate(self.agenda, self.transcript, self.review, self.qa)


if __name__ == "__main__":
    unittest.main()
