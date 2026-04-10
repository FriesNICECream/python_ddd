from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.media_ingest.entities import TelegramSource
from app.domain.media_ingest.repositories import TelegramSourceRepository
from app.infrastructure.db.models import TelegramSourceModel


class SqlAlchemyTelegramSourceRepository(TelegramSourceRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, *, source_key: str, display_name: str, schedule_minutes: int, enabled: bool = True) -> TelegramSource:
        model = TelegramSourceModel(
            source_key=source_key,
            display_name=display_name,
            schedule_minutes=schedule_minutes,
            enabled=enabled,
        )
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    def get_by_id(self, source_id: UUID) -> TelegramSource | None:
        model = self.session.get(TelegramSourceModel, source_id)
        return self._to_entity(model) if model else None

    def get_by_source_key(self, source_key: str) -> TelegramSource | None:
        stmt = select(TelegramSourceModel).where(TelegramSourceModel.source_key == source_key)
        model = self.session.scalar(stmt)
        return self._to_entity(model) if model else None

    def list_enabled(self) -> list[TelegramSource]:
        stmt = select(TelegramSourceModel).where(TelegramSourceModel.enabled.is_(True)).order_by(TelegramSourceModel.created_at)
        return [self._to_entity(model) for model in self.session.scalars(stmt)]

    def save(self, source: TelegramSource) -> TelegramSource:
        model = self.session.get(TelegramSourceModel, source.id)
        if model is None:
            raise ValueError("待保存的来源不存在。")

        model.display_name = source.display_name
        model.enabled = source.enabled
        model.schedule_minutes = source.schedule_minutes
        model.last_message_cursor = source.last_message_cursor
        model.last_synced_at = source.last_synced_at
        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    @staticmethod
    def _to_entity(model: TelegramSourceModel) -> TelegramSource:
        return TelegramSource(
            id=model.id,
            source_key=model.source_key,
            display_name=model.display_name,
            enabled=model.enabled,
            schedule_minutes=model.schedule_minutes,
            last_message_cursor=model.last_message_cursor,
            last_synced_at=model.last_synced_at,
            created_at=model.created_at,
        )
