import hashlib
import json
from datetime import datetime, timedelta, timezone

from services.perplexity_food_content_service import (
    build_queries,
    classify_results_in_batches,
    classify_results_hybrid,
    classify_results_with_agent,
    evaluate_result,
    search_food_content,
    validate_direct_url,
)


NOW = datetime(2026, 9, 9, 12, 0, tzinfo=timezone.utc)


def _raw(**overrides):
    data = {
        "title": "National tuna recall after contamination warning",
        "snippet": "Tuna distributed nationally was recalled after a food safety alert.",
        "url": "https://www.fda.gov/safety/recalls-market-withdrawals/tuna-recall",
        "date": "2026-09-08",
    }
    data.update(overrides)
    return data


def test_builds_five_queries_in_one_request():
    queries = build_queries("atum")
    assert len(queries) == 5
    assert all("atum" in query for query in queries)


def test_queries_include_multilingual_alias_without_extra_request():
    queries = build_queries("atum", aliases=["tuna"])
    assert len(queries) == 5
    assert all('"atum" OR "tuna"' in query for query in queries)


def test_accepts_recent_broad_alert_for_the_food():
    item = evaluate_result(_raw(), "tuna", now=NOW)
    assert item["accepted"] is True
    assert item["categoria"] == "alerta"
    assert item["ativo"] is False
    assert item["status"] == "candidate"


def test_rejects_local_brand_recall_without_broad_scope():
    item = evaluate_result(
        _raw(
            title="Cucina d'Oro pesto recalled due to undeclared cashew",
            snippet="One brand of pesto was recalled in a regional market.",
            url="https://recalls-rappels.canada.ca/en/alert-recall/cucina-oro-pesto",
        ),
        "pesto",
        now=NOW,
    )
    assert item["accepted"] is False
    assert "abrangencia_insuficiente" in item["reasons"]


def test_rejects_resolved_and_archive_urls():
    assert "alerta_encerrado" in validate_direct_url(
        "https://foodsafety.gov/recalls?status=resolved"
    )
    assert "pagina_de_arquivo" in validate_direct_url(
        "https://reuters.com/2026/09/"
    )


def test_rejects_intermediate_rss_url():
    reasons = validate_direct_url(
        "https://rmb.reuters.com/rmd/rss/item/tag:reuters.com,2026:newsml_test"
    )
    assert "url_intermediaria" in reasons


def test_rejects_alert_older_than_seven_days():
    item = evaluate_result(_raw(date="2026-08-31"), "tuna", now=NOW)
    assert item["accepted"] is False
    assert "conteudo_expirado" in item["reasons"]


def test_rejects_result_not_linked_to_food():
    item = evaluate_result(_raw(), "salmon", now=NOW)
    assert item["accepted"] is False
    assert "alimento_nao_confirmado" in item["reasons"]


def test_accepts_recent_research_and_sets_expiry():
    item = evaluate_result(
        _raw(
            title="New study examines tuna protein and health",
            snippet="A systematic review reports nutrition findings about tuna.",
            url="https://www.bmj.com/content/tuna-protein-study",
            date=(NOW - timedelta(days=20)).date().isoformat(),
        ),
        "tuna",
        now=NOW,
    )
    assert item["accepted"] is True
    assert item["categoria"] == "pesquisa"
    assert item["valido_ate"] is not None


class _FakeResponse:
    def raise_for_status(self):
        return None

    def json(self):
        return {"id": "request-1", "results": [_raw()]}


