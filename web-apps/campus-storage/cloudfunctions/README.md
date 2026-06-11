# CloudBase 云函数

本项目使用腾讯云 CloudBase 云开发作为生产环境托管方案。

## 云函数列表

| 云函数 | 类型 | 描述 | 触发方式 |
|--------|------|------|----------|
| login | HTTP | 用户登录获取openid | HTTP请求 |
| createOrder | HTTP | 创建订单 | HTTP请求 |
| getOrderList | HTTP | 获取订单列表 | HTTP请求 |
| getOrderDetail | HTTP | 获取订单详情 | HTTP请求 |
| updateOrderStatus | HTTP | 更新订单状态（管理员） | HTTP请求 |
| pendingTimeoutChecker | Timer | PENDING订单超时检查 | 定时触发（每30分钟） |
| deliveringTimeoutChecker | Timer | DELIVERING订单超时检查 | 定时触发（每30分钟） |

## 目录结构

```
cloudfunctions/
├── login/                    # 登录云函数
│   ├── index.py             # 入口文件
│   ├── config.json          # 云函数配置
│   └── requirements.txt     # 依赖清单
├── createOrder/             # 创建订单
│   ├── index.py
│   ├── cloudbase.py         # CloudBase SDK封装
│   ├── config.json
│   └── requirements.txt
├── getOrderList/            # 获取订单列表
├── getOrderDetail/          # 获取订单详情
├── updateOrderStatus/       # 更新订单状态
├── pendingTimeoutChecker/   # 超时检查（定时）
├── deliveringTimeoutChecker/# 配送超时检查（定时）
├── .env.example             # 环境变量示例
└── README.md                # 本文件
```

## 配置说明

### config.json

```json
{
  "runtime": "Python3.12",    // 运行环境
  "timeout": 20,              // 超时时间（秒）
  "memorySize": 256,          // 内存大小（MB）
  "triggers": [               // 触发器配置（仅定时函数）
    {
      "type": "timer",
      "config": "0 */30 * * * * *"  // Cron表达式
    }
  ]
}
```

### 环境变量

| 变量名 | 说明 | 示例 |
|--------|------|------|
| TCB_ENV_ID | CloudBase环境ID | dev-xxx |
| WX_APPID | 微信小程序AppID | wx123456789 |
| WX_SECRET | 微信小程序Secret | xxx |
| ADMIN_OPENIDS | 管理员openid列表（逗号分隔） | openid1,openid2 |
| STORAGE_FEE_RATE | 暂存费单价（元/天） | 0.5 |
| TIMEOUT_DAYS | PENDING超时天数 | 7 |
| DELIVERING_TIMEOUT_HOURS | 配送超时小时数 | 24 |

## 部署方式

### 方式一：使用部署脚本

```bash
# 部署所有云函数
python scripts/deploy_cloudfunctions.py --env-id <环境ID>

# 部署单个云函数
python scripts/deploy_cloudfunctions.py --env-id <环境ID> --function login

# 预览模式
python scripts/deploy_cloudfunctions.py --env-id <环境ID> --dry-run
```

### 方式二：使用 CloudBase CLI

```bash
# 安装 CLI
npm install -g @cloudbase/cli

# 登录
tcb login

# 部署单个云函数
tcb fn deploy login -e <环境ID>

# 部署所有云函数
tcb fn deploy -e <环境ID>
```

### 方式三：微信开发者工具

1. 打开微信开发者工具
2. 进入"云开发" → "云函数"
3. 右键云函数目录 → "上传并部署：云端安装依赖"

## 本地测试

```bash
# 安装依赖
pip install -r requirements.txt

# 运行测试
python -m pytest tests/test_cloudfunctions/
```

## 注意事项

1. **Python版本**：所有云函数使用 Python 3.12 运行时
2. **依赖管理**：每个云函数独立管理依赖，云端自动安装
3. **环境变量**：敏感配置通过环境变量注入，不硬编码
4. **超时设置**：HTTP函数默认10-20秒，定时函数60秒
5. **内存配置**：HTTP函数128-256MB，定时函数256MB
