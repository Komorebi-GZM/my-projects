# 校园物品暂存平台 · API接口文档

> 版本：v2.1
> 创建日期：2026-05-10
> 最后更新：2026-05-13
> 状态：已就绪
> 关联文档：《订单状态机设计文档.md》v2.0

---

## 一、文档概述

### 1.1 接口规范

| 项目 | 说明 |
|------|------|
| 协议 | 本地开发：HTTP / 生产部署：HTTPS |
| 数据格式 | JSON |
| 字符编码 | UTF-8 |
| 接口调用方式 | 本地开发：Flask HTTP（localhost:5000）/ 生产：CloudBase 云函数 HTTP 触发 |
| 超时时间 | 云函数默认超时（20s），状态机接口建议设为 30s |

> **双模式说明**：本地开发阶段使用 Flask 提供 HTTP 服务（`localhost:5000`），生产环境使用 CloudBase 云函数 HTTP 触发。两种方式的 API 接口路径、请求参数、响应格式完全一致，业务代码无需修改，仅切换部署目标即可。

### 1.2 统一请求格式

CloudBase 云函数调用，请求体为 JSON。所有接口统一通过 HTTP POST 触发云函数，请求头设置 `Content-Type: application/json`。

**通用请求体结构**：

```json
{
  "orderId": "string",
  "newStatus": "string",
  "operatorType": "USER | ADMIN | SYSTEM",
  "reason": "string",
  "metadata": {}
}
```

> **说明**：不同接口的必填字段和可选字段见各接口详细说明。CloudBase 云函数通过 `event` 参数接收请求参数，通过 `event['userInfo']['openId']` 获取当前用户身份。本地开发模式下通过请求头 `X-OpenId` 模拟用户身份（见 1.5 节）。

### 1.3 统一响应格式

所有接口返回统一的 JSON 结构：

```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

**字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `code` | Integer | 业务状态码，`0` 表示成功，非零表示业务错误 |
| `message` | String | 状态描述，成功为 `"success"`，失败为人类可读的错误信息 |
| `data` | Object | 业务数据载体，失败时为空对象 `{}` |

### 1.4 错误码定义

| 错误码 | 说明 | HTTP状态码 | 触发场景 |
|--------|------|-----------|---------|
| 0 | 成功 | 200 | 请求处理成功 |
| 1001 | 参数校验失败 | 400 | 必填字段缺失、字段类型错误、枚举值不合法 |
| 1002 | 未登录 | 401 | 请求未携带有效登录态，`openId` 为空 |
| 1003 | 权限不足 | 403 | 用户角色无权执行该操作（如用户尝试管理员操作） |
| 2001 | 订单不存在 | 404 | `orderId` 对应的订单在数据库中不存在 |
| 2002 | 非法状态转换 | 400 | 当前状态不允许转换到目标状态（违反状态机规则） |
| 2003 | 乐观锁冲突 | 409 | 并发更新冲突，`_version` 不匹配（重试3次后仍失败） |
| 2004 | 订单已终态 | 400 | 对已处于 `COMPLETED` 或 `CANCELLED` 终态的订单执行变更 |
| 3001 | 支付失败 | 500 | 微信支付调用失败或退款失败 |
| 5001 | 系统内部错误 | 500 | 未预期的服务端异常（如数据库连接失败） |

### 1.5 鉴权说明

| 端 | 本地开发 | 生产环境 |
|----|---------|---------|
| 用户端 | 请求头 `X-OpenId` 模拟用户身份 | `wx.login()` 获取 `code` → 云函数调用 `wx.cloud.callFunction` 换取 `openId` |
| 运营端 | 请求头 `X-OpenId` 传入管理员 ID | 预置管理员 `openId` 白名单，云函数内校验 `operatorType == 'ADMIN'` |
| 系统端 | 本地脚本直接调用 | 云函数定时触发器，`operatorType == 'SYSTEM'` |

**鉴权实现**：

- **本地开发**：通过请求头 `X-OpenId` 传递用户标识，Flask 中间件自动提取并注入到请求上下文
- **生产环境**：云函数内通过 `event['userInfo']['openId']` 获取当前用户身份
- 管理员操作需额外校验 `openId` 是否在白名单中
- 白名单配置存储在云开发环境变量或独立配置集合中

**本地开发鉴权示例**：

```bash
# 模拟普通用户请求
curl -X POST http://localhost:5000/api/v1/orders/create \
  -H "Content-Type: application/json" \
  -H "X-OpenId: oXJ9f5kQnZ8yWa7m3Lp4Rt6vUw" \
  -d '{"city":"北京","itemType":"LUGGAGE","volume":60.0,"estimatedWeight":15.5,"serviceType":"STORAGE_DELIVERY","storageDays":30}'

# 模拟管理员请求
curl -X POST http://localhost:5000/api/v1/orders/status \
  -H "Content-Type: application/json" \
  -H "X-OpenId: admin_001" \
  -d '{"orderId":"ord_a1b2c3d4e5f6","newStatus":"COLLECTED","operatorType":"ADMIN","reason":"ADMIN_COLLECT"}'
```

---

## 二、本地开发 API 调用

### 2.0 本地开发基础信息

**基础 URL**：`http://localhost:5000/api/v1`

**启动方式**：

```bash
# 进入项目根目录，启动 Flask 开发服务器
python app.py
# 或使用 flask 命令
flask run --port=5000 --debug
```

**Flask 路由与云函数映射表**：

| Flask 路由 | 云函数名 | HTTP 方法 | 功能 |
|-----------|---------|-----------|------|
| `/api/v1/login` | `login` | POST | 用户登录 |
| `/api/v1/orders/create` | `createOrder` | POST | 创建订单 |
| `/api/v1/orders/list` | `getOrderList` | POST | 获取订单列表 |
| `/api/v1/orders/detail` | `getOrderDetail` | POST | 获取订单详情 |
| `/api/v1/orders/status` | `updateOrderStatus` | POST | 状态变更（核心） |
| `/api/v1/tickets/create` | `createTicket` | POST | 创建投诉工单 |

> **说明**：生产环境中，上述 Flask 路由对应 CloudBase 云函数的 HTTP 触发路径。两种模式下，请求体（JSON）和响应体（JSON）格式完全一致。

**本地调试 curl 示例**：

