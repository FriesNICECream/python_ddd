# 任务清单：Telegram 影视资源采集

**输入**: `/specs/001-telegram-media-ingest/` 下的设计文档  
**前置文档**: `plan.md`、`spec.md`、`research.md`、`data-model.md`、`contracts/`、`quickstart.md`

**测试要求**: 本仓库将测试视为强制门禁，因此本任务清单包含领域、应用、接口测试任务，并要求实现完成后执行 `pytest`。

**组织方式**: 任务按用户故事分组，确保每个故事都可以独立实现、独立验证。

## 格式：`[ID] [P?] [Story] Description`

- **[P]**: 可并行执行（不同文件、无未完成前置依赖）
- **[Story]**: 任务所属用户故事（`[US1]`、`[US2]`、`[US3]`）
- 每个任务描述都包含明确文件路径

## Phase 1：准备阶段（共享基础设施）

**目标**: 为 Telegram 采集业务上下文建立基础目录与配置接入点

- [x] T001 创建 `app/domain/media_ingest/__init__.py`、`app/application/media_ingest/__init__.py`、`app/infrastructure/telegram/__init__.py` 和 `app/infrastructure/scheduler/__init__.py`
- [x] T002 [P] 在 `app/config.py` 中补充 Telegram 相关配置占位
- [x] T003 [P] 在 `app/interfaces/api/media_ingest_routes.py` 中创建媒体采集路由骨架

---

## Phase 2：基础阶段（阻塞前置）

**目标**: 完成所有用户故事共享的核心模型、仓储端口、数据库模型与迁移骨架

**⚠️ 关键约束**: 此阶段未完成前，不应开始任何用户故事实现

- [x] T004 在 `app/domain/media_ingest/entities.py` 和 `app/domain/media_ingest/exceptions.py` 中创建共享枚举、实体与领域异常
- [x] T005 [P] 在 `app/domain/media_ingest/repositories.py` 中定义仓储端口与 Telegram 读取端口
- [x] T006 [P] 在 `app/domain/media_ingest/services.py` 中实现标题归一化、资源匹配和链接去重领域服务
- [x] T007 在 `app/application/media_ingest/dto.py` 中创建来源、采集执行、资源和链接相关 DTO
- [x] T008 在 `app/infrastructure/db/models.py` 中扩展来源、原始消息、资源和网盘链接 ORM 模型
- [x] T009 在 `app/infrastructure/repositories/telegram_source_repository_sqlalchemy.py`、`app/infrastructure/repositories/telegram_message_repository_sqlalchemy.py` 和 `app/infrastructure/repositories/media_resource_repository_sqlalchemy.py` 中创建共享 SQLAlchemy 仓储实现
- [x] T010 在 `alembic/versions/` 中创建媒体采集相关表与索引的 Alembic 迁移
- [x] T011 在 `app/interfaces/api/schemas.py` 中创建媒体采集共享请求与响应 Schema

**阶段检查点**: 基础层完成后，用户故事可按优先级逐步实现

---

## Phase 3：用户故事 1 - 定时采集群聊资源发布（优先级：P1）🎯 MVP

**目标**: 登记 Telegram 来源并完成增量消息采集入库，保留原始消息追溯能力

**独立验证方式**: 创建一个启用来源并触发一次采集后，系统可以保存来源、原始消息和最小资源记录，无需手工复制群消息字段

### 用户故事 1 的测试 ⚠️

- [x] T012 [P] [US1] 在 `tests/domain/media_ingest/test_entities.py` 中补充来源游标推进与不完整消息处理领域测试
- [x] T013 [P] [US1] 在 `tests/application/media_ingest/test_use_cases.py` 中补充来源登记与增量采集编排应用测试
- [x] T014 [P] [US1] 在 `tests/interfaces/api/test_media_ingest_routes.py` 中补充来源创建与手动触发采集接口测试

### 用户故事 1 的实现

