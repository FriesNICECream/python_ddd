from app.application.media_ingest.dto import RunTelegramIngestionCommand
from app.application.media_ingest.use_cases import RunTelegramIngestionUseCase


class MediaIngestScheduler:
    """统一复用应用层采集用例的调度器适配器。"""

    def __init__(self, run_use_case: RunTelegramIngestionUseCase) -> None:
        self.run_use_case = run_use_case

    def run_enabled_sources(self, *, batch_size: int | None = None) -> None:
        self.run_use_case.execute(
            RunTelegramIngestionCommand(
                source_ids=[],
                batch_size=batch_size,
            )
        )
