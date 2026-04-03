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
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/python_ddd
APP_NAME=Python DDD
ACCESS_TOKEN_SECRET=change-me-in-production
ACCESS_TOKEN_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
CORS_ALLOW_ORIGINS=["*"]
CORS_ALLOW_METHODS=["*"]
CORS_ALLOW_HEADERS=["*"]
CORS_ALLOW_CREDENTIALS=false
```

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