```bash
# 1. 创建订单
curl -X POST http://localhost:5000/api/v1/orders/create \
  -H "Content-Type: application/json" \
  -H "X-OpenId: oXJ9f5kQnZ8yWa7m3Lp4Rt6vUw" \
  -d '{
    "city": "北京",
    "itemType": "LUGGAGE",
    "volume": 60.0,
    "estimatedWeight": 15.5,
    "serviceType": "STORAGE_DELIVERY",
    "storageDays": 30
  }'

# 2. 查询订单列表
curl -X POST http://localhost:5000/api/v1/orders/list \
  -H "Content-Type: application/json" \
  -H "X-OpenId: oXJ9f5kQnZ8yWa7m3Lp4Rt6vUw" \
  -d '{"status": "STORED", "page": 1, "pageSize": 10}'

# 3. 查询订单详情
curl -X POST http://localhost:5000/api/v1/orders/detail \
  -H "Content-Type: application/json" \
  -H "X-OpenId: oXJ9f5kQnZ8yWa7m3Lp4Rt6vUw" \
  -d '{"orderId": "ord_a1b2c3d4e5f6"}'

# 4. 状态变更（管理员确认取件）
curl -X POST http://localhost:5000/api/v1/orders/status \
  -H "Content-Type: application/json" \
  -H "X-OpenId: admin_001" \
  -d '{
    "orderId": "ord_a1b2c3d4e5f6",
    "newStatus": "COLLECTED",
    "operatorType": "ADMIN",
    "reason": "ADMIN_COLLECT",
    "metadata": {"collectorName": "李师傅"}
  }'

# 5. 创建投诉工单
curl -X POST http://localhost:5000/api/v1/tickets/create \
  -H "Content-Type: application/json" \
  -H "X-OpenId: oXJ9f5kQnZ8yWa7m3Lp4Rt6vUw" \
  -d '{
    "orderId": "ord_a1b2c3d4e5f6",
    "type": "ITEM_DAMAGE",
    "description": "收到行李箱时发现侧面有明显凹陷，箱体变形无法正常使用"
  }'
```

---

## 三、用户端接口

### 3.1 用户登录

**云函数名**：`login` / **Flask 路由**：`/api/v1/login`

**功能说明**：微信小程序端调用，通过 `wx.login()` 获取的 `code` 换取用户身份信息。

**请求参数**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `code` | String | 是 | 微信 `wx.login()` 返回的临时登录凭证 |

**请求示例**：

```json
{
  "code": "0a1B2c3D4e5F6g"
}
```

**响应参数**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `data.token` | String | 自定义登录态 token（用于后续请求鉴权） |
| `data.userInfo` | Object | 用户基本信息 |
| `data.userInfo.openId` | String | 用户唯一标识 |
| `data.userInfo.nickName` | String | 用户昵称 |
| `data.userInfo.avatarUrl` | String | 用户头像 URL |
| `data.isNewUser` | Boolean | 是否为新注册用户 |

**成功响应示例**：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "userInfo": {
      "openId": "oXJ9f5kQnZ8yWa7m3Lp4Rt6vUw",
      "nickName": "张三",
      "avatarUrl": "https://thirdwx.qlogo.cn/..."
    },
    "isNewUser": false
  }
}
```

**错误响应示例**：

```json
{
  "code": 1001,
  "message": "参数校验失败：code 不能为空",
  "data": {}
}
```

---

### 3.2 创建订单

**云函数名**：`createOrder` / **Flask 路由**：`/api/v1/orders/create`

**功能说明**：用户提交物品暂存订单，系统生成订单号并计算费用。

**请求参数**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `city` | String | 是 | 所在城市（如 `"北京"`、`"上海"`） |
| `itemType` | String | 是 | 物品类型枚举：`LUGGAGE`(行李)、`PARCEL`(包裹)、`ELECTRONICS`(电子产品)、`OTHER`(其他) |
| `volume` | Number | 是 | 物品体积（单位：升），精确到小数点后1位 |
| `estimatedWeight` | Number | 是 | 预估重量（单位：kg），精确到小数点后1位 |
| `serviceType` | String | 是 | 服务类型枚举：`STORAGE`(暂存)、`STORAGE_DELIVERY`(暂存+配送) |
| `storageDays` | Integer | 是 | 暂存天数（1~365） |
| `warehouseId` | String | 否 | 指定仓库ID，不填则系统自动分配 |

**请求示例**：

```json
{
  "city": "北京",
  "itemType": "LUGGAGE",
  "volume": 60.0,
  "estimatedWeight": 15.5,
  "serviceType": "STORAGE_DELIVERY",
  "storageDays": 30,
  "warehouseId": ""
}
```

**响应参数**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `data.orderId` | String | 订单唯一ID（数据库主键） |
| `data.orderNo` | String | 订单编号（用户可见，如 `"ORD2026051000001"`） |
| `data.amount` | Number | 订单金额（单位：元），精确到小数点后2位 |
| `data.status` | String | 初始状态，固定为 `"PENDING"` |

**成功响应示例**：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "orderId": "ord_a1b2c3d4e5f6",
    "orderNo": "ORD2026051000001",
    "amount": 89.00,
    "status": "PENDING"
  }
}
```

**错误响应示例**：

```json
{
  "code": 1001,
  "message": "参数校验失败：storageDays 必须在 1~365 之间",
  "data": {}
}
```

---

### 3.3 获取订单列表

**云函数名**：`getOrderList` / **Flask 路由**：`/api/v1/orders/list`

**功能说明**：分页查询当前用户的订单列表，支持按状态筛选。

**请求参数**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `status` | String | 否 | 按订单状态筛选，不填则返回全部。枚举值：`PENDING`、`COLLECTED`、`TRANSIT`、`STORED`、`DELIVERING`、`COMPLETED`、`CANCELLED`、`EXCEPTION` |
| `page` | Integer | 是 | 页码，从 `1` 开始 |
| `pageSize` | Integer | 是 | 每页条数，建议 `10~20`，最大 `50` |

**请求示例**：

```json
{
  "status": "STORED",
  "page": 1,
  "pageSize": 10
}
```

**响应参数**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `data.total` | Integer | 符合条件的订单总数 |
| `data.page` | Integer | 当前页码 |
| `data.pageSize` | Integer | 每页条数 |
| `data.list` | Array\<Order\> | 订单列表 |

