from uuid import UUID

from app.application.user.dto import UserDTO
from app.domain.user.repositories import UserRepository


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
