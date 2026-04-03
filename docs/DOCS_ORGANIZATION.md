# Docs 组织规则

本文档用于约束新需求对应文档的目录组织方式，避免随着需求增加导致 `Spec-driven + Policy-driven + Gated execution + Test gate` 相关文档混乱。

---

## 1. 总原则

每个新需求都必须拥有独立目录，禁止继续把不同需求的 `spec`、`task`、`review`、`acceptance` 混放到同一层目录中。

目录命名格式必须为：

```text
docs/requirements/{序号}-{日期}-{需求名}/
```

例如：

```text
docs/requirements/001-20260403-auth-refactor/
docs/requirements/002-20260405-order-create/
docs/requirements/003-20260406-user-profile-update/
```

---

## 2. 命名规则

### 2.1 序号

- 使用三位数字，从 `001` 开始递增
- 一个需求目录只对应一个需求编号
- 新需求不得复用旧编号

### 2.2 日期

- 使用 `YYYYMMDD`
- 默认使用需求正式进入开发的日期

### 2.3 需求名

- 使用英文 kebab-case
- 名称简洁，表达需求主题
- 避免使用过长描述

---

## 3. 目录结构

每个需求目录下默认包含以下文件：

```text
docs/requirements/001-20260403-auth-refactor/
  spec.md
  tasks.md
  review.md
  acceptance.md
```

含义如下：

- `spec.md`
  - 需求规格
- `tasks.md`
  - 开发条目拆解
- `review.md`
  - 规格或任务审查
- `acceptance.md`
  - 最终验收记录

---

## 4. 使用规则

### 4.1 新需求开始时

必须先创建新目录，再在目录中写：

- `spec.md`

如规格通过，再继续补：

- `tasks.md`
- `review.md`

实现完成后再补：

- `acceptance.md`

### 4.2 禁止行为

禁止：

1. 把多个需求写到同一个 `spec.md`
2. 把不同需求的 `tasks` 混在一个文件里
3. 将 `acceptance` 写回 `spec.md`
4. 使用无编号、无日期的需求目录
5. 将需求文档直接散落在 `docs/` 根目录

---

## 5. 与模板的关系

模板仍保留在：

```text
docs/templates/
```

模板只作为填写起点，不直接作为需求文档。

新需求应基于模板生成对应目录下的：

- `spec.md`
- `tasks.md`
- `review.md`
- `acceptance.md`

---

## 6. 当前约定

当前已落地需求目录：

```text
docs/requirements/001-20260403-auth-refactor/
```

后续需求必须继续按该规则递增，不再使用：

- `docs/specs/`
- `docs/tasks/`
- `docs/reviews/`
- `docs/acceptance/`

作为新需求文档主存放位置。
