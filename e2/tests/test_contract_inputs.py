"""Regression checks for constraints declared in A11's service input definitions."""
import copy
import json
import unittest

from jsonschema import ValidationError

from e2.validate import REFERENCE, validate_input_document
from e2.contract import validator, validate_job

EXAMPLES = json.loads((REFERENCE / "contract-examples.json").read_text(encoding="utf-8"))


class ContractInputTests(unittest.TestCase):
    def request(self, job_type):
        return copy.deepcopy(EXAMPLES["requests"][job_type])

    def test_unknown_job_type_is_rejected(self):
        request = self.request("FULL_CHECK")
        request["job_type"] = "ABC"
        with self.assertRaises(ValidationError):
            validate_input_document(request)

    def test_incremental_without_baseline_is_rejected(self):
        request = self.request("INCREMENTAL_CHECK")
        del request["input"]["baseline"]
        with self.assertRaises(ValidationError):
            validate_input_document(request)

    def test_draft_without_verification_is_rejected(self):
        request = self.request("DRAFT")
        del request["input"]["verify_command"]
        with self.assertRaises(ValidationError):
            validate_input_document(request)

    def test_zero_iterations_is_rejected(self):
        request = self.request("DRAFT")
        request["input"]["max_iterations"] = 0
        with self.assertRaises(ValidationError):
            validate_input_document(request)

    def test_short_repository_commit_is_rejected(self):
        request = self.request("REPAIR")
        request["input"]["repository"]["commit"] = "abc1234"
        with self.assertRaises(ValidationError):
            validate_input_document(request)

    def test_repair_without_report_is_rejected(self):
        request = self.request("REPAIR")
        del request["input"]["md_report_uri"]
        with self.assertRaises(ValidationError):
            validate_input_document(request)

    def test_empty_image_is_rejected(self):
        request = self.request("REPAIR")
        request["input"]["image"] = ""
        with self.assertRaises(ValidationError):
            validate_input_document(request)

    def test_query_input_cannot_bypass_service_constraints(self):
        response = copy.deepcopy(EXAMPLES["responses"]["query_repair"])
        del response["input"]["makefile_uri"]
        with self.assertRaises(ValidationError):
            validate_input_document(response, query=True)

    def test_202_cannot_be_running(self):
        with self.assertRaises(ValidationError):
            validator("DraftResponse").validate({"job_id":"job-x","job_type":"DRAFT","status":"RUNNING"})

    def test_failed_job_cannot_carry_findings(self):
        response=copy.deepcopy(EXAMPLES["responses"]["query_full_check"])
        response["status"]="FAILED"
        response["error"]={"code":"ANALYSIS_5001","message":"failure"}
        with self.assertRaises(ValidationError):
            validate_job(response)

    def test_baseline_configuration_mismatch(self):
        request=self.request("INCREMENTAL_CHECK")
        request["input"]["baseline"]["configuration_id"]="different"
        with self.assertRaises(ValueError):
            validate_input_document(request)


if __name__ == "__main__":
    unittest.main()