- [x] T015 [US1] 在 `app/application/media_ingest/use_cases.py` 中实现来源管理与采集执行用例
- [x] T016 [P] [US1] 在 `app/infrastructure/telegram/telegram_client_adapter.py` 中实现增量消息抓取的 Telegram 客户端适配器
- [x] T017 [P] [US1] 在 `app/infrastructure/scheduler/media_ingest_scheduler.py` 中实现调用采集用例的调度器适配器
- [x] T018 [US1] 在 `app/interfaces/api/media_ingest_routes.py` 中实现来源管理与采集触发接口
- [x] T019 [US1] 在 `app/main.py` 中注册媒体采集路由
- [x] T020 [US1] 在 `app/interfaces/api/media_ingest_routes.py` 中补充媒体采集用例与仓储的依赖装配

**阶段检查点**: 此时 US1 应能独立完成来源登记、手动触发采集和原始消息入库

---

## Phase 4：用户故事 2 - 影片去重并增量追加网盘链接（优先级：P2）

**目标**: 将重复来源消息归并到同一影视资源，并把新的网盘链接追加到已有主记录

**独立验证方式**: 对同一影视资源重复导入多条消息后，系统只保留一个主资源，并把新出现的链接追加到该资源下

### 用户故事 2 的测试 ⚠️

- [ ] T021 [P] [US2] 在 `tests/domain/media_ingest/test_services.py` 中补充资源匹配与网盘链接去重领域测试
- [ ] T022 [P] [US2] 在 `tests/application/media_ingest/test_ingestion_deduplication.py` 中补充重复消息幂等与链接增量追加应用测试
- [ ] T023 [P] [US2] 在 `tests/interfaces/api/test_media_resource_queries.py` 中补充资源去重结果查询接口测试

### 用户故事 2 的实现

- [ ] T024 [US2] 在 `app/domain/media_ingest/entities.py` 和 `app/domain/media_ingest/services.py` 中扩展资源聚合与链接合并规则
- [ ] T025 [US2] 在 `app/application/media_ingest/use_cases.py` 中更新采集编排逻辑，复用已有资源并追加新链接
- [ ] T026 [US2] 在 `app/infrastructure/repositories/media_resource_repository_sqlalchemy.py` 和 `app/infrastructure/repositories/telegram_message_repository_sqlalchemy.py` 中增强资源查询、消息幂等与链接 upsert 行为
- [ ] T027 [US2] 在 `app/infrastructure/db/models.py` 和 `alembic/versions/` 中完善资源与链接唯一性约束
- [ ] T028 [US2] 在 `app/interfaces/api/media_ingest_routes.py` 中增加资源列表与详情查询接口

**阶段检查点**: 此时 US1 和 US2 应可共同支撑“采集即归并，重复不重复入库，新增链接可追加”

---

## Phase 5：用户故事 3 - 建立可整理的影视资源基础库（优先级：P3）

**目标**: 为资源主记录沉淀类型、封面、基础刮削字段和待整理状态，支撑后续整理流程

**独立验证方式**: 即使消息字段不完整，系统仍能生成可查询的资源记录，并清晰标记待整理状态和基础信息字段

### 用户故事 3 的测试 ⚠️

- [ ] T029 [P] [US3] 在 `tests/domain/media_ingest/test_curation_rules.py` 中补充整理状态流转与刮削字段默认值领域测试
- [ ] T030 [P] [US3] 在 `tests/application/media_ingest/test_resource_curation.py` 中补充部分字段资源持久化应用测试
- [ ] T031 [P] [US3] 在 `tests/interfaces/api/test_media_resource_detail.py` 中补充资源详情字段接口测试

### 用户故事 3 的实现

- [ ] T032 [US3] 在 `app/domain/media_ingest/entities.py` 中扩展刮削信息与整理状态处理能力
- [ ] T033 [US3] 在 `app/application/media_ingest/dto.py` 和 `app/application/media_ingest/use_cases.py` 中暴露面向整理流程的字段
- [ ] T034 [US3] 在 `app/infrastructure/db/models.py` 和 `app/infrastructure/repositories/media_resource_repository_sqlalchemy.py` 中扩展刮削信息持久化与待整理记录支持
- [ ] T035 [US3] 在 `app/interfaces/api/schemas.py` 和 `app/interfaces/api/media_ingest_routes.py` 中返回整理字段、来源消息摘要和链接元数据

