from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.user.entities import User


class UserRepository(ABC):
    @abstractmethod
    def add(self, *, email: str, full_name: str) -> User:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, user_id: UUID) -> User | None:
        raise NotImplementedError

    @abstractmethod
    def get_by_email(self, email: str) -> User | None:
        raise NotImplementedError
