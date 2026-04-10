from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.application.media_ingest.dto import (
    CreateTelegramSourceCommand,
    IngestionRunResultDTO,
    RunTelegramIngestionCommand,
    TelegramSourceDTO,
)
from app.domain.media_ingest.entities import MediaType
from app.domain.media_ingest.repositories import (
    MediaResourceRepository,
    TelegramMessageReader,
    TelegramMessageRepository,
    TelegramSourceRepository,
)
from app.domain.media_ingest.services import MediaResourceMatcher, build_pending_raw_message


class CreateTelegramSourceUseCase:
    def __init__(self, source_repository: TelegramSourceRepository) -> None:
        self.source_repository = source_repository

    def execute(self, command: CreateTelegramSourceCommand) -> TelegramSourceDTO:
        source = self.source_repository.add(
            source_key=command.source_key,
            display_name=command.display_name,
            schedule_minutes=command.schedule_minutes,
            enabled=command.enabled,
        )
        return TelegramSourceDTO(
            id=str(source.id),
            source_key=source.source_key,
            display_name=source.display_name,
            enabled=source.enabled,
            schedule_minutes=source.schedule_minutes,
            last_message_cursor=source.last_message_cursor,
            last_synced_at=source.last_synced_at,
            created_at=source.created_at,
        )


class RunTelegramIngestionUseCase:
    def __init__(
        self,
        source_repository: TelegramSourceRepository,
        message_repository: TelegramMessageRepository,
        media_resource_repository: MediaResourceRepository,
        message_reader: TelegramMessageReader,
        matcher: MediaResourceMatcher | None = None,
    ) -> None:
        self.source_repository = source_repository
        self.message_repository = message_repository
        self.media_resource_repository = media_resource_repository
        self.message_reader = message_reader
        self.matcher = matcher or MediaResourceMatcher()

    def execute(self, command: RunTelegramIngestionCommand) -> IngestionRunResultDTO:
        selected_sources = self._select_sources(command.source_ids)
        processed_source_count = 0

        for source in selected_sources:
            fetched_messages = self.message_reader.fetch_incremental(
                source=source,
                limit=command.batch_size or 100,
            )
            if not fetched_messages:
                continue

            latest_cursor = source.last_message_cursor
            for fetched_message in fetched_messages:
                if self.message_repository.get_by_source_message_key(
                    source_id=source.id,
                    message_key=fetched_message.message_key,
                ):
                    latest_cursor = self._next_cursor(latest_cursor, fetched_message.message_key)
                    continue

                raw_message = build_pending_raw_message(
                    message_id=uuid4(),
                    source_id=source.id,
                    message_key=fetched_message.message_key,
                    published_at=fetched_message.published_at,
                    text_excerpt=fetched_message.text_excerpt,
                    raw_payload=fetched_message.raw_payload,
                    cover_url=fetched_message.cover_url,
                )
                saved_message = self.message_repository.add(raw_message)

                if fetched_message.text_excerpt.strip():
                    resource = self.matcher.create_pending_resource(
                        resource_id=uuid4(),
                        title=self._extract_display_title(fetched_message.text_excerpt),
                        media_type=MediaType.UNKNOWN,
                        cover_url=fetched_message.cover_url,
                        first_seen_at=fetched_message.published_at,
                        source_message_id=saved_message.id,
                        scrape_profile={"source": "telegram"},
                    )
                    self.media_resource_repository.add(resource)

                latest_cursor = self._next_cursor(latest_cursor, fetched_message.message_key)

            source.advance_cursor(latest_cursor, datetime.now(UTC))
            self.source_repository.save(source)
            processed_source_count += 1

        return IngestionRunResultDTO(
            accepted=True,
            source_count=processed_source_count,
            message="Telegram 增量采集任务已执行。",
        )

    def _select_sources(self, source_ids: list[str]) -> list:
        if not source_ids:
            return self.source_repository.list_enabled()

        selected_sources = []
        for source_id in source_ids:
            source = self.source_repository.get_by_id(UUID(source_id))
            if source and source.enabled:
                selected_sources.append(source)
        return selected_sources

    @staticmethod
    def _extract_display_title(text_excerpt: str) -> str:
        for line in text_excerpt.splitlines():
            cleaned = line.strip()
            if cleaned:
                return cleaned[:255]
        return text_excerpt.strip()[:255]

    @staticmethod
    def _next_cursor(current_cursor: str | None, candidate_cursor: str) -> str:
        if current_cursor is None:
            return candidate_cursor
        if current_cursor.isdigit() and candidate_cursor.isdigit():
            return str(max(int(current_cursor), int(candidate_cursor)))
        return max(current_cursor, candidate_cursor)
