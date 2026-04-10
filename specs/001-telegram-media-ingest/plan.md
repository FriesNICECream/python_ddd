# 实施计划：Telegram 影视资源采集

**分支**: `[001-telegram-media-ingest]` | **日期**: 2026-04-10 | **规格**: [spec.md](D:\code-gh\python_ddd\specs\001-telegram-media-ingest\spec.md)
**输入**: `/specs/001-telegram-media-ingest/spec.md` 中的功能规格

## 概述

为现有 FastAPI + SQLAlchemy DDD 后端新增一个“Telegram 影视资源采集”业务上下文。该能力将围绕采集来源、原始消息、影视资源主记录、网盘链接四类核心对象展开，在领域层定义去重与增量链接沉淀规则，在应用层编排采集与入库流程，在基础设施层对接 Telegram 会话读取、数据库持久化与定时触发，并通过 API 暴露来源管理与采集结果查询能力。

## 技术上下文

**语言与版本**: Python 3.11+  
**主要依赖**: FastAPI、SQLAlchemy 2.0、Pydantic 2、Alembic、PostgreSQL、pytest、Telegram MTProto 客户端库  
**存储**: PostgreSQL  
**测试**: pytest  
**目标平台**: Linux 服务器常驻进程或容器化后端服务  
**项目类型**: Web service（Web 服务）  
**性能目标**: 单次采集任务在常规增量场景下可处理最近一个周期内的新增消息，并在 5 分钟内完成入库与可追溯查询  
**约束条件**: 必须遵守 `interfaces -> application -> domain` 与 `infrastructure -> application/domain` 单向依赖；表结构变更必须提供 Alembic 迁移；首期只实现采集、去重、链接沉淀与基础信息落库，不实现深度整理  
**规模范围**: 首期支持个位数到数十个群聊来源、每个周期数十到数百条候选消息、单资源关联多个来源消息与多个网盘链接

## 宪章检查

*门禁要求：在 Phase 0 研究前必须通过，并在 Phase 1 设计后再次复核。*

- `分层边界优先`: 通过。新功能按独立业务上下文设计，核心规则放入 `app/domain/media_ingest/` 与 `app/application/media_ingest/`，Telegram SDK、SQLAlchemy、调度器都限制在基础设施层。
- `领域模型承载业务规则`: 通过。资源去重、链接归并、来源消息幂等约束属于领域规则，不放在路由、Schema 或 ORM 中。
- `规格先于实现`: 通过。当前已完成 spec，本计划只产出设计文档，不直接编码。
- `测试门禁不可跳过`: 通过。计划中已预留领域、应用、接口测试；实现阶段完成后必须执行 `pytest`。
- `迁移与适配器一致性`: 通过。该功能明确需要新增表结构，计划包含 ORM Model 与 Alembic 迁移。

**设计后复核**: 通过。Phase 1 设计产物保持了端口先行、适配器后置和迁移一致性，没有让 Telegram/数据库细节泄漏到核心层。

## 项目结构

### 文档产物（当前功能）

```text
specs/001-telegram-media-ingest/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── telegram-media-ingest.openapi.yaml
└── tasks.md
```

### 源代码结构（仓库根目录）

```text
app/
├── application/
│   └── media_ingest/
│       ├── __init__.py
│       ├── dto.py
│       └── use_cases.py
├── domain/
│   └── media_ingest/
│       ├── __init__.py
│       ├── entities.py
│       ├── exceptions.py
│       ├── repositories.py
│       └── services.py
├── infrastructure/
│   ├── db/
│   │   └── models.py
│   ├── repositories/
│   │   ├── media_resource_repository_sqlalchemy.py
│   │   ├── telegram_message_repository_sqlalchemy.py
│   │   └── telegram_source_repository_sqlalchemy.py
│   ├── scheduler/
│   │   └── media_ingest_scheduler.py
│   └── telegram/
│       └── telegram_client_adapter.py
└── interfaces/
    └── api/
        ├── media_ingest_routes.py
        └── schemas.py
alembic/
└── versions/
tests/
├── application/
│   └── media_ingest/
├── domain/
│   └── media_ingest/
└── interfaces/
    └── api/
```

**结构决策**: 采用现有单体后端目录结构，在 `media_ingest` 新增独立业务上下文。由于当前仓库的部分旧路由仍直接装配仓储实现，新功能应避免复制这一模式，并在本上下文内优先通过依赖注入工厂或装配函数保持接口层轻量。

## Phase 0：研究结论

- Telegram 群聊读取接入需要按“用户会话读取”能力设计，而不是假定所有来源都可由机器人接口直接覆盖。
- 去重策略应采用“资源主记录去重 + 原始消息幂等 + 链接唯一约束”三层保护，避免误把单层唯一键当成完整业务规则。
- 基础刮削字段首期应建模为可扩展结构，先满足沉淀与待整理，不在 v1 固化过多整理规则。
- 调度触发应作为应用服务入口的外层适配器，手动触发与定时触发复用同一用例，避免把调度逻辑嵌入领域模型。

## Phase 1：设计方案

### 领域设计

- 新建 `TelegramSource` 实体，负责表达来源启停、最近游标与采集范围。
- 新建 `TelegramRawMessage` 实体，负责表达来源消息幂等键、原文摘要、发布时间和附件元数据。
- 新建 `MediaResource` 聚合根，统一管理资源名称归一化、类型、封面、整理状态和基础刮削信息。
- 新建 `CloudLink` 实体或聚合内子实体，负责平台识别、链接唯一性、提取码与来源关系。
- 在领域服务中定义资源匹配规则、链接去重规则和待整理判定规则。

### 应用层设计

- 提供“登记采集来源”“执行单来源采集”“执行全量增量采集”“查询资源列表/详情”四类用例。
- 通过 DTO 隔离接口层请求响应与领域对象。
- 用例层负责事务边界，统一编排来源读取端口、消息持久化端口、资源仓储端口和调度触发端口。
- 手动触发与定时触发复用同一个采集用例，避免双份业务流程。

### 基础设施层设计

- 在 `db.models` 新增采集来源表、原始消息表、影视资源表、资源链接表以及必要关联与唯一约束。
- 在 `repositories` 中实现来源仓储、消息仓储、资源仓储，并承担 ORM 与领域实体转换。
- 在 `telegram` 目录中实现 Telegram 客户端适配器，向应用层暴露“按来源拉取增量消息”的端口。
- 在 `scheduler` 中实现定时适配器，负责按周期触发应用层采集用例。
- 通过 Alembic 创建全部新增表与索引，确保去重和追溯能力可落地。

### 接口层设计

- 新增来源管理 API，用于登记、启停和查看 Telegram 来源。
- 新增采集触发 API，用于手动触发指定来源或全部来源的增量采集。
- 新增资源查询 API，用于查看资源主记录、网盘链接和来源摘要。
- 保持路由层只做参数解析、用例调用和响应映射，不直接操作 Session 完成业务流程。

### 测试策略

- 领域测试覆盖资源名称归一化后匹配、重复链接识别、缺失字段进入待整理状态。
- 应用层测试覆盖增量采集流程、重复消息幂等、同资源追加新链接。
- 接口层测试覆盖来源创建、手动采集触发和资源查询返回结构。
- 仓储测试可按需要补充，用于验证唯一约束映射与查询行为。

## 复杂度跟踪

| 违反项 | 必要原因 | 未采用更简单方案的原因 |
|--------|----------|--------------------------|
| 暂无 | 暂无 | 暂无 |