**Order 对象结构**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `orderId` | String | 订单唯一ID |
| `orderNo` | String | 订单编号 |
| `status` | String | 订单状态 |
| `itemType` | String | 物品类型 |
| `serviceType` | String | 服务类型 |
| `amount` | Number | 订单金额 |
| `createdAt` | String | 创建时间（ISO 8601） |
| `updatedAt` | String | 最后更新时间（ISO 8601） |

**成功响应示例**：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "total": 3,
    "page": 1,
    "pageSize": 10,
    "list": [
      {
        "orderId": "ord_a1b2c3d4e5f6",
        "orderNo": "ORD2026051000001",
        "status": "STORED",
        "itemType": "LUGGAGE",
        "serviceType": "STORAGE_DELIVERY",
        "amount": 89.00,
        "createdAt": "2026-05-10T10:30:00+08:00",
        "updatedAt": "2026-05-12T14:00:00+08:00"
      }
    ]
  }
}
```

---

### 3.4 获取订单详情

**云函数名**：`getOrderDetail` / **Flask 路由**：`/api/v1/orders/detail`

**功能说明**：查询单个订单的完整信息，包含状态变更历史。

**请求参数**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `orderId` | String | 是 | 订单唯一ID |

**请求示例**：

```json
{
  "orderId": "ord_a1b2c3d4e5f6"
}
```

**响应参数**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `data.order` | Object | 订单完整信息 |
| `data.order.orderId` | String | 订单唯一ID |
| `data.order.orderNo` | String | 订单编号 |
| `data.order.status` | String | 当前状态 |
| `data.order.city` | String | 所在城市 |
| `data.order.itemType` | String | 物品类型 |
| `data.order.volume` | Number | 物品体积 |
| `data.order.estimatedWeight` | Number | 预估重量 |
| `data.order.serviceType` | String | 服务类型 |
| `data.order.storageDays` | Integer | 暂存天数 |
| `data.order.amount` | Number | 订单金额 |
| `data.order.isPaid` | Boolean | 是否已支付 |
| `data.order.warehouseId` | String | 仓库ID |
| `data.order.statusHistory` | Array | 状态变更历史记录 |
| `data.order.createdAt` | String | 创建时间 |
| `data.order.updatedAt` | String | 最后更新时间 |

**statusHistory 数组元素结构**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `timestamp` | String | 变更时间（ISO 8601） |
| `fromStatus` | String | 原状态（首次创建为 `None`） |
| `toStatus` | String | 新状态 |
| `operatorType` | String | 操作人类型：`USER` / `ADMIN` / `SYSTEM` |
| `operatorId` | String | 操作人ID |
| `reason` | String | 变更原因 |
| `metadata` | Object | 附加信息 |

**成功响应示例**：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "order": {
      "orderId": "ord_a1b2c3d4e5f6",
      "orderNo": "ORD2026051000001",
      "status": "STORED",
      "city": "北京",
      "itemType": "LUGGAGE",
      "volume": 60.0,
      "estimatedWeight": 15.5,
      "serviceType": "STORAGE_DELIVERY",
      "storageDays": 30,
      "amount": 89.00,
      "isPaid": true,
      "warehouseId": "wh_bj_001",
      "statusHistory": [
        {
          "timestamp": "2026-05-10T10:30:00+08:00",
          "fromStatus": null,
          "toStatus": "PENDING",
          "operatorType": "USER",
          "operatorId": "oXJ9f5kQnZ8yWa7m",
          "reason": "USER_CREATE",
          "metadata": {}
        },
        {
          "timestamp": "2026-05-11T09:00:00+08:00",
          "fromStatus": "PENDING",
          "toStatus": "COLLECTED",
          "operatorType": "ADMIN",
          "operatorId": "admin_001",
          "reason": "ADMIN_COLLECT",
          "metadata": {}
        },
        {
          "timestamp": "2026-05-11T15:00:00+08:00",
          "fromStatus": "COLLECTED",
          "toStatus": "TRANSIT",
          "operatorType": "ADMIN",
          "operatorId": "admin_001",
          "reason": "ADMIN_DISPATCH",
          "metadata": {}
        },
        {
          "timestamp": "2026-05-12T14:00:00+08:00",
          "fromStatus": "TRANSIT",
          "toStatus": "STORED",
          "operatorType": "ADMIN",
          "operatorId": "admin_002",
          "reason": "ADMIN_STORE",
          "metadata": {
            "storagePhotoUrl": "cloud://env-id.xxxx/storage/ord_a1b2.jpg"
          }
        }
      ],
      "createdAt": "2026-05-10T10:30:00+08:00",
      "updatedAt": "2026-05-12T14:00:00+08:00"
    }
  }
}
```

**错误响应示例**：

```json
{
  "code": 2001,
  "message": "订单不存在：ord_invalid_id",
  "data": {}
}
```

---

### 3.5 取消订单

**云函数名**：`updateOrderStatus` / **Flask 路由**：`/api/v1/orders/status`

**功能说明**：用户取消处于 `PENDING` 状态的订单。已支付订单将自动触发退款。

**约束条件**：

- 仅 `PENDING` 状态可取消
- `operatorType` 必须为 `USER`
- 已支付订单取消后自动退款（退款由系统异步处理）

**请求参数**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `orderId` | String | 是 | 订单唯一ID |
| `newStatus` | String | 是 | 固定值 `"CANCELLED"` |
| `operatorType` | String | 是 | 固定值 `"USER"` |
| `reason` | String | 是 | 固定值 `"USER_CANCEL"` |

**请求示例**：

```json
{
  "orderId": "ord_a1b2c3d4e5f6",
  "newStatus": "CANCELLED",
  "operatorType": "USER",
  "reason": "USER_CANCEL"
}
```

