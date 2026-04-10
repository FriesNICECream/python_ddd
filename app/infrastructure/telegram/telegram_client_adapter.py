from app.domain.media_ingest.entities import TelegramFetchedMessage, TelegramSource
from app.domain.media_ingest.repositories import TelegramMessageReader


class TelegramClientAdapter(TelegramMessageReader):
    """Telegram 读取适配器占位实现。"""

    def fetch_incremental(self, *, source: TelegramSource, limit: int) -> list[TelegramFetchedMessage]:
        """当前先返回空结果，后续阶段再接入真实 Telegram 客户端。"""
        return []
