from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.application.media_ingest.dto import CreateTelegramSourceCommand, RunTelegramIngestionCommand
from app.application.media_ingest.use_cases import CreateTelegramSourceUseCase, RunTelegramIngestionUseCase
from app.domain.media_ingest.entities import CurationStatus, MediaResource, TelegramFetchedMessage, TelegramRawMessage, TelegramSource
from app.domain.media_ingest.repositories import (
    MediaResourceRepository,
    TelegramMessageReader,
    TelegramMessageRepository,
    TelegramSourceRepository,
)


class InMemoryTelegramSourceRepository(TelegramSourceRepository):
    def __init__(self) -> None:
        self.sources: dict[UUID, TelegramSource] = {}

    def add(self, *, source_key: str, display_name: str, schedule_minutes: int, enabled: bool = True) -> TelegramSource:
        source = TelegramSource(
            id=uuid4(),
            source_key=source_key,
            display_name=display_name,
            enabled=enabled,
            schedule_minutes=schedule_minutes,
            last_message_cursor=None,
            last_synced_at=None,
            created_at=datetime.now(UTC),
        )
        self.sources[source.id] = source
        return source

    def get_by_id(self, source_id: UUID) -> TelegramSource | None:
        return self.sources.get(source_id)

    def get_by_source_key(self, source_key: str) -> TelegramSource | None:
        return next((source for source in self.sources.values() if source.source_key == source_key), None)

    def list_enabled(self) -> list[TelegramSource]:
        return [source for source in self.sources.values() if source.enabled]

    def save(self, source: TelegramSource) -> TelegramSource:
        self.sources[source.id] = source
        return source


class InMemoryTelegramMessageRepository(TelegramMessageRepository):
    def __init__(self) -> None:
        self.messages: dict[tuple[UUID, str], TelegramRawMessage] = {}

    def add(self, raw_message: TelegramRawMessage) -> TelegramRawMessage:
        self.messages[(raw_message.source_id, raw_message.message_key)] = raw_message
        return raw_message

    def get_by_source_message_key(self, *, source_id: UUID, message_key: str) -> TelegramRawMessage | None:
        return self.messages.get((source_id, message_key))

    def save(self, raw_message: TelegramRawMessage) -> TelegramRawMessage:
        self.messages[(raw_message.source_id, raw_message.message_key)] = raw_message
        return raw_message


class InMemoryMediaResourceRepository(MediaResourceRepository):
    def __init__(self) -> None:
        self.resources: dict[UUID, MediaResource] = {}

    def add(self, resource: MediaResource) -> MediaResource:
        self.resources[resource.id] = resource
        return resource

    def get_by_id(self, resource_id: UUID) -> MediaResource | None:
        return self.resources.get(resource_id)

    def get_by_fingerprint(self, fingerprint: str) -> MediaResource | None:
        return next((resource for resource in self.resources.values() if resource.normalization_fingerprint == fingerprint), None)

    def list_all(self) -> list[MediaResource]:
        return list(self.resources.values())

    def save(self, resource: MediaResource) -> MediaResource:
        self.resources[resource.id] = resource
        return resource


@dataclass(slots=True)
class FakeTelegramMessageReader(TelegramMessageReader):
    messages_by_source_key: dict[str, list[TelegramFetchedMessage]]

    def fetch_incremental(self, *, source: TelegramSource, limit: int) -> list[TelegramFetchedMessage]:
        return self.messages_by_source_key.get(source.source_key, [])[:limit]


def test_create_source_use_case_should_create_enabled_source() -> None:
    repository = InMemoryTelegramSourceRepository()
    use_case = CreateTelegramSourceUseCase(repository)

    result = use_case.execute(
        CreateTelegramSourceCommand(
            source_key="group-001",
            display_name="影视群 1",
            schedule_minutes=30,
        )
    )

    assert result.source_key == "group-001"
    assert result.enabled is True
    assert repository.get_by_source_key("group-001") is not None


def test_run_ingestion_use_case_should_store_raw_message_and_resource() -> None:
    source_repository = InMemoryTelegramSourceRepository()
    message_repository = InMemoryTelegramMessageRepository()
    resource_repository = InMemoryMediaResourceRepository()
    source = source_repository.add(
        source_key="group-001",
        display_name="影视群 1",
        schedule_minutes=30,
        enabled=True,
    )
    reader = FakeTelegramMessageReader(
        messages_by_source_key={
            "group-001": [
                TelegramFetchedMessage(
                    source_key="group-001",
                    message_key="101",
                    published_at=datetime.now(UTC),
                    text_excerpt="流浪地球 2",
                    raw_payload={"text": "流浪地球 2"},
                    cover_url="https://example.com/cover.jpg",
                )
            ]
        }
    )
    use_case = RunTelegramIngestionUseCase(
        source_repository=source_repository,
        message_repository=message_repository,
        media_resource_repository=resource_repository,
        message_reader=reader,
    )

    result = use_case.execute(RunTelegramIngestionCommand())

    assert result.accepted is True
    assert result.source_count == 1
    assert message_repository.get_by_source_message_key(source_id=source.id, message_key="101") is not None
    assert len(resource_repository.list_all()) == 1
    assert resource_repository.list_all()[0].curation_status == CurationStatus.PENDING
