# -*- coding: utf-8 -*-
"""Regression tests for raw-vs-adjusted recognition diagnostics."""

import copy
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

import server  # noqa: E402
from ai.policy import analyze_result  # noqa: E402


class IdentifyDiagnosticsTest(unittest.TestCase):
    def setUp(self):
        self.results = [
            {
                "dish": "Raw Top One",
                "raw_score": 0.83,
                "score": 0.76,
                "confidence": "media",
                "gap": 0.01,
            },
            {
                "dish": "Raw Top Two",
                "raw_score": 0.82,
                "score": 0.82,
                "confidence": "media",
                "gap": 0.01,
            },
            {
                "dish": "Raw Top Three",
                "raw_score": 0.70,
                "score": 0.70,
                "confidence": "baixa",
                "gap": 0.01,
            },
        ]

    @staticmethod
    def _rendered_messages(log_mock):
        return [
            call.args[0] % call.args[1:]
            for call in log_mock.call_args_list
        ]

    def test_logs_raw_and_adjusted_scores_without_reinterpreting_candidates(self):
        original = copy.deepcopy(self.results)

        with patch.object(server.logger, "info") as log_info:
            server._log_identify_diagnostics(self.results)

        self.assertEqual(self.results, original)
        messages = self._rendered_messages(log_info)
        self.assertIn(
            "[IDENTIFY_DIAG] top1 dish='Raw Top One' raw_score=0.8300 "
            "adjusted_score=0.7600 scores_equal=false",
            messages,
        )
        self.assertIn(
            "[IDENTIFY_DIAG] top2 dish='Raw Top Two' raw_score=0.8200 "
            "adjusted_score=0.8200 scores_equal=true",
            messages,
        )
        self.assertIn(
            "[IDENTIFY_DIAG] top3 dish='Raw Top Three' raw_score=0.7000 "
            "adjusted_score=0.7000 scores_equal=true",
            messages,
        )
        self.assertIn(
            "[IDENTIFY_DIAG] top1_score_detail raw_score=0.8300 "
            "adjusted_score=0.7600 penalty_total=0.0700",
            messages,
        )
        self.assertIn(
            "[IDENTIFY_DIAG] gap_top1_top2=0.0100 "
            "score_basis=raw_score source=local_index",
            messages,
        )

    def test_adjusted_score_does_not_change_raw_top1_identity(self):
        decision = analyze_result(self.results)

        self.assertEqual(decision["dish"], "Raw Top One")
        self.assertEqual(decision["score"], 0.76)
        self.assertEqual(
            decision["alternatives"][:2],
            ["Raw Top Two", "Raw Top Three"],
        )

    def test_empty_results_do_not_log(self):
        with patch.object(server.logger, "info") as log_info:
            server._log_identify_diagnostics([])
        log_info.assert_not_called()


if __name__ == "__main__":
    unittest.main()
