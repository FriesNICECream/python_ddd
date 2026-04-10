from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import UUID

from app.domain.media_ingest.exceptions import DuplicateCloudLinkError, InvalidCursorAdvanceError


class MediaType(str, Enum):
    MOVIE = "movie"
    SERIES = "series"
    UNKNOWN = "unknown"


class CloudPlatform(str, Enum):
    BAIDU = "baidu"
    ALIYUN = "aliyun"
    OTHER = "other"


class ParseStatus(str, Enum):
    PARSED = "parsed"
    PENDING_CURATION = "pending_curation"
    IGNORED = "ignored"
    FAILED = "failed"


class CurationStatus(str, Enum):
    PENDING = "pending"
    CURATED = "curated"
    IGNORED = "ignored"


@dataclass(slots=True)
class TelegramFetchedMessage:
    source_key: str
    message_key: str
    published_at: datetime
    text_excerpt: str
    raw_payload: dict
    cover_url: str | None = None


@dataclass(slots=True)
class TelegramSource:
    id: UUID
    source_key: str
    display_name: str
    enabled: bool
    schedule_minutes: int
    last_message_cursor: str | None
    last_synced_at: datetime | None
    created_at: datetime

    def advance_cursor(self, next_cursor: str | None, synced_at: datetime) -> None:
        """只允许来源游标向前推进。"""
        if not next_cursor:
            self.last_synced_at = synced_at
            return

        if self.last_message_cursor and next_cursor < self.last_message_cursor:
            raise InvalidCursorAdvanceError("来源游标不允许回退。")

        self.last_message_cursor = next_cursor
        self.last_synced_at = synced_at

    def enable(self) -> None:
        self.enabled = True

    def disable(self) -> None:
        self.enabled = False


@dataclass(slots=True)
class TelegramRawMessage:
    id: UUID
    source_id: UUID
    message_key: str
    published_at: datetime
    text_excerpt: str
    cover_url: str | None
    raw_payload: dict
    parse_status: ParseStatus
    created_at: datetime

    def mark_pending_curation(self) -> None:
        self.parse_status = ParseStatus.PENDING_CURATION

    def mark_parsed(self) -> None:
        self.parse_status = ParseStatus.PARSED


@dataclass(slots=True)
class CloudLink:
    id: UUID
    media_resource_id: UUID
    source_message_id: UUID
    platform: CloudPlatform
    url: str
    extraction_code: str | None
    first_seen_at: datetime
    last_seen_at: datetime

    @property
    def normalized_url(self) -> str:
        return self.url.strip().lower()

    def same_identity(self, *, platform: CloudPlatform, normalized_url: str) -> bool:
        return self.platform == platform and self.normalized_url == normalized_url

    def refresh_seen_at(self, seen_at: datetime) -> None:
        if seen_at > self.last_seen_at:
            self.last_seen_at = seen_at


@dataclass(slots=True)
class MediaResource:
    id: UUID
    canonical_title: str
    display_title: str
    media_type: MediaType
    cover_url: str | None
    scrape_profile: dict
    normalization_fingerprint: str
    curation_status: CurationStatus
    first_seen_at: datetime
    last_seen_at: datetime
    created_at: datetime
    links: list[CloudLink] = field(default_factory=list)
    source_message_ids: list[UUID] = field(default_factory=list)

    def add_source_message(self, source_message_id: UUID, seen_at: datetime) -> None:
        if source_message_id not in self.source_message_ids:
            self.source_message_ids.append(source_message_id)
        if seen_at > self.last_seen_at:
            self.last_seen_at = seen_at

    def add_cloud_link(self, link: CloudLink) -> None:
        for existing in self.links:
            if existing.same_identity(platform=link.platform, normalized_url=link.normalized_url):
                raise DuplicateCloudLinkError("资源下已存在相同网盘链接。")
        self.links.append(link)

    def mark_pending_curation(self) -> None:
        self.curation_status = CurationStatus.PENDING
