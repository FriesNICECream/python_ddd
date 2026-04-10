import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class TelegramSourceModel(Base):
    __tablename__ = "telegram_sources"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    schedule_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=30, server_default="30")
    last_message_cursor: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    raw_messages: Mapped[list["TelegramRawMessageModel"]] = relationship(back_populates="source")


class TelegramRawMessageModel(Base):
    __tablename__ = "telegram_raw_messages"
    __table_args__ = (UniqueConstraint("source_id", "message_key", name="uq_telegram_raw_messages_source_message"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("telegram_sources.id"), nullable=False, index=True)
    message_key: Mapped[str] = mapped_column(String(255), nullable=False)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    text_excerpt: Mapped[str] = mapped_column(Text, nullable=False)
    cover_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    parse_status: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    source: Mapped["TelegramSourceModel"] = relationship(back_populates="raw_messages")
    links: Mapped[list["CloudLinkModel"]] = relationship(back_populates="source_message")


class MediaResourceModel(Base):
    __tablename__ = "media_resources"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    canonical_title: Mapped[str] = mapped_column(String(255), nullable=False)
    display_title: Mapped[str] = mapped_column(String(255), nullable=False)
    media_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    cover_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    scrape_profile: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    normalization_fingerprint: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    curation_status: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    links: Mapped[list["CloudLinkModel"]] = relationship(back_populates="resource")


class CloudLinkModel(Base):
    __tablename__ = "cloud_links"
    __table_args__ = (UniqueConstraint("media_resource_id", "platform", "url", name="uq_cloud_links_resource_platform_url"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    media_resource_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("media_resources.id"), nullable=False, index=True)
    source_message_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("telegram_raw_messages.id"),
        nullable=False,
        index=True,
    )
    platform: Mapped[str] = mapped_column(String(64), nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    extraction_code: Mapped[str | None] = mapped_column(String(32), nullable=True)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    resource: Mapped["MediaResourceModel"] = relationship(back_populates="links")
    source_message: Mapped["TelegramRawMessageModel"] = relationship(back_populates="links")
