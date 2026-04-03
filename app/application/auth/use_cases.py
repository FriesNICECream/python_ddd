from app.application.auth.dto import AccessTokenDTO, LoginCommand, RegisterCommand, RegisteredUserDTO
from app.domain.auth.exceptions import InvalidCredentialsError, UserAlreadyExistsError
from app.domain.auth.repositories import AuthUserRepository
from app.domain.auth.services import AccessTokenIssuer, PasswordHasher


class RegisterUseCase:
    def __init__(self, user_repository: AuthUserRepository, password_hasher: PasswordHasher) -> None:
        self.user_repository = user_repository
        self.password_hasher = password_hasher

    def execute(self, command: RegisterCommand) -> RegisteredUserDTO:
        if self.user_repository.get_by_email(command.email):
            raise UserAlreadyExistsError(f"User with email {command.email} already exists")

        password_hash = self.password_hasher.hash_password(command.password)
        user = self.user_repository.add(
            email=command.email,
            full_name=command.full_name,
            password_hash=password_hash,
        )
        return RegisteredUserDTO(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            created_at=user.created_at.isoformat(),
        )


class LoginUseCase:
    def __init__(
        self,
        user_repository: AuthUserRepository,
        password_hasher: PasswordHasher,
        access_token_issuer: AccessTokenIssuer,
    ) -> None:
        self.user_repository = user_repository
        self.password_hasher = password_hasher
        self.access_token_issuer = access_token_issuer

    def execute(self, command: LoginCommand) -> AccessTokenDTO:
        user = self.user_repository.get_by_email(command.email)
        if not user:
            raise InvalidCredentialsError("Invalid email or password")

        if not self.password_hasher.verify_password(command.password, user.password_hash):
            raise InvalidCredentialsError("Invalid email or password")

        access_token = self.access_token_issuer.issue_for_user(user_id=str(user.id), email=user.email)
        return AccessTokenDTO(access_token=access_token)