**成功响应示例**：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "orderId": "ord_a1b2c3d4e5f6",
    "oldStatus": "PENDING",
    "newStatus": "CANCELLED",
    "updatedAt": "2026-05-10T16:00:00+08:00"
  }
}
```

**错误响应示例**：

```json
{
  "code": 2002,
  "message": "非法状态转换：当前状态 COLLECTED 不允许转换为 CANCELLED，仅 PENDING 状态可取消",
  "data": {}
}
```

```json
{
  "code": 2004,
  "message": "订单已终态：当前状态为 CANCELLED，不可变更",
  "data": {}
}
```

---

### 3.6 发起配送

**云函数名**：`updateOrderStatus` / **Flask 路由**：`/api/v1/orders/status`

**功能说明**：用户对已入库（`STORED`）的订单发起配送请求，需提供配送地址和期望配送时间。

**约束条件**：

- 仅 `STORED` 状态可发起配送
- `operatorType` 必须为 `USER`
- 需提供配送地址和配送时间

**请求参数**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `orderId` | String | 是 | 订单唯一ID |
| `newStatus` | String | 是 | 固定值 `"DELIVERING"` |
| `operatorType` | String | 是 | 固定值 `"USER"` |
| `reason` | String | 是 | 固定值 `"USER_REQUEST_DELIVERY"` |
| `metadata.deliveryAddress` | String | 是 | 配送地址 |
| `metadata.deliveryTime` | String | 是 | 期望配送时间（ISO 8601） |

**请求示例**：

```json
{
  "orderId": "ord_a1b2c3d4e5f6",
  "newStatus": "DELIVERING",
  "operatorType": "USER",
  "reason": "USER_REQUEST_DELIVERY",
  "metadata": {
    "deliveryAddress": "北京市海淀区中关村大街1号XX宿舍楼3层302",
    "deliveryTime": "2026-06-10T14:00:00+08:00"
  }
}
```

**成功响应示例**：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "orderId": "ord_a1b2c3d4e5f6",
    "oldStatus": "STORED",
    "newStatus": "DELIVERING",
    "updatedAt": "2026-05-15T10:00:00+08:00"
  }
}
```

**错误响应示例**：

```json
{
  "code": 1001,
  "message": "参数校验失败：metadata.deliveryAddress 不能为空",
  "data": {}
}
```

---

### 3.7 确认收货

**云函数名**：`updateOrderStatus` / **Flask 路由**：`/api/v1/orders/status`

**功能说明**：用户确认收到配送物品，订单进入终态 `COMPLETED`。

**约束条件**：

- 仅 `DELIVERING` 状态可确认收货
- `operatorType` 必须为 `USER`
- 确认后订单不可逆（投诉走独立工单系统）

**请求参数**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `orderId` | String | 是 | 订单唯一ID |
| `newStatus` | String | 是 | 固定值 `"COMPLETED"` |
| `operatorType` | String | 是 | 固定值 `"USER"` |
| `reason` | String | 是 | 固定值 `"USER_CONFIRM"` |

**请求示例**：

```json
{
  "orderId": "ord_a1b2c3d4e5f6",
  "newStatus": "COMPLETED",
  "operatorType": "USER",
  "reason": "USER_CONFIRM"
}
```

**成功响应示例**：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "orderId": "ord_a1b2c3d4e5f6",
    "oldStatus": "DELIVERING",
    "newStatus": "COMPLETED",
    "updatedAt": "2026-05-18T16:30:00+08:00"
  }
}
```

---

### 3.8 创建投诉工单

**云函数名**：`createTicket` / **Flask 路由**：`/api/v1/tickets/create`

**功能说明**：用户对已完成（`COMPLETED`）的订单创建投诉工单，投诉走独立工单系统，不修改订单状态。

**请求参数**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `orderId` | String | 是 | 关联的订单唯一ID |
| `type` | String | 是 | 投诉类型枚举：`ITEM_DAMAGE`(物品损坏)、`ITEM_LOSS`(物品丢失)、`DELAY`(配送延迟)、`OTHER`(其他) |
| `description` | String | 是 | 投诉描述，最少10字，最多500字 |
| `imageUrl` | String | 否 | 凭证图片 URL（最多3张，逗号分隔） |

**请求示例**：

```json
{
  "orderId": "ord_a1b2c3d4e5f6",
  "type": "ITEM_DAMAGE",
  "description": "收到行李箱时发现侧面有明显凹陷，箱体变形无法正常使用",
  "imageUrl": "cloud://env-id.xxxx/ticket/img001.jpg,cloud://env-id.xxxx/ticket/img002.jpg"
}
```

**响应参数**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `data.ticketId` | String | 工单唯一ID |
| `data.ticketNo` | String | 工单编号（如 `"TKT2026051800001"`） |
| `data.createdAt` | String | 创建时间（ISO 8601） |

**成功响应示例**：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "ticketId": "tkt_x1y2z3w4",
    "ticketNo": "TKT2026051800001",
    "createdAt": "2026-05-18T17:00:00+08:00"
  }
}
```

**错误响应示例**：

```json
{
  "code": 1001,
  "message": "参数校验失败：description 长度不能少于10字",
  "data": {}
}
```

---

## 四、运营端接口

> **鉴权要求**：以下运营端接口均要求 `operatorType == 'ADMIN'`，云函数内会校验当前用户的 `openId` 是否在管理员白名单中。非管理员调用返回 `code: 1003`。

### 4.1 确认取件

**云函数名**：`updateOrderStatus` / **Flask 路由**：`/api/v1/orders/status`

**功能说明**：运营人员确认已取件（揽收），订单从 `PENDING` 转为 `COLLECTED`。

**请求参数**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `orderId` | String | 是 | 订单唯一ID |
| `newStatus` | String | 是 | 固定值 `"COLLECTED"` |
| `operatorType` | String | 是 | 固定值 `"ADMIN"` |
| `reason` | String | 是 | 固定值 `"ADMIN_COLLECT"` |
| `metadata.collectorName` | String | 否 | 取件人姓名 |
| `metadata.collectNote` | String | 否 | 取件备注 |

**请求示例**：

```json
{
  "orderId": "ord_a1b2c3d4e5f6",
  "newStatus": "COLLECTED",
  "operatorType": "ADMIN",
  "reason": "ADMIN_COLLECT",
  "metadata": {
    "collectorName": "李师傅",
    "collectNote": "用户自送到仓"
  }
}
```

**成功响应示例**：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "orderId": "ord_a1b2c3d4e5f6",
    "oldStatus": "PENDING",
    "newStatus": "COLLECTED",
    "updatedAt": "2026-05-11T09:00:00+08:00"
  }
}
```

---

### 4.2 发运

**云函数名**：`updateOrderStatus` / **Flask 路由**：`/api/v1/orders/status`

**功能说明**：运营人员将已揽收的物品发运，订单从 `COLLECTED` 转为 `TRANSIT`。

> **业务提醒**：`COLLECTED` 状态超过24小时未发运，系统将自动提醒运营人员。

**请求参数**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `orderId` | String | 是 | 订单唯一ID |
| `newStatus` | String | 是 | 固定值 `"TRANSIT"` |
| `operatorType` | String | 是 | 固定值 `"ADMIN"` |
| `reason` | String | 是 | 固定值 `"ADMIN_DISPATCH"` |
| `metadata.trackingNo` | String | 否 | 物流单号 |
| `metadata.carrier` | String | 否 | 承运商名称 |

**请求示例**：

```json
{
  "orderId": "ord_a1b2c3d4e5f6",
  "newStatus": "TRANSIT",
  "operatorType": "ADMIN",
  "reason": "ADMIN_DISPATCH",
  "metadata": {
    "trackingNo": "SF1234567890",
    "carrier": "顺丰速运"
  }
}
```

**成功响应示例**：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "orderId": "ord_a1b2c3d4e5f6",
    "oldStatus": "COLLECTED",
    "newStatus": "TRANSIT",
    "updatedAt": "2026-05-11T15:00:00+08:00"
  }
}
```

