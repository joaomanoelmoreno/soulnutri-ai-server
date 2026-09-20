# -*- coding: utf-8 -*-
"""Instrumentacao observacional opt-in do endpoint Radar Alimentar."""

import json
import ipaddress
import logging
import os
import time
import uuid
from contextvars import ContextVar
from urllib.parse import urlsplit, urlunsplit


logger = logging.getLogger(__name__)

_request_id = ContextVar("radar_request_id", default=None)
_started_at = ContextVar("radar_started_at", default=None)
_first_candidate_logged = ContextVar("radar_first_candidate_logged", default=False)


def enabled():
    try:
        return os.getenv("RADAR_DIAGNOSTICS_ENABLED", "false").strip().lower() in {
            "1", "true", "yes", "on",
        }
    except Exception:
        return False


def log_runtime_status():
    """Registra apenas o estado booleano do flag; nunca registra o valor bruto."""
    try:
        logger.warning("[RADAR_DIAG_BOOT] enabled=%s", enabled())
    except Exception:
        pass


def active():
    """Verdadeiro somente dentro de contexto iniciado pelo endpoint Radar."""
    try:
        return enabled() and _request_id.get() is not None
    except Exception:
        return False


def begin_request():
    if not enabled():
        return None
    try:
        request_id = uuid.uuid4().hex[:12]
        started_at = time.perf_counter()
        return (
            _request_id.set(request_id),
            _started_at.set(started_at),
            _first_candidate_logged.set(False),
        )
    except Exception:
        return None


def end_request(tokens):
    if not tokens:
        return
    try:
        _first_candidate_logged.reset(tokens[2])
        _started_at.reset(tokens[1])
        _request_id.reset(tokens[0])
    except Exception:
        pass


def timer_start():
    if not active():
        return None
    try:
        return time.perf_counter()
    except Exception:
        return None


def duration_ms(started):
    if started is None:
        return None
    try:
        return round((time.perf_counter() - started) * 1000, 2)
    except Exception:
        return None


def elapsed_ms():
    try:
        return duration_ms(_started_at.get())
    except Exception:
        return None


def sanitize_url(value):
    """Remove credenciais, query e fragmento apenas da copia diagnostica."""
    try:
        parts = urlsplit(str(value))
        hostname = parts.hostname or ""
        try:
            ipaddress.ip_address(hostname)
            hostname = "ip-redacted"
        except ValueError:
            pass
        if ":" in hostname and not hostname.startswith("["):
            hostname = f"[{hostname}]"
        netloc = f"{hostname}:{parts.port}" if parts.port is not None else hostname
        return urlunsplit((parts.scheme, netloc, parts.path, "", ""))
    except Exception:
        return "[url-redacted]"


def _safe_fields(fields):
    return {
        key: sanitize_url(value)
        if key.lower() == "url" or key.lower().endswith("_url")
        else value
        for key, value in fields.items()
        if value is not None
    }


def log_event(event, **fields):
    if not active():
        return
    try:
        payload = {
            "event": event,
            "radar_request_id": _request_id.get(),
        }
        payload.update(_safe_fields(fields))
        serialized = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        logger.info("[RADAR_DIAG] %s", serialized)
    except Exception:
        pass


def log_first_candidate(**fields):
    if not active():
        return
    try:
        if _first_candidate_logged.get():
            return
        _first_candidate_logged.set(True)
        log_event("first_candidate", first_candidate_ms=elapsed_ms(), **fields)
    except Exception:
        pass
