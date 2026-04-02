from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Python DDD"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/python_ddd"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
