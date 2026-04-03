from abc import ABC, abstractmethod


class PasswordHasher(ABC):
    @abstractmethod
    def hash_password(self, password: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def verify_password(self, password: str, password_hash: str) -> bool:
        raise NotImplementedError


class AccessTokenIssuer(ABC):
    @abstractmethod
    def issue_for_user(self, *, user_id: str, email: str) -> str:
        raise NotImplementedError
