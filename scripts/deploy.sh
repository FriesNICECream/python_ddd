#!/usr/bin/env bash

set -Eeuo pipefail

# 用于 Linux 服务器的一键部署脚本。
# 默认使用 Poetry 安装依赖，并以 prod 环境启动当前 FastAPI 项目。

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_HOST="${APP_HOST:-0.0.0.0}"
APP_PORT="${APP_PORT:-8000}"
APP_ENV_VALUE="prod"
PID_FILE="${PID_FILE:-$APP_DIR/run/uvicorn.pid}"
LOG_FILE="${LOG_FILE:-$APP_DIR/logs/uvicorn.log}"
HEALTH_ENDPOINT="${HEALTH_ENDPOINT:-/health}"
HEALTH_CHECK_RETRIES="${HEALTH_CHECK_RETRIES:-20}"
HEALTH_CHECK_INTERVAL="${HEALTH_CHECK_INTERVAL:-3}"

mkdir -p "$(dirname "$PID_FILE")"
mkdir -p "$(dirname "$LOG_FILE")"

log() {
  printf '[deploy] %s\n' "$1"
}

fail() {
  printf '[deploy] 错误: %s\n' "$1" >&2
  exit 1
}

require_command() {
  command -v "$1" >/dev/null 2>&1 || fail "缺少命令: $1"
}

ensure_project_files() {
  [[ -f "$APP_DIR/pyproject.toml" ]] || fail "缺少 pyproject.toml，当前目录不是有效项目根目录"
  [[ -f "$APP_DIR/poetry.lock" ]] || fail "缺少 poetry.lock，请先在仓库内生成锁文件"
  [[ -f "$APP_DIR/.env" ]] || fail "缺少 .env，请先准备服务器环境变量配置"
}

ensure_poetry_environment() {
  require_command python
  require_command poetry

  log "检查 Poetry 项目配置"
  poetry check --lock

  log "检查 Poetry 虚拟环境"
  if poetry env info --path >/dev/null 2>&1; then
    local env_path
    env_path="$(poetry env info --path)"
    log "检测到已有虚拟环境: $env_path"
    return
  fi

  log "未检测到虚拟环境，先创建 Poetry 虚拟环境并安装生产依赖"
  poetry install --only main --no-interaction

  local env_path
  env_path="$(poetry env info --path 2>/dev/null || true)"
  [[ -n "$env_path" ]] || fail "Poetry 虚拟环境创建失败"
  log "虚拟环境已创建: $env_path"
}

stop_existing_process() {
  if [[ ! -f "$PID_FILE" ]]; then
    return
  fi

  local existing_pid
  existing_pid="$(cat "$PID_FILE")"

  if [[ -z "$existing_pid" ]]; then
    rm -f "$PID_FILE"
    return
  fi

  if kill -0 "$existing_pid" >/dev/null 2>&1; then
    log "停止旧进程 PID=$existing_pid"
    kill "$existing_pid"

    for _ in $(seq 1 10); do
      if ! kill -0 "$existing_pid" >/dev/null 2>&1; then
        rm -f "$PID_FILE"
        return
      fi
      sleep 1
    done

    log "旧进程未在预期时间内退出，执行强制停止"
    kill -9 "$existing_pid"
  fi

  rm -f "$PID_FILE"
}

run_health_check() {
  local health_url="http://127.0.0.1:${APP_PORT}${HEALTH_ENDPOINT}"

  for _ in $(seq 1 "$HEALTH_CHECK_RETRIES"); do
    if poetry run python -c "import json, sys, urllib.request; data = json.load(urllib.request.urlopen(sys.argv[1], timeout=5)); raise SystemExit(0 if data.get('status') == 'ok' else 1)" "$health_url"; then
      log "健康检查通过: $health_url"
      return 0
    fi
    sleep "$HEALTH_CHECK_INTERVAL"
  done

  return 1
}

main() {
  cd "$APP_DIR"

  ensure_project_files
  ensure_poetry_environment

  export APP_ENV="$APP_ENV_VALUE"

  log "安装依赖"
  poetry install --only main --no-interaction

  log "执行数据库迁移"
  poetry run alembic upgrade head

  stop_existing_process

  log "以 prod 环境启动服务"
  nohup poetry run uvicorn app.main:app --host "$APP_HOST" --port "$APP_PORT" >"$LOG_FILE" 2>&1 &
  local app_pid=$!
  echo "$app_pid" >"$PID_FILE"

  if ! kill -0 "$app_pid" >/dev/null 2>&1; then
    fail "服务进程启动失败"
  fi

  log "等待健康检查"
  if run_health_check; then
    log "部署完成，服务 PID=$app_pid"
    return 0
  fi

  log "健康检查失败，输出最近日志"
  tail -n 50 "$LOG_FILE" || true

  if kill -0 "$app_pid" >/dev/null 2>&1; then
    kill "$app_pid" || true
  fi
  rm -f "$PID_FILE"

  fail "部署失败，服务未通过健康检查"
}

main "$@"
