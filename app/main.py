from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.interfaces.api.auth_routes import router as auth_router
from app.interfaces.api.media_ingest_routes import router as media_ingest_router
from app.interfaces.api.routes import router as user_router

app = FastAPI(title=settings.app_name)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)
app.include_router(auth_router, prefix="/api")
app.include_router(user_router, prefix="/api")
app.include_router(media_ingest_router, prefix="/api")


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}
