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

1. 安装依赖

```bash
pip install -e .
```

2. 配置环境变量（可选）

```bash
cp .env.example .env
```

3. 执行迁移

```bash
alembic upgrade head
```

4. 启动服务

```bash
uvicorn app.main:app --reload
```

## User 模块

- `POST /api/users`：用户注册
- `GET /api/users/{user_id}`：按 ID 查询用户

示例请求：

```json
{
  "email": "alice@example.com",
  "full_name": "Alice"
}
```
