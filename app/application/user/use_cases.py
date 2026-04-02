from uuid import UUID

from app.application.user.dto import RegisterUserCommand, UserDTO
from app.domain.user.repositories import UserRepository


class UserAlreadyExistsError(Exception):
    pass


class RegisterUserUseCase:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    def execute(self, command: RegisterUserCommand) -> UserDTO:
        if self.user_repository.get_by_email(command.email):
            raise UserAlreadyExistsError(f"User with email {command.email} already exists")

        user = self.user_repository.add(email=command.email, full_name=command.full_name)
        return UserDTO(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            created_at=user.created_at.isoformat(),
        )


class GetUserUseCase:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    def execute(self, user_id: UUID) -> UserDTO | None:
        user = self.user_repository.get_by_id(user_id)
        if not user:
            return None
        return UserDTO(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            created_at=user.created_at.isoformat(),
        )
