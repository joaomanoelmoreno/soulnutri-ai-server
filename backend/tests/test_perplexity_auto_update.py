# -*- coding: utf-8 -*-

from datetime import datetime, timedelta, timezone

from scripts.perplexity_auto_update import build_document, polaridade_for


def _valid_item():
    now = datetime.now(timezone.utc)
    return {
        "id": "teste-alerta",
        "titulo": "Contaminação relacionada ao atum",
        "url": "https://example.com/tuna-alert",
        "fonte": "Fonte especializada",
        "categoria": "alerta",
        "resumo": "Informação publicada por fonte especializada.",
        "data": now.isoformat(),
        "valido_ate": (now + timedelta(days=7)).isoformat(),
        "tags": ["atum"],
    }


def test_build_document_publishes_valid_alert_neutrally():
    document = build_document(_valid_item())

    assert document is not None
    assert document["ativo"] is True
    assert document["publicacao_automatica"] is True
    assert document["polaridade"] == "alerta"
    assert document["categoria"] == "alerta"
    assert document["mensagem_alerta"].startswith("ALERTA:")
    assert "Clique aqui para ler a notícia." in document["mensagem_alerta"]
    assert "não é médico" in document["disclaimer"]


def test_build_document_rejects_incomplete_content():
    item = _valid_item()
    item["resumo"] = ""

    assert build_document(item) is None


def test_polaridade_does_not_turn_risk_into_alert():
    assert polaridade_for("risco") == "neutro"
    assert polaridade_for("pesquisa") == "neutro"
    assert polaridade_for("beneficio") == "beneficio"
    assert polaridade_for("alerta") == "alerta"


def test_run_publishes_candidates_and_expires_old_content():
    import asyncio
    import json
    import os
    import scripts.perplexity_auto_update as auto

    class UpdateResult:
        modified_count = 2

    class FakeCollection:
        def __init__(self):
            self.updates = []

        async def update_many(self, query, update):
            return UpdateResult()

        async def update_one(self, query, update, upsert=False):
            self.updates.append({
                "query": query,
                "update": update,
                "upsert": upsert,
            })
            return UpdateResult()

    class FakeClient:
        last_collection = None

        def __init__(self, mongo_url):
            self.collection = FakeCollection()
            FakeClient.last_collection = self.collection

        def __getitem__(self, name):
            return self

        @property
        def contextual_breaking_news(self):
            return self.collection

        def close(self):
            return None

    async def fake_search(foods, **kwargs):
        now = datetime.now(timezone.utc)
        return {
            "ok": True,
            "error_count": 0,
            "results": [{
                "food": "atum",
                "candidate_count": 1,
                "candidates": [{
                    "id": "candidate-1",
                    "titulo": "Informação relevante sobre atum",
                    "url": "https://example.com/tuna",
                    "fonte": "Fonte especializada",
                    "categoria": "risco",
                    "resumo": "Resumo baseado em fonte especializada.",
                    "data": now.isoformat(),
                    "valido_ate": (now + timedelta(days=30)).isoformat(),
                    "tags": ["atum"],
                }],
            }],
        }

    original_client = auto.AsyncIOMotorClient
    original_search = auto.search_food_content_batch

    try:
        auto.AsyncIOMotorClient = FakeClient
        auto.search_food_content_batch = fake_search
        os.environ["PERPLEXITY_API_KEY"] = "pplx-test-key"
        os.environ["MONGO_URL"] = "mongodb://fake"
        os.environ["DB_NAME"] = "soulnutri_test"
        os.environ["PERPLEXITY_AUTO_FOODS_JSON"] = json.dumps(["atum"])

        result = asyncio.run(auto.run())

        assert result["ok"] is True
        assert result["published"] == 1
        assert result["expired"] == 2
        assert result["errors"] == 0
        assert len(FakeClient.last_collection.updates) == 1
        document = FakeClient.last_collection.updates[0]["update"]["$set"]
        assert document["ativo"] is True
        assert document["categoria"] == "risco"
        assert document["polaridade"] == "neutro"
    finally:
        auto.AsyncIOMotorClient = original_client
        auto.search_food_content_batch = original_search

if __name__ == "__main__":
    test_build_document_publishes_valid_alert_neutrally()
    test_build_document_rejects_incomplete_content()
    test_polaridade_does_not_turn_risk_into_alert()
    test_run_publishes_candidates_and_expires_old_content()
    print("TESTES AUTOMÁTICOS: 4 testes aprovados.")
