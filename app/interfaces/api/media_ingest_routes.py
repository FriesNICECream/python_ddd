from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.application.media_ingest.dto import CreateTelegramSourceCommand, RunTelegramIngestionCommand
from app.application.media_ingest.use_cases import CreateTelegramSourceUseCase, RunTelegramIngestionUseCase
from app.infrastructure.db.session import get_db_session
from app.infrastructure.repositories.media_resource_repository_sqlalchemy import SqlAlchemyMediaResourceRepository
from app.infrastructure.repositories.telegram_message_repository_sqlalchemy import SqlAlchemyTelegramMessageRepository
from app.infrastructure.repositories.telegram_source_repository_sqlalchemy import SqlAlchemyTelegramSourceRepository
from app.infrastructure.telegram.telegram_client_adapter import TelegramClientAdapter
from app.interfaces.api.schemas import (
    CreateTelegramSourceRequest,
    IngestionRunResponse,
    RunTelegramIngestionRequest,
    TelegramSourceResponse,
)

router = APIRouter(tags=["media-ingest"])


def get_create_source_use_case(db: Session = Depends(get_db_session)) -> CreateTelegramSourceUseCase:
    repository = SqlAlchemyTelegramSourceRepository(db)
    return CreateTelegramSourceUseCase(repository)


def get_run_ingestion_use_case(db: Session = Depends(get_db_session)) -> RunTelegramIngestionUseCase:
    source_repository = SqlAlchemyTelegramSourceRepository(db)
    message_repository = SqlAlchemyTelegramMessageRepository(db)
    media_resource_repository = SqlAlchemyMediaResourceRepository(db)
    message_reader = TelegramClientAdapter()
    return RunTelegramIngestionUseCase(
        source_repository=source_repository,
        message_repository=message_repository,
        media_resource_repository=media_resource_repository,
        message_reader=message_reader,
    )


@router.get("/media-ingest/status", status_code=status.HTTP_200_OK)
def get_media_ingest_status() -> dict[str, str]:
    """用于确认媒体采集模块已装配。"""
    return {
        "feature": "telegram-media-ingest",
        "status": "us1-ready",
        "message": "媒体采集模块已装配，支持来源登记与手动触发增量采集。",
    }


@router.post("/telegram-sources", response_model=TelegramSourceResponse, status_code=status.HTTP_201_CREATED)
def create_telegram_source(
    payload: CreateTelegramSourceRequest,
    use_case: CreateTelegramSourceUseCase = Depends(get_create_source_use_case),
) -> TelegramSourceResponse:
    source = use_case.execute(
        CreateTelegramSourceCommand(
            source_key=payload.source_key,
            display_name=payload.display_name,
            schedule_minutes=payload.schedule_minutes,
            enabled=payload.enabled,
        )
    )
    return TelegramSourceResponse.model_validate(source.model_dump())


@router.post("/telegram-ingestions/run", response_model=IngestionRunResponse, status_code=status.HTTP_202_ACCEPTED)
def run_telegram_ingestion(
    payload: RunTelegramIngestionRequest,
    use_case: RunTelegramIngestionUseCase = Depends(get_run_ingestion_use_case),
) -> IngestionRunResponse:
    result = use_case.execute(
        RunTelegramIngestionCommand(
            source_ids=payload.source_ids,
            batch_size=payload.batch_size,
        )
    )
    return IngestionRunResponse.model_validate(result.model_dump())
