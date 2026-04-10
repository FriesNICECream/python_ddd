from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.media_ingest.entities import ParseStatus, TelegramRawMessage
from app.domain.media_ingest.repositories import TelegramMessageRepository
from app.infrastructure.db.models import TelegramRawMessageModel


class SqlAlchemyTelegramMessageRepository(TelegramMessageRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, raw_message: TelegramRawMessage) -> TelegramRawMessage:
        model = TelegramRawMessageModel(
            id=raw_message.id,
            source_id=raw_message.source_id,
            message_key=raw_message.message_key,
            published_at=raw_message.published_at,
            text_excerpt=raw_message.text_excerpt,
            cover_url=raw_message.cover_url,
            raw_payload=raw_message.raw_payload,
            parse_status=raw_message.parse_status.value,
            created_at=raw_message.created_at,
        )
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    def get_by_source_message_key(self, *, source_id: UUID, message_key: str) -> TelegramRawMessage | None:
        stmt = select(TelegramRawMessageModel).where(
            TelegramRawMessageModel.source_id == source_id,
            TelegramRawMessageModel.message_key == message_key,
        )
        model = self.session.scalar(stmt)
        return self._to_entity(model) if model else None

    def save(self, raw_message: TelegramRawMessage) -> TelegramRawMessage:
        model = self.session.get(TelegramRawMessageModel, raw_message.id)
        if model is None:
            raise ValueError("待保存的原始消息不存在。")

        model.text_excerpt = raw_message.text_excerpt
        model.cover_url = raw_message.cover_url
        model.raw_payload = raw_message.raw_payload
        model.parse_status = raw_message.parse_status.value
        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    @staticmethod
    def _to_entity(model: TelegramRawMessageModel) -> TelegramRawMessage:
        return TelegramRawMessage(
            id=model.id,
            source_id=model.source_id,
            message_key=model.message_key,
            published_at=model.published_at,
            text_excerpt=model.text_excerpt,
            cover_url=model.cover_url,
            raw_payload=model.raw_payload,
            parse_status=ParseStatus(model.parse_status),
            created_at=model.created_at,
        )
