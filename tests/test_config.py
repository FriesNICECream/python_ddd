from app.config import Settings


def test_settings_use_dev_database_url_by_default() -> None:
    settings = Settings(_env_file=None)

    assert settings.app_env == "dev"
    assert settings.database_url == settings.dev_database_url


def test_settings_use_prod_database_url_when_app_env_is_prod() -> None:
    settings = Settings(_env_file=None, app_env="prod")

    assert settings.database_url == settings.prod_database_url
    assert settings.database_url == "postgresql+psycopg://python_ddd_pass_001:python_ddd_pass_001@localhost:5432/python_ddd"


def test_settings_keep_database_url_override() -> None:
    override_url = "postgresql+psycopg://custom:custom@localhost:5432/custom_db"

    settings = Settings(_env_file=None, app_env="prod", database_url=override_url)

    assert settings.database_url == override_url
