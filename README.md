# OrderTracker 订单跟踪系统

一个基于 FastAPI 的订单跟踪系统，用于管理商品下单任务，支持用户下单限制、订单状态跟踪和完整的订单生命周期管理。

## 🚀 功能特性

- **智能下单限制**: 同一用户在同一店铺24小时内只能下一单，防止重复下单
- **订单状态管理**: 支持进行中、完成、失败三种状态
- **完整订单信息**: 记录订单号、支付宝交易号、收货信息等详细数据
- **时区感知**: 支持UTC时间存储，本地时间显示
- **RESTful API**: 提供完整的REST API接口
- **数据库迁移**: 使用Alembic进行数据库版本管理
- **容器化部署**: 支持Docker和Docker Compose一键部署

## 📋 技术栈

- **后端框架**: FastAPI 0.116+
- **数据库**: MySQL 8.0
- **ORM**: SQLAlchemy 2.0
- **数据验证**: Pydantic 2.11+
- **数据库迁移**: Alembic 1.16+
- **容器化**: Docker & Docker Compose
- **数据库管理**: phpMyAdmin

## 🛠️ 快速开始

### 方式一：Docker Compose 部署（推荐）

1. **克隆项目**
```bash
git clone <repository-url>
cd OrderTracker
```

2. **启动服务**
```bash
docker-compose up -d
```

3. **访问服务**
- API 服务: http://localhost:8000
- API 文档: http://localhost:8000/docs
- 数据库管理: http://localhost:8080

### 方式二：本地开发环境

1. **环境要求**
- Python 3.13+
- MySQL 8.0+

2. **安装依赖**
```bash
# 使用 uv (推荐)
uv sync

# 或使用 pip
pip install -r requirements.txt
```

3. **配置数据库**
```bash
# 创建数据库
mysql -u root -p -e "CREATE DATABASE ordertracker;"

# 设置环境变量
export DATABASE_URL="mysql+pymysql://username:password@localhost:3306/ordertracker"
```

4. **运行数据库迁移**
```bash
alembic upgrade head
```

5. **启动应用**
```bash
python main.py
```

## 📚 API 接口

### 健康检查
```http
GET /health
```

### 创建下单任务
```http
POST /product
Content-Type: application/json

{
  "user_name": "张三",
  "shop_name": "测试店铺",
  "product_url": "https://example.com/product/123",
  "product_price": 99.99,
  "product_sku": "SKU123456"
}
```

### 更新订单信息
```http
PUT /order/update
Content-Type: application/json

{
  "task_uuid": "550e8400-e29bxxxd4-a7xxx6655440001",
  "order_id": "28565xxxxxx41363",
  "alipay_trade_no": "2025073xxxxxx1402512358",
  "receiver_name": "xxx",
  "receiver_address": "xxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "receiver_phone": "17858574473",
  "order_status": 2
}
```

## 🗄️ 数据库结构

### order_tasks 表

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | INT | 主键，自增ID |
| task_uuid | VARCHAR(36) | 任务唯一标识符 |
| user_name | VARCHAR(100) | 用户名 |
| shop_name | VARCHAR(200) | 店铺名称 |
| product_url | TEXT | 商品链接 |
| product_price | DECIMAL(10,2) | 商品价格 |
| product_sku | VARCHAR(100) | 商品SKU |
| order_status | TINYINT | 订单状态 (1:进行中, 2:完成, 3:失败) |
| order_id | VARCHAR(100) | 订单号 |
| alipay_trade_no | VARCHAR(100) | 支付宝交易号 |
| receiver_name | VARCHAR(100) | 收货人姓名 |
| receiver_address | VARCHAR(500) | 收货地址 |
| receiver_phone | VARCHAR(20) | 收货人手机号 |
| error_message | TEXT | 错误信息 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |
| completed_at | TIMESTAMP | 完成时间 |

## 🔧 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| DATABASE_URL | 数据库连接字符串 | mysql+pymysql://ordertracker:ordertracker123@localhost:3306/ordertracker |

### Docker Compose 配置

- **MySQL**: 端口 3306，数据库名 `ordertracker`
- **API 服务**: 端口 8000
- **phpMyAdmin**: 端口 8080

## 📝 业务规则

1. **下单限制**: 同一用户在同一店铺24小时内只能创建一个下单任务
2. **状态自动判断**: 当提供订单号、支付宝交易号和收货人信息时，自动设置订单状态为完成
3. **时间管理**: 使用UTC时间存储，支持时区转换显示
4. **错误处理**: 完整的错误信息记录和返回

## 🚀 部署指南

### 生产环境部署

1. **修改配置**
```yaml
# docker-compose.yml
environment:
  MYSQL_ROOT_PASSWORD: your_secure_password
  MYSQL_PASSWORD: your_secure_password
```

2. **启动服务**
```bash
docker-compose up -d
```

3. **检查服务状态**
```bash
docker-compose ps
docker-compose logs app
```

### 数据库备份

```bash
# 备份数据库
docker exec ordertracker_mysql mysqldump -u ordertracker -pordertracker123 ordertracker > backup.sql

# 恢复数据库
docker exec -i ordertracker_mysql mysql -u ordertracker -pordertracker123 ordertracker < backup.sql
```

## 🔍 监控和日志

- **应用日志**: `docker-compose logs app`
- **数据库日志**: `docker-compose logs mysql`
- **健康检查**: `curl http://localhost:8000/health`

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 创建 Issue
- 发送邮件至: [iheng13606@gmail.com]

---

⭐ 如果这个项目对你有帮助，请给它一个星标！