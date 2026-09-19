"""Best-effort persistence for controlled shadow recognition scans."""
from __future__ import annotations

import asyncio
import hashlib
import logging
import os
from datetime import datetime, timezone
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)

SHADOW_COLLECTION = "shadow_recognition_scans"
SHADOW_R2_PREFIX = "shadow/scans/objects"


def shadow_mode_enabled() -> bool:
    """The feature is opt-in and disabled unless explicitly set to true."""
    return os.environ.get("SHADOW_MODE_ENABLED", "false").strip().lower() == "true"


def _safe_top_k(top_k: Optional[list[dict[str, Any]]]) -> Optional[list[dict[str, Any]]]:
    if not top_k:
        return None
    return [
        {
            key: item.get(key)
            for key in ("dish", "dish_display", "score", "raw_score", "gap", "consistency", "image_count")
            if item.get(key) is not None
        }
        for item in top_k[:5]
        if isinstance(item, dict)
    ] or None


async def persist_shadow_scan(
    *,
    db: Any,
    image_bytes: bytes,
    request_id: str,
    predicted_dish: Optional[str],
    identified: bool,
    score: Optional[float],
    confidence: Optional[str],
    gap: Optional[float],
    top_k: Optional[list[dict[str, Any]]],
    width: Optional[int],
    height: Optional[int],
    content_type: str,
    recognition_source: Optional[str],
    index_name: Optional[str] = None,
    index_version: Optional[str] = None,
    uploader: Optional[Callable[[str, bytes, str], bool]] = None,
) -> None:
    """Store one isolated scan. Every failure is swallowed by design."""
    if not shadow_mode_enabled():
        return

    try:
        if uploader is None:
            from services.r2_service import r2_upload_image
            uploader = r2_upload_image

        created_at = datetime.now(timezone.utc)
        sha256 = hashlib.sha256(image_bytes).hexdigest()
        object_key = f"{SHADOW_R2_PREFIX}/{sha256}"
        record = {
            "request_id": request_id,
            "created_at": created_at,
            "image_sha256": sha256,
            "image": {
                "r2_key": object_key,
                "content_type": content_type or "application/octet-stream",
                "size_bytes": len(image_bytes),
                "width": width,
                "height": height,
                "upload_status": "pending",
            },
            "recognition": {
                "predicted_dish": predicted_dish,
                "identified": bool(identified),
                "score": score,
                "confidence": confidence,
                "gap": gap,
                "top_k": _safe_top_k(top_k),
                "source": recognition_source,
                "index_name": index_name,
                "index_version": index_version,
            },
            "namespace": "shadow",
        }

        collection = db[SHADOW_COLLECTION]
        await collection.update_one(
            {"request_id": request_id},
            {"$setOnInsert": record},
            upsert=True,
        )

        uploaded = bool(await asyncio.to_thread(
            uploader,
            object_key,
            image_bytes,
            content_type or "application/octet-stream",
        ))
        await collection.update_one(
            {"request_id": request_id},
            {"$set": {
                "image.upload_status": "uploaded" if uploaded else "failed",
                "image.upload_attempted_at": datetime.now(timezone.utc),
            }},
        )
    except Exception as exc:
        logger.warning("[SHADOW] coleta ignorada request_id=%s: %s", request_id, exc)
