#!/usr/bin/env python3
"""
数据库配置和模型定义
"""

from sqlalchemy import create_engine, Column, Integer, String, DECIMAL, TIMESTAMP, TEXT, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
import enum
from typing import Optional
import os
import uuid
from datetime import timezone

# 数据库配置
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "mysql+pymysql://ordertracker:ordertracker123@localhost:3306/ordertracker"
)

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL,
    echo=True,  # 开发环境下显示SQL语句
    pool_pre_ping=True,  # 连接池预检查
    pool_recycle=3600,   # 连接回收时间
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基础模型类
Base = declarative_base()

# 定义下单状态枚举
class OrderStatus(enum.Enum):
    PROCESSING = 1  # 进行中
    COMPLETED = 2   # 完成
    FAILED = 3      # 失败

# 商品下单任务模型
class OrderTask(Base):
    __tablename__ = "order_tasks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    task_uuid = Column(String(36), nullable=False, unique=True, comment="任务唯一标识UUID")
    user_name = Column(String(100), nullable=False, comment="用户名")
    shop_name = Column(String(200), nullable=False, comment="店铺名称")
    product_url = Column(String(1000), nullable=False, comment="商品链接")
    product_price = Column(DECIMAL(10, 2), nullable=False, comment="商品价格")
    product_sku = Column(String(100), nullable=False, comment="商品SKU")
    order_status = Column(
        Integer,
        default=1,  # 1-进行中
        comment="下单进度：1-进行中、2-完成、3-失败"
    )
    error_message = Column(TEXT, nullable=True, comment="失败原因（当状态为失败时）")
    order_id = Column(String(100), nullable=True, comment="订单号（当状态为完成时）")
    alipay_trade_no = Column(String(100), nullable=True, comment="支付宝交易号")
    receiver_name = Column(String(100), nullable=True, comment="收货人姓名")
    receiver_address = Column(String(500), nullable=True, comment="收货地址")
    receiver_phone = Column(String(20), nullable=True, comment="收货人手机号")
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间"
    )
    completed_at = Column(TIMESTAMP(timezone=True), nullable=True, comment="完成时间")

    def __init__(self, **kwargs):
        """初始化时自动生成UUID"""
        if 'task_uuid' not in kwargs:
            kwargs['task_uuid'] = str(uuid.uuid4())
        super().__init__(**kwargs)

# 数据库依赖函数
def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 创建所有表
def create_tables():
    """创建数据库表"""
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    # 测试数据库连接
    try:
        create_tables()
        print("✅ 数据库连接成功，表创建完成")
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
