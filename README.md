# Software Auth API

多软件授权支付平台

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 填入实际值

# 3. 启动
uvicorn app.main:app --host 0.0.0.0 --port 5006
```

## ⚠️ 安全警告（生产环境必读）

**以下环境变量必须设置，否则服务无法正常运行：**

| 变量 | 说明 | 必须 |
|---|---|---|
| `JWT_SECRET` | JWT签名密钥（生成: `python3 -c "import secrets; print(secrets.token_hex(32))"`） | ✅ 必须 |
| `CALLBACK_SIGN_KEY` | 支付回调HMAC签名密钥 | ✅ 必须 |
| `GATEWAY_TOKEN` | 支付网关简单Token认证 | ✅ 必须 |
| `DB_PASSWORD` | 数据库密码（默认为空，必须设置） | ✅ 必须 |
| `DEBUG` | 调试模式（生产设为 `false`） | ⚠️ 建议 |

**⚠️ 禁止使用默认密钥部署到生产环境！**

## 架构

- FastAPI + SQLAlchemy + Redis
- JWT认证 + HMAC签名验签
- 多软件隔离（app_id）
- 统一支付网关集成

## API文档

启动后访问: `http://localhost:5006/docs`
