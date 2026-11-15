"""Harness tests: failures in the test runner must not become mutant kills."""
import subprocess
import unittest
from unittest.mock import patch
import check_rule_mutations as qa


class RunnerClassification(unittest.TestCase):
    def result(self, output, code=1):
        with patch.object(qa.subprocess, 'run', return_value=subprocess.CompletedProcess([], code, '', output)):
            return qa.run_case('.', 1)[0]

    def test_assertion_failure_is_recorded(self):
        result = self.result('FAIL: test_guard (matrix.Tests.test_guard)\nTraceback\nAssertionError: bad\nRan 1 test in 0.01s\n')
        self.assertEqual(len(result['failures']), 1)
        self.assertEqual(result['model_errors'], 0)

    def test_model_unavailable_is_semantic_error(self):
        result = self.result('ERROR: test_guard (matrix.Tests.test_guard)\nTraceback\ntlm_model.NotAvailable: handoff\n\n----------------------------------------------------------------------\nRan 1 test in 0.01s\n')
        self.assertEqual(len(result['errors']), 1)
        self.assertEqual(result['model_errors'], 1)

    def test_import_error_is_not_model_failure(self):
        result = self.result('ERROR: matrix (unittest.loader._FailedTest.matrix)\nTraceback\nModuleNotFoundError: missing\n\n----------------------------------------------------------------------\nRan 1 test in 0.01s\n')
        self.assertEqual(len(result['errors']), 1)
        self.assertEqual(result['model_errors'], 0)

    def test_mixed_errors_do_not_hide_infrastructure_failure(self):
        result = self.result('ERROR: test_a (matrix.Tests.test_a)\nTraceback\ntlm_model.NotAvailable: x\n\n======================================================================\nERROR: test_b (matrix.Tests.test_b)\nTraceback\nImportError: broken\n\n----------------------------------------------------------------------\nRan 2 tests in 0.01s\n')
        self.assertEqual(len(result['errors']), 2)
        self.assertEqual(result['model_errors'], 1)

    def test_no_test_summary_is_not_success(self):
        result = self.result('interpreter crashed', 2)
        self.assertIsNone(result['tests'])

    def test_chained_import_error_invalidates_audit(self):
        output = ('ERROR: test_guard (matrix.Tests.test_guard)\n'
                  '----------------------------------------------------------------------\n'
                  'Traceback (most recent call last):\n'
                  'tlm_model.NotAvailable: handoff\n\n'
                  'During handling of the above exception, another exception occurred:\n\n'
                  'Traceback (most recent call last):\n'
                  'ImportError: broken dependency\n\n'
                  '----------------------------------------------------------------------\n'
                  'Ran 70 tests in 0.01s\n\nFAILED (errors=1)\n')
        result = self.result(output)
        self.assertEqual(result['model_errors'], 0)
        baseline = dict(result, exit_code=0, errors=[], model_errors=0)
        with patch.object(qa, 'run_case', side_effect=[(baseline, '')] + [(result, output)] * len(qa.RULES)):
            report = qa.audit()
        self.assertEqual(report['status'], 'failed')
        self.assertTrue(all(item['status'] == 'invalid_run' for item in report['mutations']))


if __name__ == '__main__':
    unittest.main()
