from pathlib import Path


DEPLOY_SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "deploy.sh"


def test_deploy_script_exists() -> None:
    assert DEPLOY_SCRIPT_PATH.exists()


def test_deploy_script_runs_prod_deployment_flow() -> None:
    script_content = DEPLOY_SCRIPT_PATH.read_text(encoding="utf-8")

    assert 'export APP_ENV="$APP_ENV_VALUE"' in script_content
    assert 'poetry check --lock' in script_content
    assert 'poetry env info --path' in script_content
    assert 'poetry install --only main --no-interaction' in script_content
    assert "poetry run alembic upgrade head" in script_content
    assert 'nohup poetry run uvicorn app.main:app --host "$APP_HOST" --port "$APP_PORT"' in script_content


def test_deploy_script_contains_health_check() -> None:
    script_content = DEPLOY_SCRIPT_PATH.read_text(encoding="utf-8")

    assert 'HEALTH_ENDPOINT="${HEALTH_ENDPOINT:-/health}"' in script_content
    assert 'http://127.0.0.1:${APP_PORT}${HEALTH_ENDPOINT}' in script_content
    assert "部署失败，服务未通过健康检查" in script_content


def test_deploy_script_checks_project_prerequisites() -> None:
    script_content = DEPLOY_SCRIPT_PATH.read_text(encoding="utf-8")

    assert '缺少 pyproject.toml' in script_content
    assert '缺少 poetry.lock' in script_content
    assert '缺少 .env' in script_content
    assert '缺少命令: python 或 python3' in script_content
