-- OrderTracker 初始化测试数据
-- 只包含 order_tasks 表的测试数据

-- 插入测试下单任务数据
INSERT INTO order_tasks (task_uuid, user_name, shop_name, product_url, product_price, product_sku, order_status, error_message, order_id, completed_at) VALUES
('550e8400-e29b-41d4-a716-446655440001', '测试用户1', '测试店铺1', 'https://example.com/product1', 99.99, 'TEST-SKU-001', '完成', NULL, 'ORDER-001', '2025-07-31 10:00:00'),
('550e8400-e29b-41d4-a716-446655440002', '测试用户2', '测试店铺2', 'https://example.com/product2', 199.99, 'TEST-SKU-002', '进行中', NULL, NULL, NULL),
('550e8400-e29b-41d4-a716-446655440003', '测试用户3', '测试店铺3', 'https://example.com/product3', 299.99, 'TEST-SKU-003', '失败', '库存不足', NULL, NULL);
