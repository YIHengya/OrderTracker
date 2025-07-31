# 商品购买记录管理系统 - 数据库设计

## 概述
这是一个支持多平台、多账号的商品购买限制管理系统的数据库设计。系统支持1688、拼多多等电商平台，可以管理不同账号的每日购买限制，并提供时区感知的重置逻辑。

## 核心功能
- 多平台支持（1688、拼多多、淘宝、天猫等）
- 多账号管理
- 店铺级别的购买限制
- 时区感知的每日重置逻辑
- 灵活的购买规则配置

## 数据库表结构

### 1. platforms (电商平台表)
存储支持的电商平台信息
- `id`: 主键
- `name`: 平台名称（如：1688、拼多多）
- `code`: 平台代码（如：1688、pdd）
- `base_url`: 平台基础URL
- `status`: 状态（1-启用，0-禁用）

### 2. accounts (账号表)
存储用户在各平台的账号信息
- `id`: 主键
- `platform_id`: 关联平台ID
- `account_name`: 账号名称/用户名
- `account_id`: 平台账号ID
- `nickname`: 账号昵称
- `daily_purchase_limit`: 每日购买限制次数
- `timezone`: 时区设置（默认：Asia/Shanghai）
- `status`: 状态（1-正常，0-禁用）

### 3. shops (店铺表)
存储商品所属的店铺信息
- `id`: 主键
- `platform_id`: 关联平台ID
- `shop_id`: 店铺在平台的唯一标识
- `shop_name`: 店铺名称
- `shop_url`: 店铺链接
- `status`: 状态（1-正常，0-禁用）

### 4. products (商品表)
存储商品基本信息
- `id`: 主键
- `platform_id`: 关联平台ID
- `shop_id`: 关联店铺ID
- `product_id`: 商品在平台的唯一标识
- `product_name`: 商品名称
- `product_url`: 商品链接
- `price`: 商品价格
- `category`: 商品分类
- `status`: 状态（1-正常，0-下架）

### 5. purchase_records (购买记录表)
存储购买记录，支持时区感知
- `id`: 主键
- `account_id`: 关联账号ID
- `shop_id`: 关联店铺ID
- `product_id`: 关联商品ID
- `purchase_date`: 购买日期（基于账号时区）
- `purchase_time`: 购买时间（UTC）
- `order_id`: 订单号
- `amount`: 购买金额
- `quantity`: 购买数量
- `status`: 状态（1-成功，0-失败，2-取消）
- `remark`: 备注信息

### 6. purchase_rules (购买限制规则表)
可扩展的购买规则配置
- `id`: 主键
- `account_id`: 关联账号ID（可选）
- `platform_id`: 关联平台ID（可选）
- `shop_id`: 关联店铺ID（可选）
- `rule_type`: 规则类型（daily_shop_limit、daily_platform_limit、daily_account_limit）
- `limit_count`: 限制次数
- `reset_time`: 重置时间（基于账号时区）
- `status`: 状态（1-启用，0-禁用）

## 核心查询逻辑

### 检查今日是否已购买某店铺商品
```sql
-- 检查指定账号今日是否已在某店铺购买过商品
SELECT COUNT(*) as purchase_count
FROM purchase_records pr
JOIN accounts a ON pr.account_id = a.id
WHERE pr.account_id = ? 
  AND pr.shop_id = ?
  AND DATE(CONVERT_TZ(pr.purchase_time, '+00:00', a.timezone)) = CURDATE()
  AND pr.status = 1;
```

### 获取今日购买统计
使用 `daily_purchase_stats` 视图可以快速获取各账号的今日购买统计。

## 时区处理
- 所有时间戳以UTC格式存储在数据库中
- 每个账号可以设置独立的时区
- 购买日期基于账号时区计算
- 支持不同时区的每日重置逻辑

## 扩展性
- 支持添加新的电商平台
- 支持灵活的购买限制规则
- 支持多种规则类型（店铺级、平台级、账号级）
- 支持自定义重置时间
