-- 初始化测试数据

-- 插入测试账号数据
INSERT INTO accounts (platform_id, account_name, account_id, nickname, daily_purchase_limit, timezone) VALUES 
(1, 'test_1688_001', '1688_user_001', '测试1688账号1', 1, 'Asia/Shanghai'),
(1, 'test_1688_002', '1688_user_002', '测试1688账号2', 2, 'Asia/Shanghai'),
(2, 'test_pdd_001', 'pdd_user_001', '测试拼多多账号1', 1, 'Asia/Shanghai'),
(2, 'test_pdd_002', 'pdd_user_002', '测试拼多多账号2', 1, 'Asia/Shanghai');

-- 插入测试店铺数据
INSERT INTO shops (platform_id, shop_id, shop_name, shop_url) VALUES
(1, '1688_shop_001', '测试1688店铺1', 'https://shop001.1688.com'),
(1, '1688_shop_002', '测试1688店铺2', 'https://shop002.1688.com'),
(2, 'pdd_shop_001', '测试拼多多店铺1', 'https://shop001.pinduoduo.com'),
(2, 'pdd_shop_002', '测试拼多多店铺2', 'https://shop002.pinduoduo.com');

-- 插入测试商品数据
INSERT INTO products (platform_id, shop_id, product_id, product_name, product_url, price, category) VALUES 
(1, 1, '1688_product_001', '测试商品1-1688店铺1', 'https://detail.1688.com/product001', 99.99, '电子产品'),
(1, 1, '1688_product_002', '测试商品2-1688店铺1', 'https://detail.1688.com/product002', 199.99, '服装'),
(1, 2, '1688_product_003', '测试商品3-1688店铺2', 'https://detail.1688.com/product003', 299.99, '家居'),
(2, 3, 'pdd_product_001', '测试商品1-拼多多店铺1', 'https://mobile.pinduoduo.com/product001', 49.99, '食品'),
(2, 3, 'pdd_product_002', '测试商品2-拼多多店铺1', 'https://mobile.pinduoduo.com/product002', 79.99, '美妆'),
(2, 4, 'pdd_product_003', '测试商品3-拼多多店铺2', 'https://mobile.pinduoduo.com/product003', 129.99, '运动');

-- 插入购买限制规则
INSERT INTO purchase_rules (account_id, shop_id, rule_type, limit_count, reset_time) VALUES 
(1, 1, 'daily_shop_limit', 1, '00:00:00'),
(1, 2, 'daily_shop_limit', 1, '00:00:00'),
(2, 1, 'daily_shop_limit', 2, '00:00:00'),
(2, 2, 'daily_shop_limit', 2, '00:00:00'),
(3, 3, 'daily_shop_limit', 1, '00:00:00'),
(3, 4, 'daily_shop_limit', 1, '00:00:00'),
(4, 3, 'daily_shop_limit', 1, '00:00:00'),
(4, 4, 'daily_shop_limit', 1, '00:00:00');