---

### 4.3 入库

**云函数名**：`updateOrderStatus` / **Flask 路由**：`/api/v1/orders/status`

**功能说明**：运营人员确认物品到仓并拍照入库，订单从 `TRANSIT` 转为 `STORED`。

**请求参数**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `orderId` | String | 是 | 订单唯一ID |
| `newStatus` | String | 是 | 固定值 `"STORED"` |
| `operatorType` | String | 是 | 固定值 `"ADMIN"` |
| `reason` | String | 是 | 固定值 `"ADMIN_STORE"` |
| `metadata.storagePhotoUrl` | String | 是 | 入库照片 URL（必填，至少1张） |
| `metadata.storageLocation` | String | 否 | 仓库存储位置（如 `"A区-3排-2层"`） |

**请求示例**：

```json
{
  "orderId": "ord_a1b2c3d4e5f6",
  "newStatus": "STORED",
  "operatorType": "ADMIN",
  "reason": "ADMIN_STORE",
  "metadata": {
    "storagePhotoUrl": "cloud://env-id.xxxx/storage/ord_a1b2.jpg",
    "storageLocation": "A区-3排-2层"
  }
}
```

**成功响应示例**：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "orderId": "ord_a1b2c3d4e5f6",
    "oldStatus": "TRANSIT",
    "newStatus": "STORED",
    "updatedAt": "2026-05-12T14:00:00+08:00"
  }
}
```

**错误响应示例**：

```json
{
  "code": 1001,
  "message": "参数校验失败：入库操作必须上传入库照片（metadata.storagePhotoUrl）",
  "data": {}
}
```

---

### 4.4 标记异常

**云函数名**：`updateOrderStatus` / **Flask 路由**：`/api/v1/orders/status`

**功能说明**：管理员将订单标记为异常状态，所有非终态均可标记异常。需填写异常原因。

**请求参数**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `orderId` | String | 是 | 订单唯一ID |
| `newStatus` | String | 是 | 固定值 `"EXCEPTION"` |
| `operatorType` | String | 是 | 固定值 `"ADMIN"` |
| `reason` | String | 是 | 异常原因枚举：`ITEM_DAMAGE`(物品损坏)、`ITEM_LOSS`(物品丢失)、`DELIVERY_FAILED`(配送失败)、`ADMIN_MARK_EXCEPTION`(其他异常) |
| `metadata.description` | String | 否 | 异常详细描述 |
| `metadata.imageUrl` | String | 否 | 异常凭证图片 URL |

**请求示例**：

```json
{
  "orderId": "ord_a1b2c3d4e5f6",
  "newStatus": "EXCEPTION",
  "operatorType": "ADMIN",
  "reason": "ITEM_DAMAGE",
  "metadata": {
    "description": "运输过程中行李箱侧面凹陷，已拍照留证",
    "imageUrl": "cloud://env-id.xxxx/exception/dmg001.jpg"
  }
}
```

**成功响应示例**：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "orderId": "ord_a1b2c3d4e5f6",
    "oldStatus": "TRANSIT",
    "newStatus": "EXCEPTION",
    "updatedAt": "2026-05-12T16:00:00+08:00"
  }
}
```

---

### 4.5 异常结案

**云函数名**：`updateOrderStatus` / **Flask 路由**：`/api/v1/orders/status`

**功能说明**：管理员对异常订单进行结案处理，订单从 `EXCEPTION` 转为 `COMPLETED`（终态）。

> **典型场景**：破损赔偿后完结、丢失补发后确认收货。

**请求参数**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `orderId` | String | 是 | 订单唯一ID |
| `newStatus` | String | 是 | 固定值 `"COMPLETED"` |
| `operatorType` | String | 是 | 固定值 `"ADMIN"` |
| `reason` | String | 是 | 固定值 `"ADMIN_RESOLVE"` |
| `metadata.resolution` | String | 否 | 处理结果说明（如 `"已赔偿50元，用户确认"`） |

**请求示例**：

```json
{
  "orderId": "ord_a1b2c3d4e5f6",
  "newStatus": "COMPLETED",
  "operatorType": "ADMIN",
  "reason": "ADMIN_RESOLVE",
  "metadata": {
    "resolution": "已赔偿50元，用户确认完结"
  }
}
```

**成功响应示例**：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "orderId": "ord_a1b2c3d4e5f6",
    "oldStatus": "EXCEPTION",
    "newStatus": "COMPLETED",
    "updatedAt": "2026-05-15T11:00:00+08:00"
  }
}
```

---

### 4.6 异常作废

**云函数名**：`updateOrderStatus` / **Flask 路由**：`/api/v1/orders/status`

**功能说明**：管理员对异常订单进行作废处理，订单从 `EXCEPTION` 转为 `CANCELLED`（终态）。

> **典型场景**：配送失败无法恢复，取消 + 退款 + 建议用户重新下单。

**请求参数**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `orderId` | String | 是 | 订单唯一ID |
| `newStatus` | String | 是 | 固定值 `"CANCELLED"` |
| `operatorType` | String | 是 | 固定值 `"ADMIN"` |
| `reason` | String | 是 | 固定值 `"ADMIN_VOID"` |
| `metadata.resolution` | String | 否 | 处理结果说明 |
| `metadata.refundAmount` | Number | 否 | 退款金额（如已支付则自动退款） |

**请求示例**：

```json
{
  "orderId": "ord_a1b2c3d4e5f6",
  "newStatus": "CANCELLED",
  "operatorType": "ADMIN",
  "reason": "ADMIN_VOID",
  "metadata": {
    "resolution": "配送失败，物品退回，已全额退款",
    "refundAmount": 89.00
  }
}
```

**成功响应示例**：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "orderId": "ord_a1b2c3d4e5f6",
    "oldStatus": "EXCEPTION",
    "newStatus": "CANCELLED",
    "updatedAt": "2026-05-15T14:00:00+08:00"
  }
}
```

