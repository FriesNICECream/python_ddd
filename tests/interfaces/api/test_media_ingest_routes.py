from datetime import UTC, datetime

from fastapi.testclient import TestClient

from app.application.media_ingest.dto import IngestionRunResultDTO, TelegramSourceDTO
from app.interfaces.api.media_ingest_routes import (
    get_create_source_use_case,
    get_run_ingestion_use_case,
)
from app.main import app


class FakeCreateTelegramSourceUseCase:
    def execute(self, command):  # type: ignore[no-untyped-def]
        return TelegramSourceDTO(
            id="source-1",
            source_key=command.source_key,
            display_name=command.display_name,
            enabled=command.enabled,
            schedule_minutes=command.schedule_minutes,
            last_message_cursor=None,
            last_synced_at=None,
            created_at=datetime.now(UTC),
        )


class FakeRunTelegramIngestionUseCase:
    def execute(self, command):  # type: ignore[no-untyped-def]
        return IngestionRunResultDTO(
            accepted=True,
            source_count=len(command.source_ids) or 1,
            message="Telegram 增量采集任务已执行。",
        )


def test_create_telegram_source_endpoint_should_return_created_source() -> None:
    app.dependency_overrides[get_create_source_use_case] = lambda: FakeCreateTelegramSourceUseCase()
    client = TestClient(app)

    response = client.post(
        "/api/telegram-sources",
        json={
            "source_key": "group-001",
            "display_name": "影视群 1",
            "schedule_minutes": 30,
            "enabled": True,
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 201
    assert response.json()["source_key"] == "group-001"
    assert response.json()["display_name"] == "影视群 1"


def test_run_telegram_ingestion_endpoint_should_return_accepted_result() -> None:
    app.dependency_overrides[get_run_ingestion_use_case] = lambda: FakeRunTelegramIngestionUseCase()
    client = TestClient(app)

    response = client.post(
        "/api/telegram-ingestions/run",
        json={
            "source_ids": ["11111111-1111-1111-1111-111111111111"],
            "batch_size": 50,
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 202
    assert response.json()["accepted"] is True
    assert response.json()["source_count"] == 1
