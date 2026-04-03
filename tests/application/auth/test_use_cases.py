from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest

from app.application.auth.dto import LoginCommand, RegisterCommand
from app.application.auth.use_cases import LoginUseCase, RegisterUseCase
from app.domain.auth.entities import AuthUser
from app.domain.auth.exceptions import InvalidCredentialsError, UserAlreadyExistsError
from app.domain.auth.repositories import AuthUserRepository
from app.domain.auth.services import AccessTokenIssuer, PasswordHasher


class InMemoryAuthUserRepository(AuthUserRepository):
    def __init__(self) -> None:
        self.users_by_email: dict[str, AuthUser] = {}

    def add(self, *, email: str, full_name: str, password_hash: str) -> AuthUser:
        user = AuthUser(
            id=uuid4(),
            email=email,
            full_name=full_name,
            password_hash=password_hash,
            created_at=datetime.now(UTC),
        )
        self.users_by_email[email] = user
        return user

    def get_by_email(self, email: str) -> AuthUser | None:
        return self.users_by_email.get(email)


class FakePasswordHasher(PasswordHasher):
    def hash_password(self, password: str) -> str:
        return f"hashed::{password}"

    def verify_password(self, password: str, password_hash: str) -> bool:
        return password_hash == f"hashed::{password}"


@dataclass(slots=True)
class FakeAccessTokenIssuer(AccessTokenIssuer):
    issued_for_user_id: str | None = None

    def issue_for_user(self, *, user_id: str, email: str) -> str:
        self.issued_for_user_id = user_id
        return f"token-for::{email}"


def test_register_use_case_should_create_user_with_hashed_password() -> None:
    repository = InMemoryAuthUserRepository()
    use_case = RegisterUseCase(repository, FakePasswordHasher())

    result = use_case.execute(
        RegisterCommand(email="alice@example.com", full_name="Alice", password="strong-pass")
    )

    saved_user = repository.get_by_email("alice@example.com")
    assert result.email == "alice@example.com"
    assert saved_user is not None
    assert saved_user.password_hash == "hashed::strong-pass"


def test_register_use_case_should_reject_duplicate_email() -> None:
    repository = InMemoryAuthUserRepository()
    repository.users_by_email["alice@example.com"] = AuthUser(
        id=uuid4(),
        email="alice@example.com",
        full_name="Alice",
        password_hash="hashed::strong-pass",
        created_at=datetime.now(UTC),
    )
    use_case = RegisterUseCase(repository, FakePasswordHasher())

    with pytest.raises(UserAlreadyExistsError):
        use_case.execute(
            RegisterCommand(email="alice@example.com", full_name="Alice", password="strong-pass")
        )


def test_login_use_case_should_issue_access_token() -> None:
    repository = InMemoryAuthUserRepository()
    user_id = uuid4()
    repository.users_by_email["alice@example.com"] = AuthUser(
        id=user_id,
        email="alice@example.com",
        full_name="Alice",
        password_hash="hashed::strong-pass",
        created_at=datetime.now(UTC),
    )
    token_issuer = FakeAccessTokenIssuer()
    use_case = LoginUseCase(repository, FakePasswordHasher(), token_issuer)

    result = use_case.execute(LoginCommand(email="alice@example.com", password="strong-pass"))

    assert result.access_token == "token-for::alice@example.com"
    assert result.token_type == "bearer"
    assert token_issuer.issued_for_user_id == str(user_id)


def test_login_use_case_should_reject_invalid_password() -> None:
    repository = InMemoryAuthUserRepository()
    repository.users_by_email["alice@example.com"] = AuthUser(
        id=uuid4(),
        email="alice@example.com",
        full_name="Alice",
        password_hash="hashed::strong-pass",
        created_at=datetime.now(UTC),
    )
    use_case = LoginUseCase(repository, FakePasswordHasher(), FakeAccessTokenIssuer())

    with pytest.raises(InvalidCredentialsError):
        use_case.execute(LoginCommand(email="alice@example.com", password="wrong-pass"))
