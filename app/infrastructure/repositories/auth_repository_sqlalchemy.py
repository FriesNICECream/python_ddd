from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.auth.entities import AuthUser
from app.domain.auth.repositories import AuthUserRepository
from app.infrastructure.db.models import UserModel


class SqlAlchemyAuthUserRepository(AuthUserRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, *, email: str, full_name: str, password_hash: str) -> AuthUser:
        model = UserModel(email=email, full_name=full_name, password_hash=password_hash)
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    def get_by_email(self, email: str) -> AuthUser | None:
        stmt = select(UserModel).where(UserModel.email == email)
        model = self.session.scalar(stmt)
        if not model or model.password_hash is None:
            return None
        return self._to_entity(model)

    @staticmethod
    def _to_entity(model: UserModel) -> AuthUser:
        return AuthUser(
            id=model.id,
            email=model.email,
            full_name=model.full_name,
            password_hash=model.password_hash or "",
            created_at=model.created_at,
        )
