from abc import ABC, abstractmethod

from app.domain.auth.entities import AuthUser


class AuthUserRepository(ABC):
    @abstractmethod
    def add(self, *, email: str, full_name: str, password_hash: str) -> AuthUser:
        raise NotImplementedError

    @abstractmethod
    def get_by_email(self, email: str) -> AuthUser | None:
        raise NotImplementedError
