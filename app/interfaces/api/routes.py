from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.application.user.dto import RegisterUserCommand
from app.application.user.use_cases import GetUserUseCase, RegisterUserUseCase, UserAlreadyExistsError
from app.infrastructure.db.session import get_db_session
from app.infrastructure.repositories.user_repository_sqlalchemy import SqlAlchemyUserRepository
from app.interfaces.api.schemas import RegisterUserRequest, UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(payload: RegisterUserRequest, db: Session = Depends(get_db_session)) -> UserResponse:
    repo = SqlAlchemyUserRepository(db)
    use_case = RegisterUserUseCase(repo)

    try:
        user = use_case.execute(RegisterUserCommand(email=payload.email, full_name=payload.full_name))
    except UserAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return UserResponse.model_validate(user.model_dump())


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: UUID, db: Session = Depends(get_db_session)) -> UserResponse:
    repo = SqlAlchemyUserRepository(db)
    use_case = GetUserUseCase(repo)
    user = use_case.execute(user_id)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserResponse.model_validate(user.model_dump())
