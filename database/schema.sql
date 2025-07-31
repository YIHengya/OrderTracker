-- OrderTracker 数据库设计
-- 商品下单任务管理系统

-- 7. 商品下单任务表（用于保存商品数据和下单进度）
CREATE TABLE order_tasks (
    id INT PRIMARY KEY AUTO_INCREMENT,
    task_uuid VARCHAR(36) NOT NULL UNIQUE COMMENT '任务唯一标识UUID',
    user_name VARCHAR(100) NOT NULL COMMENT '用户名',
    shop_name VARCHAR(200) NOT NULL COMMENT '店铺名称',
    product_url VARCHAR(1000) NOT NULL COMMENT '商品链接',
    product_price DECIMAL(10,2) NOT NULL COMMENT '商品价格',
    product_sku VARCHAR(100) NOT NULL COMMENT '商品SKU',
    order_status ENUM('进行中', '完成', '失败') DEFAULT '进行中' COMMENT '下单进度：进行中、完成、失败',
    error_message TEXT COMMENT '失败原因（当状态为失败时）',
    order_id VARCHAR(100) COMMENT '订单号（当状态为完成时）',
    alipay_trade_no VARCHAR(100) COMMENT '支付宝交易号',
    receiver_name VARCHAR(100) COMMENT '收货人姓名',
    receiver_address VARCHAR(500) COMMENT '收货地址',
    receiver_phone VARCHAR(20) COMMENT '收货人手机号',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    completed_at TIMESTAMP NULL COMMENT '完成时间',
    INDEX idx_order_status (order_status),
    INDEX idx_created_at (created_at),
    INDEX idx_shop_name (shop_name),
    INDEX idx_user_name (user_name),
    INDEX idx_task_uuid (task_uuid)
) COMMENT '商品下单任务表';

-- 创建视图：下单任务统计
CREATE VIEW order_task_stats AS
SELECT
    order_status,
    COUNT(*) as task_count,
    DATE(created_at) as task_date
FROM order_tasks
GROUP BY order_status, DATE(created_at)
ORDER BY task_date DESC, order_status;