---

### 4.7 运营订单列表

**云函数名**：`getOrderList` / **Flask 路由**：`/api/v1/orders/list`

**功能说明**：运营端查询所有用户的订单列表，支持按状态筛选和分页。

> **权限说明**：运营端可查看所有用户的订单，不受用户维度过滤限制。

**请求参数**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `status` | String | 否 | 按订单状态筛选，不填则返回全部 |
| `page` | Integer | 是 | 页码，从 `1` 开始 |
| `pageSize` | Integer | 是 | 每页条数，建议 `10~20`，最大 `50` |

**请求示例**：

```json
{
  "status": "EXCEPTION",
  "page": 1,
  "pageSize": 20
}
```

**响应参数**：

与用户端 `getOrderList`（3.3）响应结构一致，额外包含以下字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| `data.list[].userNickName` | String | 下单用户昵称 |
| `data.list[].userOpenId` | String | 下单用户 openId（脱敏显示） |

**成功响应示例**：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "total": 1,
    "page": 1,
    "pageSize": 20,
    "list": [
      {
        "orderId": "ord_a1b2c3d4e5f6",
        "orderNo": "ORD2026051000001",
        "status": "EXCEPTION",
        "itemType": "LUGGAGE",
        "serviceType": "STORAGE_DELIVERY",
        "amount": 89.00,
        "createdAt": "2026-05-10T10:30:00+08:00",
        "updatedAt": "2026-05-12T16:00:00+08:00",
        "userNickName": "张三",
        "userOpenId": "oXJ9f5***7m3L"
      }
    ]
  }
}
```

---

## 五、核心接口详细设计

### 5.1 updateOrderStatus（核心接口）

> 引用自《订单状态机设计文档.md》v2.0

**云函数名**：`updateOrderStatus` / **Flask 路由**：`/api/v1/orders/status`

**功能说明**：统一的状态变更接口，所有订单状态流转均通过此接口完成。内部实现状态转换校验、权限校验、乐观锁并发控制和操作日志记录。

**函数签名**：

```python
def main(event, context):
    """
    输入：event = { orderId, newStatus, operatorType, operatorId, reason, metadata }
    输出：成功返回新状态 + 记录，失败返回 { "code": int, "message": str }
    """
```

**请求参数**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `orderId` | String | 是 | 订单唯一ID |
| `newStatus` | String | 是 | 目标状态枚举值 |
| `operatorType` | String | 是 | 操作人类型：`USER` / `ADMIN` / `SYSTEM` |
| `operatorId` | String | 否 | 操作人ID（云函数可从 `event['userInfo']['openId']` 自动获取） |
| `reason` | String | 是 | 状态变更原因（枚举约束，见下表） |
| `metadata` | Object | 否 | 附加信息（如物流单号、仓库位置、照片URL等） |

**reason 枚举值**：

| 枚举值 | 说明 | 适用角色 |
|--------|------|---------|
| `USER_CANCEL` | 用户主动取消 | USER |
| `USER_REQUEST_DELIVERY` | 用户发起配送 | USER |
| `USER_CONFIRM` | 用户确认收货 | USER |
| `ADMIN_COLLECT` | 运营确认取件 | ADMIN |
| `ADMIN_DISPATCH` | 运营发运 | ADMIN |
| `ADMIN_STORE` | 运营入库 | ADMIN |
| `ADMIN_MARK_EXCEPTION` | 管理员标记异常 | ADMIN |
| `ADMIN_RESOLVE` | 管理员异常结案 | ADMIN |
| `ADMIN_VOID` | 管理员异常作废 | ADMIN |
| `TIMEOUT_CANCEL` | 超时自动取消 | SYSTEM |
| `AUTO_COMPLETE` | 超时自动完结 | SYSTEM |

---

#### 5.1.1 状态转换校验矩阵

> 以下矩阵定义了所有合法的状态转换路径，任何不在矩阵中的转换将被拒绝（返回错误码 `2002`）。

| 当前状态 | 可转换目标 | 所需 operatorType | 说明 |
|---------|-----------|-------------------|------|
| `PENDING` | `COLLECTED` | `ADMIN` | 运营确认取件 / 用户自送到仓 |
| `PENDING` | `CANCELLED` | `USER`, `SYSTEM` | 用户主动取消 / 超时自动取消 |
| `PENDING` | `EXCEPTION` | `ADMIN` | 管理员标记异常 |
| `COLLECTED` | `TRANSIT` | `ADMIN` | 运营手动发运 |
| `COLLECTED` | `EXCEPTION` | `ADMIN` | 管理员标记异常 |
| `TRANSIT` | `STORED` | `ADMIN` | 到仓拍照入库 |
| `TRANSIT` | `EXCEPTION` | `ADMIN` | 管理员标记异常 |
| `STORED` | `DELIVERING` | `USER` | 用户发起配送 |
| `STORED` | `EXCEPTION` | `ADMIN` | 管理员标记异常 |
| `DELIVERING` | `COMPLETED` | `USER`, `SYSTEM` | 手动确认 / 7天超时自动完结 |
| `DELIVERING` | `EXCEPTION` | `ADMIN` | 管理员标记异常（含配送失败退回） |
| `EXCEPTION` | `COMPLETED` | `ADMIN` | 人工结案（如：破损赔偿后完结） |
| `EXCEPTION` | `CANCELLED` | `ADMIN` | 人工作废（如：配送失败→取消+退款+重下单） |

**终态（不可转换）**：

| 终态 | 说明 |
|------|------|
| `COMPLETED` | 订单正常完结，不可逆。后续投诉走独立工单系统 |
| `CANCELLED` | 订单已取消，不可逆 |

---

#### 5.1.2 乐观锁处理流程

> 引用自状态机设计文档 Q7 决策：CloudBase `_version` 乐观锁，云函数内重试最多3次。

```
┌─────────────────────────────────────┐
│ 1. 查询订单当前 status 和 _version   │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 2. 校验状态转换合法性                 │
│    - 当前状态是否允许转换到目标状态    │
│    - 不合法 → 返回 code: 2002        │
└──────────────┬──────────────────────┘
               │ 合法
               ▼
