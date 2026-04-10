# 数据模型：Telegram 影视资源采集

## 1. TelegramSource

### 业务含义

表示一个被系统登记并可被周期性采集的 Telegram 群聊来源。

### 关键字段

| 字段 | 类型倾向 | 说明 |
|------|----------|------|
| id | UUID | 系统内部主键 |
| source_key | 字符串 | Telegram 侧可识别的来源标识 |
| display_name | 字符串 | 来源展示名称 |
| enabled | 布尔 | 是否参与采集 |
| schedule_minutes | 整数 | 采集周期分钟数 |
| last_message_cursor | 字符串/整数 | 最近一次成功处理到的位置 |
| last_synced_at | 时间 | 最近一次成功采集时间 |
| created_at | 时间 | 创建时间 |

### 规则

- `source_key` 在系统内必须唯一。
- 禁用来源不会被定时采集。
- 游标只能向前推进，失败采集不能覆盖成功游标。

## 2. TelegramRawMessage

### 业务含义

表示某次从来源读取到的原始消息，用于幂等、追溯和后续解析。

### 关键字段

| 字段 | 类型倾向 | 说明 |
|------|----------|------|
| id | UUID | 系统内部主键 |
| source_id | UUID | 所属采集来源 |
| message_key | 字符串 | 来源内唯一的消息标识 |
| published_at | 时间 | 消息发布时间 |
| text_excerpt | 文本 | 原始文本摘要 |
| cover_url | 字符串，可空 | 抽取到的封面地址或媒体引用 |
| raw_payload | JSON | 原始消息结构摘要 |
| parse_status | 枚举 | 已解析、待整理、已忽略、解析失败 |
| created_at | 时间 | 首次入库时间 |

### 规则

- `source_id + message_key` 必须唯一。
- 原始消息保留后，资源匹配失败也不能丢失追溯能力。
- 同一条消息重复采集时必须命中幂等，不得重复生成业务记录。

## 3. MediaResource

### 业务含义

表示去重后的影视资源主记录，是后续整理与查询的核心聚合根。

### 关键字段

| 字段 | 类型倾向 | 说明 |
|------|----------|------|
| id | UUID | 系统内部主键 |
| canonical_title | 字符串 | 归一化标题 |
| display_title | 字符串 | 展示标题 |
| media_type | 枚举 | 电影、剧集、未确定 |
| cover_url | 字符串，可空 | 主封面 |
| scrape_profile | JSON | 基础刮削信息容器 |
| normalization_fingerprint | 字符串 | 匹配用指纹 |
| curation_status | 枚举 | 待整理、已初步整理、已忽略 |
| first_seen_at | 时间 | 首次发现时间 |
| last_seen_at | 时间 | 最近关联来源时间 |
| created_at | 时间 | 创建时间 |

### 规则

- 资源主记录的唯一性由领域匹配规则决定，不应仅由展示标题决定。
- 同一资源可关联多个来源消息。
- 缺字段资源允许入库，但必须标记 `待整理`。

## 4. CloudLink

### 业务含义

表示挂载在影视资源上的一个网盘访问链接。

### 关键字段

| 字段 | 类型倾向 | 说明 |
|------|----------|------|
| id | UUID | 系统内部主键 |
| media_resource_id | UUID | 所属影视资源 |
| source_message_id | UUID | 首次发现该链接的原始消息 |
| platform | 枚举 | 百度、阿里、其他 |
| url | 文本 | 网盘地址 |
| extraction_code | 字符串，可空 | 提取码 |
| first_seen_at | 时间 | 首次发现时间 |
| last_seen_at | 时间 | 最近再次出现时间 |

### 规则

- 同一资源下，相同平台和标准化链接组合不得重复。
- 相同链接可因不同来源再次出现，但应更新 `last_seen_at` 而不是重复插入。
- 链接必须可追溯到至少一个来源消息。

## 5. 关联关系

- 一个 `TelegramSource` 对应多个 `TelegramRawMessage`。
- 一个 `TelegramRawMessage` 可关联零个或一个主资源，也可作为待整理消息单独保留。
- 一个 `MediaResource` 对应多个 `CloudLink`。
- 一个 `MediaResource` 可由多个 `TelegramRawMessage` 共同支撑。

## 6. 状态转换

### 原始消息

`已采集 -> 已解析 -> 已关联资源`
`已采集 -> 待整理`
`已采集 -> 已忽略`

### 影视资源

`待整理 -> 已初步整理`
`待整理 -> 已忽略`

### 采集来源

`启用 -> 采集中 -> 启用`
`启用 -> 禁用`
