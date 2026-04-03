from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Python DDD"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/python_ddd"
    access_token_secret: str = "change-me-in-production"
    access_token_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
