import re
from dataclasses import replace
from datetime import datetime
from typing import Iterable
from uuid import UUID

from app.domain.media_ingest.entities import (
    CloudLink,
    CloudPlatform,
    CurationStatus,
    MediaResource,
    MediaType,
    ParseStatus,
    TelegramRawMessage,
)
from app.domain.media_ingest.exceptions import EmptyCanonicalTitleError

_TITLE_NOISE_PATTERN = re.compile(r"[\[\]()（）【】\-_·|]+")
_MULTI_SPACE_PATTERN = re.compile(r"\s+")


def normalize_title(title: str) -> str:
    """归一化标题，尽量消除常见噪声字符。"""
    normalized = _TITLE_NOISE_PATTERN.sub(" ", title).strip().lower()
    normalized = _MULTI_SPACE_PATTERN.sub(" ", normalized)
    if not normalized:
        raise EmptyCanonicalTitleError("标题不能为空或仅包含噪声字符。")
    return normalized


def build_resource_fingerprint(title: str, media_type: MediaType) -> str:
    """基于标题和类型构造资源匹配指纹。"""
    return f"{media_type.value}:{normalize_title(title)}"


def detect_cloud_platform(url: str) -> CloudPlatform:
    """根据链接域名识别网盘平台。"""
    normalized = url.strip().lower()
    if "pan.baidu.com" in normalized:
        return CloudPlatform.BAIDU
    if "aliyundrive.com" in normalized or "alipan.com" in normalized:
        return CloudPlatform.ALIYUN
    return CloudPlatform.OTHER


def should_mark_pending_curation(*, title: str | None, links: Iterable[str]) -> bool:
    """字段不完整时默认进入待整理状态。"""
    valid_links = [link for link in links if link.strip()]
    return not title or not title.strip() or not valid_links


class MediaResourceMatcher:
    """负责创建资源聚合与链接归并的共享领域服务。"""

    def create_pending_resource(
        self,
        *,
        resource_id: UUID,
        title: str,
        media_type: MediaType,
        cover_url: str | None,
        first_seen_at: datetime,
        source_message_id: UUID,
        scrape_profile: dict | None = None,
    ) -> MediaResource:
        canonical_title = normalize_title(title)
        resource = MediaResource(
            id=resource_id,
            canonical_title=canonical_title,
            display_title=title.strip(),
            media_type=media_type,
            cover_url=cover_url,
            scrape_profile=scrape_profile or {},
            normalization_fingerprint=build_resource_fingerprint(title, media_type),
            curation_status=CurationStatus.PENDING,
            first_seen_at=first_seen_at,
            last_seen_at=first_seen_at,
            created_at=first_seen_at,
        )
        resource.add_source_message(source_message_id, first_seen_at)
        return resource

    def merge_raw_message(
        self,
        *,
        raw_message: TelegramRawMessage,
        resource: MediaResource,
    ) -> MediaResource:
        """将来源消息附着到已有资源。"""
        merged = replace(resource, links=list(resource.links), source_message_ids=list(resource.source_message_ids))
        merged.add_source_message(raw_message.id, raw_message.published_at)
        return merged

    def build_cloud_link(
        self,
        *,
        link_id: UUID,
        media_resource_id: UUID,
        source_message_id: UUID,
        url: str,
        extraction_code: str | None,
        seen_at: datetime,
    ) -> CloudLink:
        return CloudLink(
            id=link_id,
            media_resource_id=media_resource_id,
            source_message_id=source_message_id,
            platform=detect_cloud_platform(url),
            url=url.strip(),
            extraction_code=extraction_code,
            first_seen_at=seen_at,
            last_seen_at=seen_at,
        )


def build_pending_raw_message(
    *,
    message_id: UUID,
    source_id: UUID,
    message_key: str,
    published_at: datetime,
    text_excerpt: str,
    raw_payload: dict,
    cover_url: str | None = None,
) -> TelegramRawMessage:
    """为后续解析阶段创建原始消息实体。"""
    parse_status = ParseStatus.PENDING_CURATION if not text_excerpt.strip() else ParseStatus.PARSED
    return TelegramRawMessage(
        id=message_id,
        source_id=source_id,
        message_key=message_key,
        published_at=published_at,
        text_excerpt=text_excerpt,
        cover_url=cover_url,
        raw_payload=raw_payload,
        parse_status=parse_status,
        created_at=published_at,
    )
