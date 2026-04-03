# 前端登录对接接口说明

本文档面向前端联调用于说明当前仓库中已经可用的认证相关接口，内容以现有后端实现为准。

## 1. 基础信息

- 接口基础前缀：`/api`
- 本地开发默认服务地址：`http://127.0.0.1:8000`
- Swagger 文档地址：`http://127.0.0.1:8000/docs`
- 认证方式：`Bearer Token`
- Token 类型：JWT

## 2. 登录流程建议

前端建议按以下顺序完成登录链路：

1. 用户在登录页输入邮箱和密码。
2. 调用 `POST /api/auth/login` 获取 `access_token`。
3. 前端将 `access_token` 保存到内存或本地存储。
4. 后续请求在请求头中携带 `Authorization: Bearer <access_token>`。
5. 如需展示当前用户信息，可从 JWT 中取出 `sub` 作为 `user_id`，再调用 `GET /api/users/{user_id}`。

说明：

- 当前后端已提供登录、注册、按用户 ID 查询用户三个接口。
- 当前后端**尚未提供**“根据当前登录态直接返回我的信息”的 `/api/auth/me` 接口。
- 因此前端如果要在登录后拉取用户资料，需要使用登录返回的 JWT 中 `sub` 字段对应的用户 ID 再查询用户接口。

## 3. 接口明细

### 3.1 用户注册

- 方法：`POST`
- 路径：`/api/auth/register`
- 说明：创建新用户账号。

请求头：

```http
Content-Type: application/json
```

请求体：

```json
{
  "email": "alice@example.com",
  "full_name": "Alice",
  "password": "strong-pass"
}
```

字段说明：

- `email`：邮箱，必填，必须是合法邮箱格式。
- `full_name`：用户名，必填。
- `password`：密码，必填。应用层当前要求长度为 `8` 到 `128`。

成功响应：

- 状态码：`201 Created`

```json
{
  "id": "2ce7b30b-2b6f-47fb-99be-4389369c3d83",
  "email": "alice@example.com",
  "full_name": "Alice",
  "created_at": "2026-04-03T07:12:34.123456+00:00"
}
```

失败响应：

- `409 Conflict`：邮箱已存在

```json
{
  "detail": "User with email alice@example.com already exists"
}
```

- `422 Unprocessable Entity`：请求参数格式不合法，例如邮箱格式错误、缺少字段。

### 3.2 用户登录

- 方法：`POST`
- 路径：`/api/auth/login`
- 说明：校验邮箱和密码，成功后返回访问令牌。

请求头：

```http
Content-Type: application/json
```

请求体：

```json
{
  "email": "alice@example.com",
  "password": "strong-pass"
}
```

字段说明：

- `email`：邮箱，必填。
- `password`：密码，必填，当前要求长度为 `8` 到 `128`。

成功响应：

- 状态码：`200 OK`

```json
{
  "access_token": "<JWT_TOKEN>",
  "token_type": "bearer"
}
```

失败响应：

- `401 Unauthorized`：邮箱或密码错误

```json
{
  "detail": "Invalid email or password"
}
```

- `422 Unprocessable Entity`：请求体格式错误。

### 3.3 按用户 ID 查询用户

- 方法：`GET`
- 路径：`/api/users/{user_id}`
- 说明：根据用户 ID 查询用户信息。

路径参数：

- `user_id`：UUID 格式的用户 ID。

成功响应：

- 状态码：`200 OK`

```json
{
  "id": "2ce7b30b-2b6f-47fb-99be-4389369c3d83",
  "email": "alice@example.com",
  "full_name": "Alice",
  "created_at": "2026-04-03T07:12:34.123456+00:00"
}
```

失败响应：

- `404 Not Found`：用户不存在

```json
{
  "detail": "User not found"
}
```

- `422 Unprocessable Entity`：`user_id` 不是合法 UUID。

## 4. JWT 载荷说明

当前登录成功后签发的 JWT 载荷包含以下字段：

- `sub`：用户 ID，字符串格式
- `email`：用户邮箱
- `iat`：签发时间，Unix 时间戳
- `exp`：过期时间，Unix 时间戳

前端最常用的是：

- 用 `access_token` 作为后续请求凭证
- 用 `sub` 作为 `user_id` 去请求 `GET /api/users/{user_id}`

## 5. 前端对接示例

### 5.1 登录请求示例

```ts
const response = await fetch("http://127.0.0.1:8000/api/auth/login", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    email: "alice@example.com",
    password: "strong-pass",
  }),
});

const data = await response.json();

if (!response.ok) {
  throw new Error(data.detail || "登录失败");
}

localStorage.setItem("access_token", data.access_token);
```

### 5.2 携带 Token 请求示例

```ts
const token = localStorage.getItem("access_token");

const response = await fetch("http://127.0.0.1:8000/api/users/2ce7b30b-2b6f-47fb-99be-4389369c3d83", {
  headers: {
    Authorization: `Bearer ${token}`,
  },
});
```

说明：

- 当前后端还没有基于 `Authorization` 自动解析当前用户的接口。
- 因此即使前端带了 `Bearer Token`，`GET /api/users/{user_id}` 目前也只是普通查询接口。
- 如果后续需要严格的“登录后鉴权访问”，建议再补一版鉴权中间件或 `Depends` 认证依赖，以及 `/api/auth/me` 接口。

## 6. 联调注意事项

- 登录密码长度至少为 `8`。
- 登录返回的是 `token_type = bearer`，前端请求头应使用 `Authorization: Bearer <token>`。
- 本地联调前需要先执行数据库迁移，否则用户表和密码字段可能不存在。
- 如果前端和后端端口不同，联调前可能还需要补充 CORS 配置；当前仓库里暂未看到 CORS 中间件配置。

## 7. 当前可直接给前端的最小接口清单

前端登录页和登录后用户展示，当前最少使用以下两个接口即可：

1. `POST /api/auth/login`
2. `GET /api/users/{user_id}`

如果前端还需要注册页，再增加：

3. `POST /api/auth/register`
