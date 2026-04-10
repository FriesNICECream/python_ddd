from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.domain.media_ingest.entities import CloudPlatform, CurationStatus, MediaType


class RegisterUserRequest(BaseModel):
    email: EmailStr
    full_name: str
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    created_at: str


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str


class CreateTelegramSourceRequest(BaseModel):
    source_key: str = Field(min_length=1, max_length=255)
    display_name: str = Field(min_length=1, max_length=255)
    schedule_minutes: int = Field(ge=1, le=1440)
    enabled: bool = True


class ToggleTelegramSourceRequest(BaseModel):
    enabled: bool


class RunTelegramIngestionRequest(BaseModel):
    source_ids: list[str] = Field(default_factory=list)
    batch_size: int | None = Field(default=None, ge=1, le=1000)


class TelegramSourceResponse(BaseModel):
    id: str
    source_key: str
    display_name: str
    enabled: bool
    schedule_minutes: int
    last_message_cursor: str | None = None
    last_synced_at: datetime | None = None
    created_at: datetime


class CloudLinkResponse(BaseModel):
    id: str
    platform: CloudPlatform
    url: str
    extraction_code: str | None = None
    first_seen_at: datetime
    last_seen_at: datetime


class SourceMessageSummaryResponse(BaseModel):
    id: str
    source_id: str
    message_key: str
    published_at: datetime
    text_excerpt: str
    cover_url: str | None = None


class MediaResourceResponse(BaseModel):
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
    links: list[CloudLinkResponse] = Field(default_factory=list)
    source_messages: list[SourceMessageSummaryResponse] = Field(default_factory=list)


class IngestionRunResponse(BaseModel):
    accepted: bool
    source_count: int
    message: str
