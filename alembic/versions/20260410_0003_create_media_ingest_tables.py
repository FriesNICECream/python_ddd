"""create media ingest tables

Revision ID: 20260410_0003
Revises: 20260403_0002
Create Date: 2026-04-10
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "20260410_0003"
down_revision: Union[str, None] = "20260403_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "telegram_sources",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("source_key", sa.String(length=255), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("schedule_minutes", sa.Integer(), nullable=False, server_default=sa.text("30")),
        sa.Column("last_message_cursor", sa.String(length=255), nullable=True),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_telegram_sources_source_key", "telegram_sources", ["source_key"], unique=True)

    op.create_table(
        "telegram_raw_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("message_key", sa.String(length=255), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("text_excerpt", sa.Text(), nullable=False),
        sa.Column("cover_url", sa.Text(), nullable=True),
        sa.Column("raw_payload", sa.JSON(), nullable=False),
        sa.Column("parse_status", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["source_id"], ["telegram_sources.id"]),
        sa.UniqueConstraint("source_id", "message_key", name="uq_telegram_raw_messages_source_message"),
    )
    op.create_index("ix_telegram_raw_messages_source_id", "telegram_raw_messages", ["source_id"], unique=False)
    op.create_index("ix_telegram_raw_messages_parse_status", "telegram_raw_messages", ["parse_status"], unique=False)

    op.create_table(
        "media_resources",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("canonical_title", sa.String(length=255), nullable=False),
        sa.Column("display_title", sa.String(length=255), nullable=False),
        sa.Column("media_type", sa.String(length=64), nullable=False),
        sa.Column("cover_url", sa.Text(), nullable=True),
        sa.Column("scrape_profile", sa.JSON(), nullable=False),
        sa.Column("normalization_fingerprint", sa.String(length=255), nullable=False),
        sa.Column("curation_status", sa.String(length=64), nullable=False),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_media_resources_media_type", "media_resources", ["media_type"], unique=False)
    op.create_index(
        "ix_media_resources_normalization_fingerprint",
        "media_resources",
        ["normalization_fingerprint"],
        unique=True,
    )
    op.create_index("ix_media_resources_curation_status", "media_resources", ["curation_status"], unique=False)

    op.create_table(
        "cloud_links",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("media_resource_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_message_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("platform", sa.String(length=64), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("extraction_code", sa.String(length=32), nullable=True),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["media_resource_id"], ["media_resources.id"]),
        sa.ForeignKeyConstraint(["source_message_id"], ["telegram_raw_messages.id"]),
        sa.UniqueConstraint("media_resource_id", "platform", "url", name="uq_cloud_links_resource_platform_url"),
    )
    op.create_index("ix_cloud_links_media_resource_id", "cloud_links", ["media_resource_id"], unique=False)
    op.create_index("ix_cloud_links_source_message_id", "cloud_links", ["source_message_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_cloud_links_source_message_id", table_name="cloud_links")
    op.drop_index("ix_cloud_links_media_resource_id", table_name="cloud_links")
    op.drop_table("cloud_links")

    op.drop_index("ix_media_resources_curation_status", table_name="media_resources")
    op.drop_index("ix_media_resources_normalization_fingerprint", table_name="media_resources")
    op.drop_index("ix_media_resources_media_type", table_name="media_resources")
    op.drop_table("media_resources")

    op.drop_index("ix_telegram_raw_messages_parse_status", table_name="telegram_raw_messages")
    op.drop_index("ix_telegram_raw_messages_source_id", table_name="telegram_raw_messages")
    op.drop_table("telegram_raw_messages")

    op.drop_index("ix_telegram_sources_source_key", table_name="telegram_sources")
    op.drop_table("telegram_sources")
