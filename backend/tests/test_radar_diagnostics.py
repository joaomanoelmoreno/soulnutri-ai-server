# -*- coding: utf-8 -*-
"""Testes locais da instrumentacao do Radar existente na main."""

import asyncio
import json
import logging
import os
import unittest
from contextlib import contextmanager
from datetime import datetime, timezone
from unittest.mock import patch

from services import radar_diagnostics as diag
from services.breaking_news_service.providers import dynamic
from services.perplexity_food_content_service import search_food_content


NOW = datetime(2026, 9, 20, 12, 0, tzinfo=timezone.utc)


class _Response:
    def __init__(self, results):
        self.results = results

    def raise_for_status(self):
        return None

    def json(self):
        return {"id": "request-local", "results": self.results}


class _SearchClient:
    def __init__(self, results):
        self.results = results
        self.calls = []

    async def post(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return _Response(self.results)


def _raw(index=1):
    return {
        "title": f"National tuna recall after contamination warning {index}",
        "snippet": "Tuna distributed nationally was recalled after a food safety alert.",
        "url": f"https://www.fda.gov/safety/recalls-market-withdrawals/tuna-{index}",
        "date": "2026-09-19",
    }


@contextmanager
def _capture(enabled):
    records = []
    handler = logging.Handler()
    handler.emit = records.append
    logger = logging.getLogger("services.radar_diagnostics")
    previous_level = logger.level
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    try:
        with patch.dict(os.environ, {
            "RADAR_DIAGNOSTICS_ENABLED": "true" if enabled else "false"
        }):
            yield records
    finally:
        logger.removeHandler(handler)
        logger.setLevel(previous_level)


def _messages(records):
    return [
        record.getMessage().split("[RADAR_DIAG] ", 1)[1]
        for record in records
        if "[RADAR_DIAG] " in record.getMessage()
    ]


class RadarDiagnosticsMainTest(unittest.TestCase):
    def _run_search(self, enabled, results):
        client = _SearchClient(results)
        with _capture(enabled) as records:
            tokens = diag.begin_request()
            try:
                result = asyncio.run(search_food_content(
                    "tuna",
                    api_key="pplx-local-fake-key",
                    client=client,
                    use_agent=False,
                    now=NOW,
                ))
            finally:
                diag.end_request(tokens)
        return result, _messages(records), client

    def test_flag_defaults_to_false(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(diag.enabled())
            self.assertIsNone(diag.begin_request())

    def test_url_sanitizer_does_not_log_ip_hosts(self):
        sanitized = diag.sanitize_url("https://127.0.0.1:8443/noticia?token=SECRET#parte")
        self.assertEqual(sanitized, "https://ip-redacted:8443/noticia")
        self.assertNotIn("127.0.0.1", sanitized)

    def test_flag_off_has_no_logs_or_diagnostic_serialization_and_matches_on(self):
        raw = _raw()
        with patch.object(diag, "_safe_fields", side_effect=AssertionError("executado")):
            off, off_logs, off_client = self._run_search(False, [raw])
        on, on_logs, on_client = self._run_search(True, [raw])

        self.assertEqual(off, on)
        self.assertEqual(off_logs, [])
        self.assertTrue(on_logs)
        self.assertEqual(len(off_client.calls), 1)
        self.assertEqual(len(on_client.calls), 1)

    def test_empty_search_records_real_counts(self):
        result, logs, client = self._run_search(True, [])
        events = [json.loads(line) for line in logs]

        self.assertEqual(result["candidate_count"], 0)
        self.assertEqual(len(client.calls), 1)
        search = next(event for event in events if event["event"] == "search_done")
        filters = next(event for event in events if event["event"] == "local_filters_done")
        self.assertEqual(search["search_result_count"], 0)
        self.assertEqual(filters["candidate_count"], 0)
        self.assertEqual(filters["rejected_count"], 0)

    def test_search_with_candidates_records_filters_and_first_candidate(self):
        result, logs, _client = self._run_search(True, [_raw(1), _raw(2)])
        events = [json.loads(line) for line in logs]
        filters = next(event for event in events if event["event"] == "local_filters_done")

        self.assertEqual(result["candidate_count"], 2)
        self.assertEqual(filters["input_count"], 2)
        self.assertEqual(filters["unique_count"], 2)
        self.assertEqual(filters["candidate_count"], 2)
        self.assertEqual(len([e for e in events if e["event"] == "first_candidate"]), 1)

    def test_rejection_reasons_are_aggregated_without_raw_content(self):
        raw = {
            "title": "Broccoli sprouts recall after contamination warning",
            "snippet": "Broccoli sprouts distributed nationally were recalled.",
            "url": "https://www.fda.gov/safety/recalls-market-withdrawals/broccoli-sprouts",
            "date": "2026-09-19",
        }
        result, logs, _client = self._run_search(True, [raw])
        events = [json.loads(line) for line in logs]
        filters = next(event for event in events if event["event"] == "local_filters_done")

        self.assertEqual(result["candidate_count"], 0)
        self.assertEqual(filters["rejected_count"], 1)
        self.assertEqual(
            filters["rejection_reasons"],
            {"alimento_nao_confirmado": 1},
        )
        serialized = json.dumps(filters, ensure_ascii=False)
        self.assertNotIn("Broccoli sprouts", serialized)
        self.assertNotIn("broccoli-sprouts", serialized)

    def test_dynamic_keeps_use_agent_false_selection_order_and_original_url(self):
        original_url = (
            "https://apiuser:apipass@example.test:8443/noticia"
            "?token=TOKEN&key=KEY&signature=SIGNATURE&utm_source=radar&id=123#parte"
        )
        candidates = [
            {
                "titulo": "Alerta baixo",
                "url": "https://example.test/alerta",
                "fonte": "Fonte A",
                "categoria": "alerta",
                "impacto": "baixo",
                "relevancia_publica": "alta",
            },
            {
                "titulo": "Beneficio critico",
                "url": original_url,
                "fonte": "Fonte B",
                "categoria": "beneficio",
                "impacto": "critico",
                "relevancia_publica": "baixa",
            },
        ]
        calls = []

        async def fake_search(*args, **kwargs):
            calls.append((args, kwargs))
            return {"candidates": candidates}

        with patch.object(dynamic, "search_food_content", fake_search):
            with patch.dict(os.environ, {
                "RADAR_DIAGNOSTICS_ENABLED": "true",
                "PERPLEXITY_API_KEY": "pplx-local-fake-key",
            }):
                with _capture(True) as records:
                    tokens = diag.begin_request()
                    try:
                        result = asyncio.run(dynamic.fetch("tuna", None, [], None))
                    finally:
                        diag.end_request(tokens)

        joined = "\n".join(_messages(records))
        self.assertEqual(len(calls), 1)
        self.assertIs(calls[0][1]["use_agent"], False)
        self.assertEqual(result["titulo"], "Beneficio critico")
        self.assertEqual(result["url"], original_url)
        self.assertIn("https://example.test:8443/noticia", joined)
        for secret in (
            "TOKEN", "KEY", "SIGNATURE", "utm_source", "id=123", "parte",
            "apiuser", "apipass",
        ):
            self.assertNotIn(secret, joined)

    def test_empty_dynamic_result_is_logged_without_changing_none(self):
        async def fake_search(*_args, **kwargs):
            self.assertIs(kwargs["use_agent"], False)
            return {"candidates": []}

        with patch.object(dynamic, "search_food_content", fake_search):
            with patch.dict(os.environ, {
                "RADAR_DIAGNOSTICS_ENABLED": "true",
                "PERPLEXITY_API_KEY": "pplx-local-fake-key",
            }):
                with _capture(True) as records:
                    tokens = diag.begin_request()
                    try:
                        result = asyncio.run(dynamic.fetch("tuna", None, [], None))
                    finally:
                        diag.end_request(tokens)
        events = [json.loads(line) for line in _messages(records)]
        selection = next(event for event in events if event["event"] == "selection_done")
        self.assertIsNone(result)
        self.assertFalse(selection["result"])
        self.assertEqual(selection["candidate_count"], 0)

    def test_logger_and_serialization_failures_do_not_change_result(self):
        raw = _raw()
        expected, _logs, _client = self._run_search(False, [raw])
        with patch.object(diag.logger, "info", side_effect=RuntimeError("logger")):
            logger_result, _logs, _client = self._run_search(True, [raw])
        with patch.object(diag, "_safe_fields", side_effect=TypeError("serialization")):
            serialization_result, _logs, _client = self._run_search(True, [raw])
        self.assertEqual(logger_result, expected)
        self.assertEqual(serialization_result, expected)

    def test_service_outside_radar_context_emits_no_logs(self):
        client = _SearchClient([_raw()])
        with _capture(True) as records:
            result = asyncio.run(search_food_content(
                "tuna",
                api_key="pplx-local-fake-key",
                client=client,
                use_agent=False,
                now=NOW,
            ))
        self.assertEqual(result["candidate_count"], 1)
        self.assertEqual(_messages(records), [])


if __name__ == "__main__":
    unittest.main()