**阶段检查点**: 所有用户故事完成后，系统应具备后续整理所需的基础影视资源库

---

## Phase 6：收尾与跨切面事项

**目标**: 完成跨故事收尾、文档和回归验证

- [ ] T036 [P] 在 `README.md` 中补充 Telegram 媒体采集的使用说明与环境变量说明
- [ ] T037 按实现结果验证快速开始流程，并在 `specs/001-telegram-media-ingest/quickstart.md` 中同步必要修订
- [ ] T038 执行完整回归测试命令 `pytest`

---

## 依赖关系与执行顺序

### 阶段依赖

- **Phase 1：准备阶段** 可立即开始
- **Phase 2：基础阶段** 依赖准备阶段完成，并阻塞所有用户故事
- **Phase 3：US1** 依赖基础阶段完成，是 MVP
- **Phase 4: US2** 依赖 US1 的采集主流程可用
- **Phase 5: US3** 依赖 US1/US2 已建立资源主记录与查询链路
- **Phase 6：收尾阶段** 依赖所有目标用户故事完成

### 用户故事依赖

- **US1 (P1)**: 无其他故事依赖，Foundational 完成后即可开始
- **US2 (P2)**: 依赖 US1 已具备来源采集与入库流程
- **US3 (P3)**: 依赖 US1 的采集链路与 US2 的资源聚合结果

### 每个用户故事内部顺序

- 测试任务先写，且应先失败再实现
- 领域规则先于应用编排
- 应用编排先于接口暴露
- ORM / 仓储调整必须与领域行为保持一致
- 每个故事完成后先独立验证，再继续下一阶段

### 并行机会

- Phase 1 中 `T002` 与 `T003` 可并行
- Phase 2 中 `T005`、`T006`、`T008`、`T011` 可在不冲突前提下并行
- US1 中 `T012`、`T013`、`T014` 可并行编写测试，`T016` 与 `T017` 可并行实现
- US2 中 `T021`、`T022`、`T023` 可并行，随后仓储增强与接口查询可以分拆推进
- US3 中 `T029`、`T030`、`T031` 可并行

---

## 并行示例：用户故事 1

```bash
# 并行编写 US1 测试
Task: "在 tests/domain/media_ingest/test_entities.py 中补充来源游标推进与不完整消息处理领域测试"
Task: "在 tests/application/media_ingest/test_use_cases.py 中补充来源登记与增量采集编排应用测试"
Task: "在 tests/interfaces/api/test_media_ingest_routes.py 中补充来源创建与手动触发采集接口测试"

# 并行实现外层适配器
Task: "在 app/infrastructure/telegram/telegram_client_adapter.py 中实现增量消息抓取的 Telegram 客户端适配器"
Task: "在 app/infrastructure/scheduler/media_ingest_scheduler.py 中实现调用采集用例的调度器适配器"
```

---

## 实施策略

### MVP 优先（仅用户故事 1）

1. 完成 Phase 1 和 Phase 2，建立好上下文骨架、仓储端口、ORM 与迁移。
2. 完成 US1 的测试与实现，先打通来源登记、手动触发采集、原始消息入库。
3. 独立验证 US1，确认最小采集闭环成立后再继续。

### 增量交付

1. Setup + Foundational 完成后，先交付 US1 作为 MVP。
2. 在 MVP 稳定后追加 US2，实现资源去重与网盘链接增量沉淀。
3. 最后补齐 US3，让资源主记录具备后续整理所需字段。
4. 每完成一个故事，都执行对应测试并确认不破坏已有能力。

### 并行协作策略

1. 先由全员协作完成 Foundational。
2. US1 阶段可以拆分为“应用编排 / Telegram 适配器 / API 测试”三条线并行推进。
3. US2 与 US3 适合在 US1 稳定后由不同成员分工推进，但要避免同时改同一文件的大段冲突。

---

## 备注

- 所有任务均遵守 `- [ ] Txxx ...` 的 checklist 格式。
- 用户故事任务均附带 `[US1]`、`[US2]`、`[US3]` 标签。
- 任务描述已包含明确文件路径，便于直接执行。
- 实现阶段完成后，必须执行 `pytest`，否则不满足本仓库完成定义。
