# -*- coding: utf-8 -*-
"""Tests for the processing metrics environment override."""

import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

import server  # noqa: E402


class ProcessingMetricsConfigTest(unittest.IsolatedAsyncioTestCase):
    async def test_env_absent_uses_database_setting(self):
        with (
            patch.dict(server.os.environ, {}, clear=False),
            patch.object(
                server, "get_setting", new=AsyncMock(return_value=True)
            ) as setting,
        ):
            server.os.environ.pop("ENABLE_PROCESSING_METRICS", None)
            enabled = await server.processing_metrics_enabled()

        self.assertTrue(enabled)
        setting.assert_awaited_once_with("ENABLE_PROCESSING_METRICS")

    async def test_env_false_disables_metrics_write_decision(self):
        save = Mock()
        with (
            patch.dict(
                server.os.environ,
                {"ENABLE_PROCESSING_METRICS": "false"},
                clear=False,
            ),
            patch.object(server, "get_setting", new=AsyncMock()) as setting,
        ):
            enabled = await server.processing_metrics_enabled()
            if enabled:
                save({"test": True})

        self.assertFalse(enabled)
        save.assert_not_called()
        setting.assert_not_awaited()

    async def test_env_true_enables_metrics_write_decision(self):
        save = Mock()
        with (
            patch.dict(
                server.os.environ,
                {"ENABLE_PROCESSING_METRICS": "true"},
                clear=False,
            ),
            patch.object(server, "get_setting", new=AsyncMock()) as setting,
        ):
            enabled = await server.processing_metrics_enabled()
            if enabled:
                save({"test": True})

        self.assertTrue(enabled)
        save.assert_called_once_with({"test": True})
        setting.assert_not_awaited()

    async def test_env_parsing_is_case_insensitive(self):
        cases = {
            "FALSE": False,
            "0": False,
            "No": False,
            "oFf": False,
            "TRUE": True,
            "1": True,
            "YeS": True,
            "oN": True,
        }
        for raw_value, expected in cases.items():
            with self.subTest(raw_value=raw_value):
                with patch.dict(
                    server.os.environ,
                    {"ENABLE_PROCESSING_METRICS": raw_value},
                    clear=False,
                ):
                    self.assertEqual(
                        await server.processing_metrics_enabled(), expected
                    )


if __name__ == "__main__":
    unittest.main()
