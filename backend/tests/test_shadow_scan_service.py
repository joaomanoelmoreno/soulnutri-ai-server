import hashlib

import pytest

from services import shadow_scan_service as shadow


class FakeCollection:
    def __init__(self, fail=False):
        self.fail = fail
        self.calls = []

    async def update_one(self, query, update, upsert=False):
        if self.fail:
            raise RuntimeError("mongo unavailable")
        self.calls.append((query, update, upsert))


class FakeDB:
    def __init__(self, collection):
        self.collection = collection
        self.requested = []

    def __getitem__(self, name):
        self.requested.append(name)
        assert name == shadow.SHADOW_COLLECTION
        return self.collection


@pytest.mark.asyncio
async def test_disabled_by_default_performs_no_io(monkeypatch):
    monkeypatch.delenv("SHADOW_MODE_ENABLED", raising=False)
    db = FakeDB(FakeCollection())
    uploads = []
    await shadow.persist_shadow_scan(
        db=db, image_bytes=b"image", request_id="req-1",
        predicted_dish="arroz", identified=True, score=0.9,
        confidence="alta", gap=0.2, top_k=[], width=10, height=20,
        content_type="image/jpeg", recognition_source="local_index",
        uploader=lambda *args: uploads.append(args),
    )
    assert db.requested == []
    assert uploads == []


@pytest.mark.asyncio
async def test_enabled_uses_only_shadow_collection_and_namespace(monkeypatch):
    monkeypatch.setenv("SHADOW_MODE_ENABLED", "true")
    collection = FakeCollection()
    db = FakeDB(collection)
    uploads = []
    payload = b"image-bytes"
    await shadow.persist_shadow_scan(
        db=db, image_bytes=payload, request_id="req-2",
        predicted_dish="arroz_branco", identified=True, score=0.91,
        confidence="alta", gap=0.11,
        top_k=[{"dish": "arroz_branco", "score": 0.91, "ignored": "x"}],
        width=640, height=480, content_type="image/jpeg",
        recognition_source="local_index", index_name="dish_index.json",
        uploader=lambda *args: uploads.append(args) or True,
    )
    expected_hash = hashlib.sha256(payload).hexdigest()
    assert db.requested == [shadow.SHADOW_COLLECTION]
    assert len(uploads) == 1
    assert uploads[0][0] == f"shadow/scans/objects/{expected_hash}"
    inserted = collection.calls[0][1]["$setOnInsert"]
    assert inserted["image_sha256"] == expected_hash
    assert inserted["recognition"]["top_k"] == [{"dish": "arroz_branco", "score": 0.91}]
    assert collection.calls[1][1]["$set"]["image.upload_status"] == "uploaded"


@pytest.mark.asyncio
async def test_mongo_failure_never_escapes(monkeypatch):
    monkeypatch.setenv("SHADOW_MODE_ENABLED", "true")
    await shadow.persist_shadow_scan(
        db=FakeDB(FakeCollection(fail=True)), image_bytes=b"image", request_id="req-3",
        predicted_dish=None, identified=False, score=0.0, confidence="baixa",
        gap=None, top_k=None, width=None, height=None,
        content_type="image/jpeg", recognition_source="local_index",
        uploader=lambda *args: (_ for _ in ()).throw(RuntimeError("must not run")),
    )


@pytest.mark.asyncio
async def test_r2_failure_is_recorded_and_never_escapes(monkeypatch):
    monkeypatch.setenv("SHADOW_MODE_ENABLED", "true")
    collection = FakeCollection()
    await shadow.persist_shadow_scan(
        db=FakeDB(collection), image_bytes=b"image", request_id="req-4",
        predicted_dish="quinoa", identified=True, score=0.8, confidence="media",
        gap=None, top_k=None, width=1, height=1,
        content_type="image/jpeg", recognition_source="local_index",
        uploader=lambda *args: False,
    )
    assert collection.calls[1][1]["$set"]["image.upload_status"] == "failed"
