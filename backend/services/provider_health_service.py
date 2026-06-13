"""
SoulNutri — Provider Health Service
Fase 1 / Bloco 3A: Observabilidade e Resiliência de Providers

Testa chamadas reais (não ping) a cada provider configurado.
Não altera lógica de produção. Apenas observacional.
"""
import os
import time
import logging
import json
from datetime import datetime, timezone
from typing import Dict, Any

logger = logging.getLogger(__name__)


def _log_provider(provider: str, model: str, success: bool,
                  latency_ms: int, fallback: bool = False,
                  reason: str = None, error_code: str = None):
    """Emite log estruturado JSON de resultado de provider."""
    entry: Dict[str, Any] = {
        "provider": provider,
        "model": model,
        "success": success,
        "latency_ms": latency_ms,
    }
    if fallback:
        entry["fallback"] = True
    if reason:
        entry["reason"] = reason
    if error_code:
        entry["error_code"] = error_code
    logger.info("[PROVIDER] %s", json.dumps(entry, ensure_ascii=False))


def _result_ok(latency_ms: int) -> Dict[str, Any]:
    return {"status": "ok", "latency_ms": latency_ms}


def _result_error(error_code: str, message: str, latency_ms: int) -> Dict[str, Any]:
    return {
        "status": "error",
        "error_code": error_code,
        "message": message[:120],
        "latency_ms": latency_ms,
    }


def _parse_error_code(err: str) -> str:
    for code in ["404", "410", "429", "400", "403", "500", "503"]:
        if code in err:
            return code
    if "expired" in err.lower():
        return "key_expired"
    if "quota" in err.lower():
        return "quota_exceeded"
    return "unknown"


def _test_google(model: str) -> Dict[str, Any]:
    """Chama Google Gemini com prompt mínimo e mede latência."""
    google_key = os.environ.get("GOOGLE_API_KEY")
    if not google_key:
        return _result_error("no_key", "GOOGLE_API_KEY não configurada", 0)
    t0 = time.time()
    try:
        from google import genai
        client = genai.Client(api_key=google_key)
        resp = client.models.generate_content(
            model=model,
            contents=["Responda apenas OK"]
        )
        ms = round((time.time() - t0) * 1000)
        _ = resp.text  # força leitura da resposta
        _log_provider("google", model, True, ms)
        return _result_ok(ms)
    except Exception as e:
        ms = round((time.time() - t0) * 1000)
        code = _parse_error_code(str(e))
        msg = str(e)[:120]
        _log_provider("google", model, False, ms, reason=code, error_code=code)
        return _result_error(code, msg, ms)


async def _test_emergent(model: str) -> Dict[str, Any]:
    """Chama Emergent LLM com prompt mínimo e mede latência."""
    emergent_key = os.environ.get("EMERGENT_LLM_KEY")
    if not emergent_key:
        return _result_error("no_key", "EMERGENT_LLM_KEY não configurada", 0)
    t0 = time.time()
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        chat = LlmChat(
            api_key=emergent_key,
            session_id=f"health-{int(time.time())}",
            system_message="Responda apenas OK"
        ).with_model("gemini", model)
        msg = UserMessage(text="Responda apenas OK")
        await chat.send_message(msg)
        ms = round((time.time() - t0) * 1000)
        _log_provider("emergent", model, True, ms)
        return _result_ok(ms)
    except Exception as e:
        ms = round((time.time() - t0) * 1000)
        code = _parse_error_code(str(e))
        msg = str(e)[:120]
        _log_provider("emergent", model, False, ms,
                      fallback=True, reason=code, error_code=code)
        return _result_error(code, msg, ms)


async def run_provider_health_check() -> Dict[str, Any]:
    """
    Executa chamadas reais a todos os providers configurados.
    Retorna resultado estruturado.
    """
    ts = datetime.now(timezone.utc).isoformat()

    google_lite = _test_google("gemini-2.5-flash-lite")
    google_full = _test_google("gemini-2.5-flash")
    emergent = await _test_emergent("gemini-2.5-flash")

    all_ok = all(
        r["status"] == "ok"
        for r in [google_lite, google_full, emergent]
    )

    return {
        "timestamp": ts,
        "overall": "ok" if all_ok else "degraded",
        "google_flash_lite": google_lite,
        "google_flash": google_full,
        "emergent": emergent,
    }
