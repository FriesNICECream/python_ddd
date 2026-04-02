from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.user.entities import User
from app.domain.user.repositories import UserRepository
from app.infrastructure.db.models import UserModel


class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, *, email: str, full_name: str) -> User:
        model = UserModel(email=email, full_name=full_name)
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    def get_by_id(self, user_id: UUID) -> User | None:
        model = self.session.get(UserModel, user_id)
        return self._to_entity(model) if model else None

    def get_by_email(self, email: str) -> User | None:
        stmt = select(UserModel).where(UserModel.email == email)
        model = self.session.scalar(stmt)
        return self._to_entity(model) if model else None

    @staticmethod
    def _to_entity(model: UserModel) -> User:
        return User(
            id=model.id,
            email=model.email,
            full_name=model.full_name,
            created_at=model.created_at,
        )
