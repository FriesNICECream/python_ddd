# 登录与注册重构 Acceptance

---

## 1. 验收基本信息

- 验收对象：登录与注册重构
- 验收编号：AUTH-ACCEPT-001
- 验收人：AI
- 验收日期：2026-04-03
- 关联需求：AUTH-REFactor-001

---

## 2. 验收范围

- 覆盖条目：
  - `AUTH-ITEM-001`
  - `AUTH-ITEM-002`
- 覆盖模块：
  - `app/domain/auth`
  - `app/application/auth`
  - `app/infrastructure/security`
  - `app/infrastructure/repositories`
  - `app/interfaces/api`
  - `alembic/versions`
- 不在本次验收范围内的内容：
  - 权限系统
  - 刷新令牌
  - 找回密码

---

## 3. 已完成内容

1. 新增独立 `auth` 上下文，承载注册与登录核心能力。
2. 注册改为接收 `email`、`full_name`、`password`，并以哈希形式存储密码。
3. 新增登录接口，登录成功返回访问令牌。
4. 用户表新增 `password_hash` 字段，并补充 Alembic 迁移。
5. 已补应用层测试并通过 `pytest`。

---

## 4. 文件变更清单

- 文件：`app/domain/auth/*`
  - 说明：新增认证领域对象、仓储端口、服务端口、领域异常
- 文件：`app/application/auth/*`
  - 说明：新增注册与登录用例、DTO
- 文件：`app/infrastructure/repositories/auth_repository_sqlalchemy.py`
  - 说明：新增认证仓储实现
- 文件：`app/infrastructure/security/*`
  - 说明：新增密码哈希与 JWT 令牌签发实现
- 文件：`app/interfaces/api/auth_routes.py`
  - 说明：新增注册与登录接口
- 文件：`app/infrastructure/db/models.py`
  - 说明：补充密码哈希持久化字段
- 文件：`alembic/versions/20260403_0002_add_password_hash_to_users.py`
  - 说明：新增迁移
- 文件：`tests/application/auth/test_use_cases.py`
  - 说明：新增认证应用层测试

---

## 5. 架构验收

- 业务规则是否位于正确层：是
- 应用层是否只做编排：是
- 是否存在 ORM/HTTP 细节泄漏到核心层：否
- 是否存在接口层承担业务决策：否

---

## 6. 门禁结果

### 6.1 Spec Gate

- 状态：`通过`
- 说明：规格已明确登录返回访问令牌，且认证上下文独立拆分为 `auth`

### 6.2 Policy Gate

- 状态：`通过`
- 说明：实现遵循 `AGENTS.md` 分层、迁移和测试要求

### 6.3 Dependency Gate

- 状态：`通过`
- 说明：任务拆解与审查已完成，核心模型先于适配器实现

### 6.4 Approval Gate

- 状态：`通过`
- 说明：关键待确认项已由用户确认

### 6.5 Test Gate

- 状态：`passed`
- 说明：应用层测试通过

---

## 7. 测试结果

- 新增测试：
  - `tests/application/auth/test_use_cases.py`
- 执行命令：
  - `python -m pytest`
- 执行结果：
  - `4 passed`
- 失败项：
  - 无
- 若未执行或阻塞，原因：
  - 不适用

---

## 8. 风险与遗留问题

1. 当前只覆盖应用层测试，尚未补接口层集成测试。
2. 访问令牌目前只提供最小签发能力，尚未接入刷新令牌与鉴权中间件。
3. 旧数据若存在未设置 `password_hash` 的用户，将无法通过登录流程认证。

---

## 9. 验收结论

- 验收结果：`通过`
- 是否允许合并或交付：`是`
- 后续动作：
  - 可继续补接口层测试与受保护接口鉴权
- 备注：
  - 依赖中补充了 `PyJWT` 与 `email-validator`
