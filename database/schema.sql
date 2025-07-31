-- 商品购买记录管理系统数据库设计
-- 支持多平台、多账号的商品购买限制管理

-- 1. 电商平台表
CREATE TABLE platforms (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE COMMENT '平台名称，如：1688、拼多多、淘宝等',
    code VARCHAR(20) NOT NULL UNIQUE COMMENT '平台代码，如：1688、pdd、taobao',
    base_url VARCHAR(255) COMMENT '平台基础URL',
    status TINYINT DEFAULT 1 COMMENT '状态：1-启用，0-禁用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) COMMENT '电商平台表';

-- 2. 账号表
CREATE TABLE accounts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    platform_id INT NOT NULL,
    account_name VARCHAR(100) NOT NULL COMMENT '账号名称/用户名',
    account_id VARCHAR(100) COMMENT '平台账号ID',
    nickname VARCHAR(100) COMMENT '账号昵称',
    status TINYINT DEFAULT 1 COMMENT '状态：1-正常，0-禁用',
    daily_purchase_limit INT DEFAULT 1 COMMENT '每日购买限制次数',
    timezone VARCHAR(50) DEFAULT 'Asia/Shanghai' COMMENT '时区设置',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (platform_id) REFERENCES platforms(id),
    UNIQUE KEY uk_platform_account (platform_id, account_name)
) COMMENT '账号表';

-- 3. 店铺表
CREATE TABLE shops (
    id INT PRIMARY KEY AUTO_INCREMENT,
    platform_id INT NOT NULL,
    shop_id VARCHAR(100) NOT NULL COMMENT '店铺在平台的唯一标识',
    shop_name VARCHAR(200) NOT NULL COMMENT '店铺名称',
    shop_url VARCHAR(500) COMMENT '店铺链接',
    status TINYINT DEFAULT 1 COMMENT '状态：1-正常，0-禁用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (platform_id) REFERENCES platforms(id),
    UNIQUE KEY uk_platform_shop (platform_id, shop_id)
) COMMENT '店铺表';

-- 4. 商品表
CREATE TABLE products (
    id INT PRIMARY KEY AUTO_INCREMENT,
    platform_id INT NOT NULL,
    shop_id INT NOT NULL,
    product_id VARCHAR(100) NOT NULL COMMENT '商品在平台的唯一标识',
    product_name VARCHAR(500) NOT NULL COMMENT '商品名称',
    product_url VARCHAR(1000) COMMENT '商品链接',
    price DECIMAL(10,2) COMMENT '商品价格',
    category VARCHAR(100) COMMENT '商品分类',
    status TINYINT DEFAULT 1 COMMENT '状态：1-正常，0-下架',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (platform_id) REFERENCES platforms(id),
    FOREIGN KEY (shop_id) REFERENCES shops(id),
    UNIQUE KEY uk_platform_product (platform_id, product_id)
) COMMENT '商品表';

-- 5. 购买记录表
CREATE TABLE purchase_records (
    id INT PRIMARY KEY AUTO_INCREMENT,
    account_id INT NOT NULL,
    shop_id INT NOT NULL,
    product_id INT NOT NULL,
    purchase_date DATE NOT NULL COMMENT '购买日期（基于账号时区）',
    purchase_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '购买时间（UTC）',
    order_id VARCHAR(100) COMMENT '订单号',
    amount DECIMAL(10,2) COMMENT '购买金额',
    quantity INT DEFAULT 1 COMMENT '购买数量',
    status TINYINT DEFAULT 1 COMMENT '状态：1-成功，0-失败，2-取消',
    remark TEXT COMMENT '备注信息',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES accounts(id),
    FOREIGN KEY (shop_id) REFERENCES shops(id),
    FOREIGN KEY (product_id) REFERENCES products(id),
    INDEX idx_account_shop_date (account_id, shop_id, purchase_date),
    INDEX idx_purchase_date (purchase_date),
    INDEX idx_purchase_time (purchase_time)
) COMMENT '购买记录表';

-- 6. 购买限制规则表（可扩展的规则配置）
CREATE TABLE purchase_rules (
    id INT PRIMARY KEY AUTO_INCREMENT,
    account_id INT,
    platform_id INT,
    shop_id INT,
    rule_type ENUM('daily_shop_limit', 'daily_platform_limit', 'daily_account_limit') NOT NULL,
    limit_count INT NOT NULL DEFAULT 1 COMMENT '限制次数',
    reset_time TIME DEFAULT '00:00:00' COMMENT '重置时间（基于账号时区）',
    status TINYINT DEFAULT 1 COMMENT '状态：1-启用，0-禁用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES accounts(id),
    FOREIGN KEY (platform_id) REFERENCES platforms(id),
    FOREIGN KEY (shop_id) REFERENCES shops(id)
) COMMENT '购买限制规则表';

-- 插入初始数据
INSERT INTO platforms (name, code, base_url) VALUES 
('1688', '1688', 'https://www.1688.com'),
('拼多多', 'pdd', 'https://www.pinduoduo.com'),
('淘宝', 'taobao', 'https://www.taobao.com'),
('天猫', 'tmall', 'https://www.tmall.com');

-- 创建视图：今日购买统计
CREATE VIEW daily_purchase_stats AS
SELECT 
    a.id as account_id,
    a.account_name,
    p.name as platform_name,
    s.shop_name,
    DATE(CONVERT_TZ(pr.purchase_time, '+00:00', a.timezone)) as purchase_date,
    COUNT(*) as purchase_count,
    SUM(pr.amount) as total_amount
FROM purchase_records pr
JOIN accounts a ON pr.account_id = a.id
JOIN platforms p ON a.platform_id = p.id
JOIN shops s ON pr.shop_id = s.id
WHERE pr.status = 1
GROUP BY a.id, s.id, DATE(CONVERT_TZ(pr.purchase_time, '+00:00', a.timezone));
