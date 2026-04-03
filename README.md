# python_ddd

基于 **FastAPI + SQLAlchemy 2.0 + PostgreSQL + Alembic** 的企业级后端初始化模板，采用 **DDD + 六边形架构**。

## 目录结构

```text
app/
  domain/          # 领域层：实体、仓储接口
  application/     # 应用层：用例、DTO
  infrastructure/  # 基础设施层：ORM 模型、仓储实现、DB 会话
  interfaces/      # 接口层：HTTP API
alembic/           # 数据库迁移
```

## 快速开始

### 1. 安装 Poetry

确认本机已安装 Poetry：

```bash
poetry --version
```

### 2. 安装依赖

在项目根目录执行：

```bash
poetry install
```

如果你希望为当前项目创建项目内专用虚拟环境，先执行：

```bash
poetry config virtualenvs.in-project true
```

然后再执行：

```bash
poetry install
```

本项目默认将 Poetry 作为依赖与虚拟环境管理工具使用，不要求将当前仓库打包安装为独立 Python 包。

### 3. 配置环境变量

复制环境变量示例文件：

```bash
cp .env.example .env
```

如果你使用的是 PowerShell，也可以执行：

```powershell
Copy-Item .env.example .env
```

### 4. 按需修改 `.env`

至少确认以下配置：

```env
APP_ENV=dev
DEV_DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/python_ddd
PROD_DATABASE_URL=postgresql+psycopg://python_ddd_pass_001:python_ddd_pass_001@localhost:5432/python_ddd
APP_NAME=Python DDD
ACCESS_TOKEN_SECRET=change-me-in-production
ACCESS_TOKEN_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
CORS_ALLOW_ORIGINS=["*"]
CORS_ALLOW_METHODS=["*"]
CORS_ALLOW_HEADERS=["*"]
CORS_ALLOW_CREDENTIALS=false
```

说明：

- `APP_ENV=dev` 时使用 `DEV_DATABASE_URL`
- `APP_ENV=prod` 时使用 `PROD_DATABASE_URL`
- 如果显式设置 `DATABASE_URL`，则优先使用该值，便于兼容旧部署方式或临时覆盖

### 5. 执行迁移

使用 Poetry 运行 Alembic：

```bash
poetry run alembic upgrade head
```

### 6. 启动服务

使用 Poetry 启动 FastAPI：

```bash
poetry run uvicorn app.main:app --reload
```

默认启动后可访问：

- 服务地址：`http://127.0.0.1:8000`
- 健康检查：`http://127.0.0.1:8000/health`
- Swagger 文档：`http://127.0.0.1:8000/docs`

### 7. 运行测试

如需验证当前项目状态，可执行：

```bash
poetry run pytest
```

## 服务器自动部署脚本

仓库提供了 Linux 服务器部署脚本 `[scripts/deploy.sh](./scripts/deploy.sh)`，默认完成以下步骤：

1. 使用 Poetry 安装生产依赖
2. 执行 `alembic upgrade head`
3. 以 `APP_ENV=prod` 启动 `uvicorn`
4. 轮询 `http://127.0.0.1:8000/health` 做健康检查

使用方式：

```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

可选环境变量：

- `APP_HOST`：默认 `0.0.0.0`
- `APP_PORT`：默认 `8000`
- `PID_FILE`：默认 `run/uvicorn.pid`
- `LOG_FILE`：默认 `logs/uvicorn.log`
- `HEALTH_CHECK_RETRIES`：默认 `20`
- `HEALTH_CHECK_INTERVAL`：默认 `3`

如果健康检查失败，脚本会输出最近日志并停止刚启动的进程。

## Auth 模块

- `POST /api/auth/register`：用户注册
- `POST /api/auth/login`：用户登录并获取访问令牌
- `GET /api/users/{user_id}`：按 ID 查询用户

示例请求：

```json
{
  "email": "alice@example.com",
  "full_name": "Alice",
  "password": "strong-pass"
}
```

## 开发执行机制

仓库内新增了开发执行机制设计说明，定义以下四项约束如何落地：

- `Spec-driven`
- `Policy-driven`
- `Gated execution`
- `Test gate`

详细说明见 [docs/AI_DEVELOPMENT_MODE.md](./docs/AI_DEVELOPMENT_MODE.md)。

需求开发文档目录规范见 [docs/DOCS_ORGANIZATION.md](./docs/DOCS_ORGANIZATION.md)。
