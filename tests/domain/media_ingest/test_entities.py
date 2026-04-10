from datetime import UTC, datetime
from uuid import uuid4

from app.domain.media_ingest.entities import ParseStatus, TelegramSource
from app.domain.media_ingest.services import build_pending_raw_message


def test_source_cursor_advances_forward() -> None:
    source = TelegramSource(
        id=uuid4(),
        source_key="group-001",
        display_name="测试来源",
        enabled=True,
        schedule_minutes=30,
        last_message_cursor="10",
        last_synced_at=None,
        created_at=datetime.now(UTC),
    )

    source.advance_cursor("12", datetime.now(UTC))

    assert source.last_message_cursor == "12"
    assert source.last_synced_at is not None


def test_empty_text_message_should_be_marked_pending_curation() -> None:
    raw_message = build_pending_raw_message(
        message_id=uuid4(),
        source_id=uuid4(),
        message_key="1",
        published_at=datetime.now(UTC),
        text_excerpt="   ",
        raw_payload={"text": ""},
    )

    assert raw_message.parse_status == ParseStatus.PENDING_CURATION
