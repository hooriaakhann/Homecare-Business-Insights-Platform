from shared.utils import deduplicate, normalize_record


def test_normalize_record():
    row = normalize_record({"Client ID": "C1", "Updated At": "2026-08-20T10:00:00+00:00"})
    assert row["client_id"] == "C1"
    assert "updated_at" in row


def test_deduplicate_keeps_latest():
    rows = [
        {"id": "1", "updated_at": "2026-08-20T10:00:00+00:00", "value": "old"},
        {"id": "1", "updated_at": "2026-08-20T11:00:00+00:00", "value": "new"},
    ]
    result = deduplicate(rows, ["id"], "updated_at")
    assert len(result) == 1
    assert result[0]["value"] == "new"
