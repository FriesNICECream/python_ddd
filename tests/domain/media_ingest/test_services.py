from datetime import datetime, timezone
from uuid import uuid4

import pytest

from app.domain.media_ingest.entities import CloudPlatform, MediaType, TelegramSource
from app.domain.media_ingest.exceptions import DuplicateCloudLinkError, InvalidCursorAdvanceError
from app.domain.media_ingest.services import MediaResourceMatcher, detect_cloud_platform, normalize_title


def test_normalize_title_removes_common_noise() -> None:
    normalized = normalize_title(" [电影] 速度 与 激情  ")

    assert normalized == "电影 速度 与 激情"


def test_detect_cloud_platform_supports_baidu_and_aliyun() -> None:
    assert detect_cloud_platform("https://pan.baidu.com/s/example") == CloudPlatform.BAIDU
    assert detect_cloud_platform("https://www.alipan.com/s/example") == CloudPlatform.ALIYUN


def test_source_cursor_cannot_move_backward() -> None:
    source = TelegramSource(
        id=uuid4(),
        source_key="group-001",
        display_name="测试来源",
        enabled=True,
        schedule_minutes=30,
        last_message_cursor="200",
        last_synced_at=None,
        created_at=datetime.now(timezone.utc),
    )

    with pytest.raises(InvalidCursorAdvanceError):
        source.advance_cursor("199", datetime.now(timezone.utc))


def test_media_resource_rejects_duplicate_cloud_link() -> None:
    matcher = MediaResourceMatcher()
    source_message_id = uuid4()
    resource = matcher.create_pending_resource(
        resource_id=uuid4(),
        title="流浪地球",
        media_type=MediaType.MOVIE,
        cover_url=None,
        first_seen_at=datetime.now(timezone.utc),
        source_message_id=source_message_id,
    )
    link = matcher.build_cloud_link(
        link_id=uuid4(),
        media_resource_id=resource.id,
        source_message_id=source_message_id,
        url="https://pan.baidu.com/s/demo",
        extraction_code="1234",
        seen_at=datetime.now(timezone.utc),
    )

    resource.add_cloud_link(link)

    with pytest.raises(DuplicateCloudLinkError):
        resource.add_cloud_link(link)
