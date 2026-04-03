# AI 开发约束与开发模式

本文档用于总结本仓库中 AI 开发功能时必须遵守的约束，以及推荐采用的统一开发模式。

目标不是让 AI “尽快写完代码”，而是让 AI 在本仓库内持续以可控、可审查、可验证的方式交付功能。

---

## 1. 文档依据

本说明基于以下现有文档整理：

- `AGENTS.md`
- `docs/DOCS_ORGANIZATION.md`
- `docs/templates/spec_template.md`
- `docs/templates/task_template.md`
- `docs/templates/review_template.md`
- `docs/templates/acceptance_template.md`

若本说明与 `AGENTS.md` 冲突，以 `AGENTS.md` 为最高约束。

---

## 2. 核心约束

### 2.1 架构约束

本仓库采用：

- `DDD`
- `六边形架构`
- `分层依赖单向流动`

唯一允许的主依赖方向：

```text
interfaces -> application -> domain
infrastructure -> application
infrastructure -> domain
```

禁止：

```text
domain -> application / infrastructure / interfaces
application -> interfaces / infrastructure(具体实现)
```

### 2.2 分层职责约束

#### Domain

只承载：

- 实体
- 值对象
- 聚合根
- 领域服务
- 仓储接口
- 领域异常
- 纯业务规则

禁止引入：

- `fastapi`
- `sqlalchemy`
- `pydantic`
- `Session`
- ORM Model
- HTTP Request / Response

#### Application

只承载：

- 用例
- DTO
- 命令/查询处理逻辑
- 事务编排
- 对领域对象与仓储端口的协调

禁止直接依赖：

- ORM Model
- 路由函数
- FastAPI Request / Response
- 具体仓储实现
- SQL 细节

#### Infrastructure

只承载：

- ORM Model
- 仓储实现
- Session 管理
- 第三方服务适配
- 配置化技术细节

禁止：

- 定义核心业务规则
- 让 ORM Model 充当领域实体
- 把 ORM Model 在核心层传递

#### Interfaces

只承载：

- 路由
- 请求/响应 Schema
- 参数解析
- 错误映射
- 调用应用层用例

禁止：

- 直接写数据库 CRUD 流程
- 直接操作 `Session` 完成业务流程
- 直接实现核心业务规则
- 直接返回 ORM 对象

### 2.3 开发质量约束

AI 开发时必须满足：

- 新增注释、文档说明使用简体中文
- 变量名、函数名、类名、模块名使用英文
- 优先做最小必要改动，但不能为了省事破坏分层
- 发现旧代码明显越层时，应做本次范围内的最小必要纠偏
- 不允许把“暂时能跑”当成“设计正确”

### 2.4 数据与接口约束

数据库与 ORM 相关开发必须遵守：

- 表结构变化必须通过 Alembic
- 领域实体不等于 ORM Model
- 仓储实现负责 ORM 与领域对象的转换
- 不允许把 `Session` 传入领域层
- 不允许在路由层写事务性持久化流程

接口开发必须遵守：

- 请求体与响应体使用 Pydantic Schema
- API 层不直接暴露 ORM 对象
- API 层不直接暴露领域实体
- 领域异常在接口层映射为 HTTP 异常

---

## 3. AI 开发模式

AI 在本仓库中开发功能时，应采用以下统一模式。

### 3.1 先写 Spec

任何功能开发前，先补规格。

使用模板：

- `docs/templates/spec_template.md`

文档落位：

- 必须先创建需求目录：`docs/requirements/{序号}-{日期}-{需求名}/`
- 再在该目录内新增：`spec.md`

规格至少应明确：

- 目标
- 当前现状
- 范围
- 核心业务规则
- 分层落位
- 数据与持久化影响
- 风险点
- 验收标准

没有规格，或规格不完整，不进入实现。

### 3.2 再拆 Task

规格明确后，再拆分开发条目。

使用模板：

- `docs/templates/task_template.md`

文档落位：

- `docs/requirements/{序号}-{日期}-{需求名}/tasks.md`

条目要求：

- 一次只描述一个清晰目标
- 必须明确所属层
- 必须明确输入、输出、边界、依赖、测试要求
- 条目必须可以独立执行与独立验收

### 3.3 先做 Review

在实现前，对规格或任务拆解做审查。

使用模板：

- `docs/templates/review_template.md`

文档落位：

- `docs/requirements/{序号}-{日期}-{需求名}/review.md`

审查重点：

- 内容是否完整
- 分层是否正确
- 是否存在依赖方向风险
- 是否存在职责错放
- 是否定义了测试范围与验证方式

