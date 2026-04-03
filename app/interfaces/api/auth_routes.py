from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.application.auth.dto import LoginCommand, RegisterCommand
from app.application.auth.use_cases import LoginUseCase, RegisterUseCase
from app.domain.auth.exceptions import InvalidCredentialsError, UserAlreadyExistsError
from app.infrastructure.db.session import get_db_session
from app.infrastructure.repositories.auth_repository_sqlalchemy import SqlAlchemyAuthUserRepository
from app.infrastructure.security.jwt_access_token_issuer import JwtAccessTokenIssuer
from app.infrastructure.security.password_hasher import PBKDF2PasswordHasher
from app.interfaces.api.schemas import AccessTokenResponse, LoginRequest, RegisterUserRequest, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterUserRequest, db: Session = Depends(get_db_session)) -> UserResponse:
    repository = SqlAlchemyAuthUserRepository(db)
    password_hasher = PBKDF2PasswordHasher()
    use_case = RegisterUseCase(repository, password_hasher)

    try:
        user = use_case.execute(
            RegisterCommand(
                email=payload.email,
                full_name=payload.full_name,
                password=payload.password,
            )
        )
    except UserAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return UserResponse.model_validate(user.model_dump())


@router.post("/login", response_model=AccessTokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db_session)) -> AccessTokenResponse:
    repository = SqlAlchemyAuthUserRepository(db)
    password_hasher = PBKDF2PasswordHasher()
    token_issuer = JwtAccessTokenIssuer()
    use_case = LoginUseCase(repository, password_hasher, token_issuer)

    try:
        result = use_case.execute(LoginCommand(email=payload.email, password=payload.password))
    except InvalidCredentialsError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    return AccessTokenResponse.model_validate(result.model_dump())
