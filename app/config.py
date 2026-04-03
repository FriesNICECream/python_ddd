from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Python DDD"
    app_env: Literal["dev", "prod"] = "dev"
    database_url: str | None = None
    dev_database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/python_ddd"
    prod_database_url: str = "postgresql+psycopg://python_ddd_pass_001:python_ddd_pass_001@localhost:5432/python_ddd"
    access_token_secret: str = "change-me-in-production"
    access_token_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    cors_allow_origins: list[str] = ["*"]
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]
    cors_allow_credentials: bool = False

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @model_validator(mode="after")
    def apply_database_url_by_env(self) -> "Settings":
        """兼容旧配置，并按环境选择数据库连接。"""
        if self.database_url:
            return self

        if self.app_env == "prod":
            self.database_url = self.prod_database_url
            return self

        self.database_url = self.dev_database_url
        return self


settings = Settings()