class _FakeClient:
    def __init__(self):
        self.calls = []

    async def post(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return _FakeResponse()


class _AgentFakeResponse:
    def __init__(self, items, model="openai/gpt-5.6-luna"):
        self.items = items
        self.model = model

    def raise_for_status(self):
        return None

    def json(self):
        return {
            "status": "completed",
            "model": self.model,
            "output": [{
                "type": "message",
                "content": [{
                    "type": "output_text",
                    "text": json.dumps({"items": self.items}),
                }],
            }],
            "usage": {"total_tokens": 147, "cost": {"total_cost": 0.00008}},
        }


class _AgentFakeClient:
    def __init__(self, items):
        self.items = items
        self.calls = []

    async def post(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return _AgentFakeResponse(self.items, kwargs["json"]["model"])


class _SequentialAgentFakeClient:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    async def post(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return _AgentFakeResponse(self.responses.pop(0), kwargs["json"]["model"])


def _agent_decision(raw, **overrides):
    decision = {
        "id": hashlib.sha256(raw["url"].encode("utf-8")).hexdigest()[:24],
        "relevante": True,
        "categoria": "alerta",
        "alimento_relacionado": True,
        "abrangencia": "nacional",
        "vigente": True,
        "confianca": "alta",
        "manchete_pt": "Autoridade anuncia alerta nacional para atum",
        "resumo_pt": "O aviso recente envolve atum distribuido nacionalmente.",
        "motivo": "Alerta alimentar atual e abrangente.",
    }
    decision.update(overrides)
    return decision


def test_search_is_dry_run_and_has_no_persistence():
    import asyncio

    client = _FakeClient()
    result = asyncio.run(
        search_food_content("tuna", api_key="pplx-test-key-long-enough", client=client)
    )
    assert result["ok"] is True
    assert result["dry_run"] is True
    assert result["queries"] == 5
    assert result["candidate_count"] == 1
    assert len(client.calls) == 1
    assert client.calls[0][1]["json"]["query"] == build_queries("tuna")


def test_agent_accepts_alert_but_preserves_original_source_url_and_date():
    import asyncio

    raw = _raw()
    client = _AgentFakeClient([_agent_decision(raw)])
    result = asyncio.run(
        classify_results_with_agent(
            "tuna", [raw], api_key="pplx-test-key-long-enough", client=client, now=NOW
        )
    )
    assert result["candidate_count"] == 1
    item = result["candidates"][0]
    assert item["url"] == raw["url"]
    assert item["fonte"] == "FDA"
    assert item["data"].startswith("2026-09-08")
    assert item["titulo"] == "Autoridade anuncia alerta nacional para atum"
    payload = client.calls[0][1]["json"]
    assert payload["model"] == "openai/gpt-5.6-luna"
    assert payload["tools"] == []
    assert payload["response_format"]["type"] == "json_schema"


def test_agent_cannot_override_seven_day_alert_expiry():
    import asyncio

    raw = _raw(date="2026-08-31")
    client = _AgentFakeClient([_agent_decision(raw)])
    result = asyncio.run(
        classify_results_with_agent(
            "tuna", [raw], api_key="pplx-test-key-long-enough", client=client, now=NOW
        )
    )
    assert result["candidate_count"] == 0
    assert "conteudo_expirado" in result["rejected"][0]["reasons"]


def test_agent_cannot_publish_local_alert():
    import asyncio

    raw = _raw()
    client = _AgentFakeClient([_agent_decision(raw, abrangencia="local")])
    result = asyncio.run(
        classify_results_with_agent(
            "tuna", [raw], api_key="pplx-test-key-long-enough", client=client, now=NOW
        )
    )
    assert result["candidate_count"] == 0
    assert "abrangencia_insuficiente" in result["rejected"][0]["reasons"]


def test_agent_unknown_id_is_ignored_and_original_is_rejected():
    import asyncio

    raw = _raw()
    decision = _agent_decision(raw, id="id-inventado")
    client = _AgentFakeClient([decision])
    result = asyncio.run(
        classify_results_with_agent(
            "tuna", [raw], api_key="pplx-test-key-long-enough", client=client, now=NOW
        )
    )
    assert result["candidate_count"] == 0
    assert result["rejected"][0]["reasons"] == ["agent_sem_decisao"]


def test_search_and_agent_are_two_background_calls_and_still_dry_run():
    import asyncio

    raw = _raw()
    search_client = _FakeClient()
    agent_client = _AgentFakeClient([_agent_decision(raw)])
    result = asyncio.run(
        search_food_content(
            "atum",
            aliases=["tuna"],
            api_key="pplx-test-key-long-enough",
            client=search_client,
            use_agent=True,
            agent_client=agent_client,
            now=NOW,
        )
    )
    assert result["ok"] is True
    assert result["dry_run"] is True
    assert result["candidate_count"] == 1
    assert len(search_client.calls) == 1
    assert len(agent_client.calls) == 1
    assert result["usage"]["cost"]["total_cost"] == 0.00008


def test_agent_batches_never_exceed_two_items_and_usage_is_summed():
    import asyncio

    raw_items = [
        _raw(url=f"https://www.fda.gov/safety/recalls-market-withdrawals/tuna-{i}")
        for i in range(3)
    ]
    client = _SequentialAgentFakeClient([
        [_agent_decision(raw_items[0]), _agent_decision(raw_items[1])],
        [_agent_decision(raw_items[2])],
    ])
    result = asyncio.run(
        classify_results_in_batches(
            "tuna",
            raw_items,
            api_key="pplx-test-key-long-enough",
            client=client,
            now=NOW,
        )
    )
    assert result["ok"] is True
    assert result["batch_size"] == 2
    assert result["batch_count"] == 2
    assert result["candidate_count"] == 3
    assert len(client.calls) == 2
    assert result["usage"]["total_tokens"] == 294
    assert result["usage"]["cost"]["total_cost"] == 0.00016


def test_batch_size_above_safe_limit_is_rejected():
    import asyncio

    try:
        asyncio.run(
            classify_results_in_batches(
                "tuna",
                [_raw()],
                api_key="pplx-test-key-long-enough",
                client=_AgentFakeClient([]),
                batch_size=3,
            )
        )
    except ValueError as exc:
        assert "entre 1 e 2" in str(exc)
    else:
        raise AssertionError("batch_size inseguro deveria ser rejeitado")


def test_unrelated_result_is_rejected_before_spending_on_agent():
    import asyncio

    raw = _raw(
        title="National salmon recall after contamination warning",
        snippet="Salmon distributed nationally was recalled.",
    )
    client = _AgentFakeClient([])
    result = asyncio.run(
        classify_results_with_agent(
            "atum",
            [raw],
            aliases=["tuna"],
            api_key="pplx-test-key-long-enough",
            client=client,
            now=NOW,
        )
    )
    assert result["candidate_count"] == 0
    assert "alimento_nao_confirmado" in result["rejected"][0]["reasons"]
    assert len(client.calls) == 0


def test_short_food_name_does_not_match_inside_unrelated_word():
    import asyncio

    raw = _raw(
        title="Nutrition champion report",
        snippet="A general report about nutrition research.",
    )
    client = _AgentFakeClient([])
    result = asyncio.run(
        classify_results_with_agent(
            "ham",
            [raw],
            api_key="pplx-test-key-long-enough",
            client=client,
            now=NOW,
        )
    )
    assert "alimento_nao_confirmado" in result["rejected"][0]["reasons"]
    assert len(client.calls) == 0


def test_hybrid_routes_possible_alert_to_luna_and_research_to_glm():
    import asyncio

    alert = _raw()
    research = _raw(
        title="New study examines tuna protein and health",
        snippet="A systematic review reports nutrition findings about tuna.",
        url="https://www.bmj.com/content/tuna-protein-study",
    )
    client = _SequentialAgentFakeClient([
        [_agent_decision(alert)],
        [_agent_decision(
            research,
            categoria="pesquisa",
            abrangencia="nao_informada",
            manchete_pt="Estudo analisa proteina do atum",
        )],
    ])
    result = asyncio.run(
        classify_results_hybrid(
            "atum",
            [alert, research],
            aliases=["tuna"],
            api_key="pplx-test-key-long-enough",
            client=client,
            now=NOW,
        )
    )
    assert result["ok"] is True
    assert result["candidate_count"] == 2
    assert result["possible_alert_count"] == 1
    assert result["general_count"] == 1
    models = [call[1]["json"]["model"] for call in client.calls]
    assert models == ["openai/gpt-5.6-luna", "perplexity/glm-5.3-flash"]
    assert result["candidates"][0]["classificador"] == "openai/gpt-5.6-luna"
    assert result["candidates"][1]["classificador"] == "perplexity/glm-5.3-flash"


def test_hybrid_prefilters_unrelated_results_before_any_agent_call():
    import asyncio

    unrelated = _raw(
        title="National salmon recall after contamination warning",
        snippet="Salmon distributed nationally was recalled.",
        url="https://www.fda.gov/safety/recalls-market-withdrawals/salmon-recall",
    )
    client = _AgentFakeClient([])
    result = asyncio.run(
        classify_results_hybrid(
            "atum",
            [unrelated],
            aliases=["tuna"],
            api_key="pplx-test-key-long-enough",
            client=client,
            now=NOW,
        )
    )
    assert result["ok"] is True
    assert result["candidate_count"] == 0
    assert result["prefilter_rejected_count"] == 1
    assert result["agent_calls"] == 0
    assert len(client.calls) == 0
    assert "alimento_nao_confirmado" in result["rejected"][0]["reasons"]


def test_hybrid_routes_mercury_only_story_to_general_model():
    import asyncio

    curiosity = _raw(
        title="Types of tuna show different mercury levels",
        snippet="A health report compares mercury levels across tuna species.",
        url="https://www.cnn.com/2026/09/04/health/tuna-mercury-levels",
    )
    client = _AgentFakeClient([_agent_decision(
        curiosity,
        categoria="curiosidade",
        abrangencia="nao_informada",
        manchete_pt="Tipos de atum apresentam niveis diferentes de mercurio",
    )])
    result = asyncio.run(
        classify_results_hybrid(
            "atum",
            [curiosity],
            aliases=["tuna"],
            api_key="pplx-test-key-long-enough",
            client=client,
            now=NOW,
        )
    )
    assert result["possible_alert_count"] == 0
    assert result["general_count"] == 1
    assert client.calls[0][1]["json"]["model"] == "perplexity/glm-5.3-flash"
    assert result["candidates"][0]["classificador"] == "perplexity/glm-5.3-flash"


def test_hybrid_reports_agent_call_count_and_prefilter_rejections():
    import asyncio

    alert = _raw()
    unrelated = _raw(
        title="National salmon recall after contamination warning",
        snippet="Salmon distributed nationally was recalled.",
        url="https://www.fda.gov/safety/recalls-market-withdrawals/salmon-recall-2",
    )
    client = _AgentFakeClient([_agent_decision(alert)])
    result = asyncio.run(
        classify_results_hybrid(
            "atum",
            [alert, unrelated],
            aliases=["tuna"],
            api_key="pplx-test-key-long-enough",
            client=client,
            now=NOW,
        )
    )
    assert result["agent_calls"] == 1
    assert result["prefilter_rejected_count"] == 1
    assert result["rejected_count"] == 1