┌─────────────────────────────────────┐
│ 3. 校验 operatorType 权限            │
│    - 当前转换是否允许该角色操作       │
│    - 不允许 → 返回 code: 1003        │
└──────────────┬──────────────────────┘
               │ 有权限
               ▼
┌─────────────────────────────────────┐
│ 4. 使用 _version 条件更新            │
│    db.collection('orders').update(   │
│      { _id: orderId, _version: v }, │
│      { $set: { status, ... },       │
│        $inc: { _version: 1 } }      │
│    )                                 │
└──────────────┬──────────────────────┘
               │
        ┌──────┴──────┐
        │ 更新成功？   │
        ├──────┬──────┤
        │ 是   │ 否   │
        ▼      ▼      ▼
   ┌────────┐ ┌──────────────────┐
   │ 5.写入 │ │ 6. 重试（最多3次）│
   │status  │ │ 检查重试次数       │
   │History │ │ 超限 → 返回       │
   └───┬────┘ │ code: 2003        │
       │      └──────────────────┘
       ▼
┌─────────────────────────────────────┐
│ 7. 返回成功响应                       │
│    { orderId, oldStatus, newStatus,  │
│      updatedAt }                     │
└─────────────────────────────────────┘
```

**幂等性保证**：重试前检查 `statusHistory` 末条记录的 `toStatus` 是否已等于目标状态，避免同一次变更写入多条日志。

---

#### 5.1.3 完整请求/响应示例

**示例1：正常状态转换（PENDING → COLLECTED）**

请求：

```json
{
  "orderId": "ord_a1b2c3d4e5f6",
  "newStatus": "COLLECTED",
  "operatorType": "ADMIN",
  "operatorId": "admin_001",
  "reason": "ADMIN_COLLECT",
  "metadata": {
    "collectorName": "李师傅",
    "collectNote": "用户自送到仓"
  }
}
```

成功响应：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "orderId": "ord_a1b2c3d4e5f6",
    "oldStatus": "PENDING",
    "newStatus": "COLLECTED",
    "statusHistoryEntry": {
      "timestamp": "2026-05-11T09:00:00+08:00",
      "fromStatus": "PENDING",
      "toStatus": "COLLECTED",
      "operatorType": "ADMIN",
      "operatorId": "admin_001",
      "reason": "ADMIN_COLLECT",
      "metadata": {
        "collectorName": "李师傅",
        "collectNote": "用户自送到仓"
      }
    },
    "updatedAt": "2026-05-11T09:00:00+08:00"
  }
}
```

---

**示例2：非法状态转换（COLLECTED → CANCELLED，用户尝试取消已揽收订单）**

请求：

```json
{
  "orderId": "ord_a1b2c3d4e5f6",
  "newStatus": "CANCELLED",
  "operatorType": "USER",
  "reason": "USER_CANCEL"
}
```

失败响应：

```json
{
  "code": 2002,
  "message": "非法状态转换：当前状态 COLLECTED 不允许转换为 CANCELLED。仅 PENDING 状态可由用户取消，COLLECTED 及之后状态需联系管理员处理。",
  "data": {
    "orderId": "ord_a1b2c3d4e5f6",
    "currentStatus": "COLLECTED",
    "targetStatus": "CANCELLED",
    "allowedTransitions": ["TRANSIT", "EXCEPTION"]
  }
}
```

---

## 六、接口安全

### 6.1 权限校验矩阵

> 以下矩阵定义了每个操作允许的角色，云函数内必须严格执行校验。

| 操作 | USER | ADMIN | SYSTEM | 说明 |
|------|------|-------|--------|------|
| 创建订单 | Y | - | - | 用户端小程序操作 |
| 查看订单列表 | Y | Y | - | 用户看自己的，运营看全部 |
| 查看订单详情 | Y | Y | - | 用户看自己的，运营看全部 |
| 取消订单（PENDING→CANCELLED） | Y | - | Y | 超时取消由系统触发 |
| 确认取件（PENDING→COLLECTED） | - | Y | - | 运营专属 |
| 发运（COLLECTED→TRANSIT） | - | Y | - | 运营专属 |
| 入库（TRANSIT→STORED） | - | Y | - | 运营专属 |
| 发起配送（STORED→DELIVERING） | Y | - | - | 用户端操作 |
| 确认收货（DELIVERING→COMPLETED） | Y | - | Y | 超时自动完结由系统触发 |
| 标记异常（任意→EXCEPTION） | - | Y | - | 仅管理员 |
| 异常结案（EXCEPTION→COMPLETED） | - | Y | - | 仅管理员 |
| 异常作废（EXCEPTION→CANCELLED） | - | Y | - | 仅管理员 |
| 创建投诉工单 | Y | - | - | 用户端操作 |

> **Y** = 允许，**-** = 禁止

### 6.2 参数校验规则

**通用校验规则**：

| 规则 | 说明 |
|------|------|
| 必填字段检查 | 所有标记为"必填"的参数不得为 `None` 或空字符串 |
| 枚举值校验 | `status`、`operatorType`、`reason`、`itemType`、`serviceType` 等枚举字段必须在允许值范围内 |
| 字符串长度 | `description`（投诉描述）：10~500字；`deliveryAddress`（配送地址）：5~200字 |
| 数值范围 | `storageDays`：1~365；`volume`：0.1~500.0；`estimatedWeight`：0.1~100.0 |
| 分页参数 | `page` >= 1；`pageSize` 范围 1~50 |
| orderId 格式 | 必须为有效的数据库记录ID，格式校验：`ord_` 前缀 + 12位十六进制字符 |

**updateOrderStatus 专项校验**：

| 校验项 | 规则 |
|--------|------|
| 终态校验 | 当前状态为 `COMPLETED` 或 `CANCELLED` 时，拒绝任何状态变更（返回 `2004`） |
| 状态转换合法性 | 目标转换必须在状态转换校验矩阵中（返回 `2002`） |
| 角色权限 | `operatorType` 必须与状态转换校验矩阵中定义的角色匹配（返回 `1003`） |
| reason 必填 | 所有状态变更必须提供 `reason`，且值为合法枚举 |
| metadata 条件必填 | 入库操作必须提供 `storagePhotoUrl`；发起配送必须提供 `deliveryAddress` 和 `deliveryTime` |

### 6.3 限流策略

> **Demo 阶段暂不实现**，以下为生产环境建议方案，供后续迭代参考。

