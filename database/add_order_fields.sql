-- 添加订单相关字段到 order_tasks 表
-- 执行此脚本来更新现有数据库结构

-- 添加新字段
ALTER TABLE order_tasks 
ADD COLUMN alipay_trade_no VARCHAR(100) COMMENT '支付宝交易号',
ADD COLUMN receiver_name VARCHAR(100) COMMENT '收货人姓名',
ADD COLUMN receiver_address VARCHAR(500) COMMENT '收货地址',
ADD COLUMN receiver_phone VARCHAR(20) COMMENT '收货人手机号';

-- 验证字段添加成功
DESCRIBE order_tasks;
