from fastapi import FastAPI

from app.config import settings
from app.interfaces.api.routes import router as user_router

app = FastAPI(title=settings.app_name)
app.include_router(user_router, prefix="/api")


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}
