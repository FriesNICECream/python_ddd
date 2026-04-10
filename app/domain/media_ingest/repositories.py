from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.media_ingest.entities import MediaResource, TelegramFetchedMessage, TelegramRawMessage, TelegramSource


class TelegramSourceRepository(ABC):
    @abstractmethod
    def add(self, *, source_key: str, display_name: str, schedule_minutes: int, enabled: bool = True) -> TelegramSource:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, source_id: UUID) -> TelegramSource | None:
        raise NotImplementedError

    @abstractmethod
    def get_by_source_key(self, source_key: str) -> TelegramSource | None:
        raise NotImplementedError

    @abstractmethod
    def list_enabled(self) -> list[TelegramSource]:
        raise NotImplementedError

    @abstractmethod
    def save(self, source: TelegramSource) -> TelegramSource:
        raise NotImplementedError


class TelegramMessageRepository(ABC):
    @abstractmethod
    def add(self, raw_message: TelegramRawMessage) -> TelegramRawMessage:
        raise NotImplementedError

    @abstractmethod
    def get_by_source_message_key(self, *, source_id: UUID, message_key: str) -> TelegramRawMessage | None:
        raise NotImplementedError

    @abstractmethod
    def save(self, raw_message: TelegramRawMessage) -> TelegramRawMessage:
        raise NotImplementedError


class MediaResourceRepository(ABC):
    @abstractmethod
    def add(self, resource: MediaResource) -> MediaResource:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, resource_id: UUID) -> MediaResource | None:
        raise NotImplementedError

    @abstractmethod
    def get_by_fingerprint(self, fingerprint: str) -> MediaResource | None:
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> list[MediaResource]:
        raise NotImplementedError

    @abstractmethod
    def save(self, resource: MediaResource) -> MediaResource:
        raise NotImplementedError


class TelegramMessageReader(ABC):
    @abstractmethod
    def fetch_incremental(self, *, source: TelegramSource, limit: int) -> list[TelegramFetchedMessage]:
        raise NotImplementedError
