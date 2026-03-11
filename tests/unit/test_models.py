from src.models.manifest import ManifestRecord, SupportStatus


def test_manifest_model_serializes_stable_status_values() -> None:
    record = ManifestRecord(
        relative_path="app.py",
        size_bytes=10,
        modified_time="2026-03-10T00:00:00Z",
        language="python",
        support_status=SupportStatus.SUPPORTED,
        classification_source="extension:.py",
    )

    payload = record.model_dump(mode="json")

    assert payload["support_status"] == "supported"
    assert payload["relative_path"] == "app.py"