审查不过，不进入编码。

### 3.4 再做实现

实现顺序必须遵守：

```text
先核心层
  -> domain
  -> application
再适配器层
  -> infrastructure
  -> interfaces
如有表结构变更
  -> alembic
最后
  -> tests
```

AI 不应从 `routes.py` 直接起手，也不应先写 ORM 再倒推业务。

### 3.5 最后做 Acceptance

功能完成后进行验收。

使用模板：

- `docs/templates/acceptance_template.md`

文档落位：

- `docs/requirements/{序号}-{日期}-{需求名}/acceptance.md`

验收必须覆盖：

- 已完成内容
- 关键文件变更
- 架构是否符合要求
- 各门禁是否通过
- 测试结果
- 风险与遗留问题

---

## 4. 门禁机制

本仓库推荐 AI 以以下五类门禁组织开发动作。

### 4.1 Spec Gate

检查规格是否完整、是否足以支撑实现。

未通过时：

- 不允许进入任务拆解
- 不允许进入编码

### 4.2 Policy Gate

检查开发方案是否违反仓库既定约束。

重点检查：

- 是否违反 `AGENTS.md`
- 是否破坏分层
- 是否反转依赖
- 是否试图跳过测试

未通过时：

- 直接拒绝进入实现

### 4.3 Dependency Gate

检查前置条件是否满足。

例如：

- 规格是否通过
- 上游条目是否完成
- 数据结构是否已定义
- 接口依赖是否已准备好

未通过时：

- 当前条目进入阻塞态

### 4.4 Approval Gate

当存在高风险决策或待确认项时，需要人工确认。

例如：

- 是否改动数据库结构
- 是否调整公共接口行为
- 是否改变领域规则语义

未通过时：

- 不应擅自推进高风险实现

### 4.5 Test Gate

测试门禁是交付前的强制门禁。

推荐状态：

- `not_run`
- `passed`
- `failed`
- `blocked`

规则：

- 需要测试的改动，没有测试结果就不能算完成
- `failed` 不是完成
- `blocked` 不是完成，只是明确阻塞

---

## 5. AI 的标准执行顺序

AI 处理功能开发时，应默认按以下顺序自检和推进：

1. 这次需求属于哪个业务上下文
2. 涉及哪些领域对象、用例、仓储端口
3. 业务规则应落在 `domain` 还是 `application`
4. 是否涉及数据库结构变化
5. 是否已经补齐 `spec`
6. 是否已经拆出可执行 `task`
7. `review` 是否通过
8. 是否满足所有前置依赖
9. 是否已经补测试
10. 是否已经执行 `pytest`
11. 是否有证据证明没有破坏旧功能

任一关键项不成立，都不应草率交付。

---

## 6. 测试与完成定义

AI 在以下场景后必须执行 `pytest`：

- 新增功能
- 修复缺陷
- 重构代码
- 调整数据库映射
- 调整接口行为

一个任务只有同时满足以下条件才算完成：

- 代码实现完成
- 分层正确
- 必要测试已补充
- `pytest` 已执行
- `pytest` 通过，或用户明确接受当前失败状态

如果测试失败：

- 先判断是否由本次改动引起
- 是本次改动导致的，必须修复
- 若是历史问题，也必须在交付说明中明确指出

---

## 7. AI 禁止行为

AI 在本仓库中禁止以下行为：

1. 在 `routes.py` 中直接写数据库 CRUD 流程
2. 在 `domain` 中导入 `fastapi`、`sqlalchemy`、`pydantic`
3. 让应用层依赖具体仓储实现
4. 把 ORM Model 当成领域实体使用
5. 在 Schema 中承载业务规则
6. 在 ORM Model 中堆业务逻辑
7. 为了赶进度跳过分层
8. 不补测试就宣称完成
9. 未执行 `pytest` 就宣称没有破坏旧功能
10. 明知架构错误仍继续在错误层叠代码

---

## 8. 推荐的交付格式

AI 完成一次开发后，交付说明至少应覆盖：

1. 改了什么
2. 为什么这样分层
3. 是否补了测试
4. 是否执行了 `pytest`
5. `pytest` 的结果如何
6. 是否有遗留风险

若未执行 `pytest`，必须明确说明原因，不允许省略。

---

## 9. 一句话开发口径

本仓库内 AI 开发功能的默认口径应为：

```text
先补 Spec，再拆 Task，Review 通过后按 domain -> application -> infrastructure/interfaces -> alembic -> tests 顺序实现，最后以 Acceptance 和 pytest 结果作为完成依据。
```
