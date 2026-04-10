from datetime import datetime

from pydantic import BaseModel, Field

from app.domain.media_ingest.entities import CloudPlatform, CurationStatus, MediaType, ParseStatus


class CreateTelegramSourceCommand(BaseModel):
    source_key: str = Field(min_length=1, max_length=255)
    display_name: str = Field(min_length=1, max_length=255)
    schedule_minutes: int = Field(ge=1, le=1440)
    enabled: bool = True


class UpdateTelegramSourceCommand(BaseModel):
    enabled: bool


class RunTelegramIngestionCommand(BaseModel):
    source_ids: list[str] = Field(default_factory=list)
    batch_size: int | None = Field(default=None, ge=1, le=1000)


class TelegramSourceDTO(BaseModel):
    id: str
    source_key: str
    display_name: str
    enabled: bool
    schedule_minutes: int
    last_message_cursor: str | None = None
    last_synced_at: datetime | None = None
    created_at: datetime


class TelegramRawMessageDTO(BaseModel):
    id: str
    source_id: str
    message_key: str
    published_at: datetime
    text_excerpt: str
    cover_url: str | None = None
    parse_status: ParseStatus


class CloudLinkDTO(BaseModel):
    id: str
    media_resource_id: str
    source_message_id: str
    platform: CloudPlatform
    url: str
    extraction_code: str | None = None
    first_seen_at: datetime
    last_seen_at: datetime


class MediaResourceDTO(BaseModel):
    id: str
    canonical_title: str
    display_title: str
    media_type: MediaType
    cover_url: str | None = None
    scrape_profile: dict = Field(default_factory=dict)
    normalization_fingerprint: str
    curation_status: CurationStatus
    first_seen_at: datetime
    last_seen_at: datetime
    created_at: datetime
    links: list[CloudLinkDTO] = Field(default_factory=list)
    source_message_ids: list[str] = Field(default_factory=list)


class IngestionRunResultDTO(BaseModel):
    accepted: bool
    source_count: int
    message: str