| 策略 | 说明 | 建议阈值 |
|------|------|---------|
| 用户级限流 | 单用户每分钟请求次数上限 | 60 次/分钟 |
| 接口级限流 | 单接口每秒请求次数上限 | 100 次/秒 |
| 全局限流 | 服务总 QPS 上限 | 1000 QPS |
| 状态变更限流 | 单订单状态变更频率限制 | 10 次/分钟 |

**实现建议**：CloudBase 可通过云函数内访问 Redis（云开发内置）或使用数据库计数器实现简单限流。

---

## 七、数据模型参考

### 7.1 Order（订单）完整字段

> 以下字段定义供接口开发参考，数据库设计详见《04_数据库设计文档.md》。

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `_id` | String | 订单唯一ID（orderId） |
| `_version` | Integer | 乐观锁版本号，每次更新自增 |
| `orderNo` | String | 订单编号（用户可见） |
| `status` | Enum | 订单当前状态 |
| `isPaid` | Boolean | 是否已支付（独立于状态机） |
| `paidAt` | DateTime | 支付时间 |
| `openId` | String | 下单用户 openId |
| `city` | String | 所在城市 |
| `itemType` | Enum | 物品类型 |
| `volume` | Number | 物品体积（升） |
| `estimatedWeight` | Number | 预估重量（kg） |
| `serviceType` | Enum | 服务类型 |
| `storageDays` | Integer | 暂存天数 |
| `warehouseId` | String | 仓库ID |
| `amount` | Number | 订单金额（元） |
| `statusHistory` | Array | 状态变更历史记录数组 |
| `createdAt` | DateTime | 创建时间 |
| `updatedAt` | DateTime | 最后更新时间 |

### 7.2 状态枚举值汇总

| 枚举值 | 中文名称 | 类型 |
|--------|---------|------|
| `PENDING` | 待交付 | 订单状态 |
| `COLLECTED` | 已揽收 | 订单状态 |
| `TRANSIT` | 运输中 | 订单状态 |
| `STORED` | 已入库 | 订单状态 |
| `DELIVERING` | 配送中 | 订单状态 |
| `COMPLETED` | 已完成 | 订单状态（终态） |
| `CANCELLED` | 已取消 | 订单状态（终态） |
| `EXCEPTION` | 异常状态 | 订单状态 |
| `USER` | 用户 | 操作人类型 |
| `ADMIN` | 管理员 | 操作人类型 |
| `SYSTEM` | 系统 | 操作人类型 |
| `STORAGE` | 暂存 | 服务类型 |
| `STORAGE_DELIVERY` | 暂存+配送 | 服务类型 |
| `LUGGAGE` | 行李 | 物品类型 |
| `PARCEL` | 包裹 | 物品类型 |
| `ELECTRONICS` | 电子产品 | 物品类型 |
| `OTHER` | 其他 | 物品类型 |

---

## 八、自动化规则（系统触发）

> 以下规则由云函数定时触发器执行，`operatorType` 固定为 `SYSTEM`。

| 规则 | 触发条件 | 执行动作 | 调用接口 |
|------|---------|---------|---------|
| 发运提醒 | `COLLECTED` 状态超过24小时 | 系统发送订阅消息提醒运营人员 | 内部通知，不调用 updateOrderStatus |
| 自动完结 | `DELIVERING` 状态超过7天 | 自动转为 `COMPLETED` | `updateOrderStatus`（operatorType=SYSTEM, reason=AUTO_COMPLETE） |
| 超时取消 | `PENDING` 状态超过交付窗口期（7天） | 自动转为 `CANCELLED`，区分 `isPaid` 决定是否自动退款 | `updateOrderStatus`（operatorType=SYSTEM, reason=TIMEOUT_CANCEL） |

> **计时说明**：
> - 自动完结：以 `statusHistory` 中 `DELIVERING` 状态的 `timestamp` 为起点计算7天
> - 超时取消：以订单创建时间 + 用户选择的交付窗口期结束时间为起点计算7天

---

## 九、待决策项

- [ ] 是否需要接口版本管理（v1/v2）—— 当前为 Demo MVP，建议暂不引入版本管理，后续如需不兼容变更再考虑
- [ ] 分页默认 `pageSize` 设为多少 —— 建议 `10`，与小程序端列表展示习惯一致
- [ ] 订单编号生成规则 —— 建议格式 `ORD` + `YYYYMMDD` + 6位自增序号（如 `ORD20260510000001`）
- [ ] 管理员白名单管理方式 —— 建议初期使用云开发环境变量，后续迁移至独立配置集合
- [ ] 是否需要接口请求签名防篡改 —— Demo 阶段依赖 HTTPS + 云函数鉴权，生产环境建议增加签名机制

---

## 附录

### A. 云函数清单

| 云函数名 | 功能 | 调用端 | 触发方式 | Flask 路由 |
|---------|------|--------|---------|-----------|
| `login` | 用户登录 | 用户端 | HTTP | `/api/v1/login` |
| `createOrder` | 创建订单 | 用户端 | HTTP | `/api/v1/orders/create` |
| `getOrderList` | 获取订单列表 | 用户端 + 运营端 | HTTP | `/api/v1/orders/list` |
| `getOrderDetail` | 获取订单详情 | 用户端 + 运营端 | HTTP | `/api/v1/orders/detail` |
| `updateOrderStatus` | 状态变更（核心） | 用户端 + 运营端 + 系统 | HTTP + 定时触发器 | `/api/v1/orders/status` |
| `createTicket` | 创建投诉工单 | 用户端 | HTTP | `/api/v1/tickets/create` |

### B. 关联文档

| 文档 | 版本 | 说明 |
|------|------|------|
| 《订单状态机设计文档.md》 | v2.0 | 状态机流转规则、设计决策 |
| 《04_数据库设计文档.md》 | v2.0 | 数据模型与集合设计（含本地 SQLite 表结构） |
| 《01_产品需求文档_PRD.md》 | - | 产品需求与业务规则 |

### C. 变更记录

| 版本 | 日期 | 变更内容 | 作者 |
|------|------|---------|------|
| v2.0 | 2026-05-10 | 适配"本地Python开发 → 统一部署"模式：新增本地开发 Flask 路由映射、X-OpenId 鉴权方式、本地调试示例 | - |
| v1.1 | 2026-05-10 | 技术栈从Node.js迁移至Python 3.12+ | - |
| v1.0 | 2026-05-10 | 初稿创建 | - |
