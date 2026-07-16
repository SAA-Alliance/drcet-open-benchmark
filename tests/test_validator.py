import copy
import json
from pathlib import Path
import unittest

from drcet_validator.validate import validate_submission

ROOT = Path(__file__).resolve().parents[1]


class ValidatorTests(unittest.TestCase):
    def load(self, rel):
        return json.loads((ROOT / rel).read_text(encoding="utf-8"))

    def test_synthetic_pass_fixture(self):
        result = validate_submission(self.load("examples/synthetic_pass/drcet_submission.json"))
        self.assertEqual(result["status"], "PASS")

    def test_synthetic_withheld_fixture(self):
        result = validate_submission(self.load("examples/synthetic_withheld/drcet_submission.json"))
        self.assertEqual(result["status"], "PASS")

    def test_withheld_value_is_rejected(self):
        payload = self.load("examples/synthetic_withheld/drcet_submission.json")
        payload = copy.deepcopy(payload)
        payload["metrics"][0]["value"] = -0.42
        result = validate_submission(payload)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("WITHHELD metric must not serialize value" in e for e in result["errors"]))

    def test_missing_core_non_claim_is_rejected(self):
        payload = self.load("examples/synthetic_pass/drcet_submission.json")
        payload = copy.deepcopy(payload)
        payload["non_claims"] = ["not production approval"]
        result = validate_submission(payload)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("not execution authorization" in e for e in result["errors"]))


if __name__ == "__main__":
    unittest.main()
