#!/usr/bin/env python3
"""
Pydantic模型定义
"""

from pydantic import BaseModel, HttpUrl, Field
from typing import Optional
from datetime import datetime
from enum import Enum

# 下单状态枚举
class OrderStatusEnum(int, Enum):
    PROCESSING = 1  # 进行中
    COMPLETED = 2   # 完成
    FAILED = 3      # 失败

# 商品请求模型
class ProductRequest(BaseModel):
    user_name: str = Field(..., min_length=1, max_length=100, description="用户名")
    shop_name: str = Field(..., min_length=1, max_length=200, description="店铺名称")
    product_url: HttpUrl = Field(..., description="商品链接")
    product_price: float = Field(..., gt=0, description="商品价格，必须大于0")
    product_sku: str = Field(..., min_length=1, max_length=100, description="商品SKU")

    class Config:
        schema_extra = {
            "example": {
                "user_name": "张三",
                "shop_name": "测试店铺",
                "product_url": "https://example.com/product/123",
                "product_price": 99.99,
                "product_sku": "SKU123456"
            }
        }

# 商品响应模型
class ProductResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    task_id: Optional[int] = None
    task_uuid: Optional[str] = None

# 下单任务详情模型
class OrderTaskDetail(BaseModel):
    id: int
    task_uuid: str
    user_name: str
    shop_name: str
    product_url: str
    product_price: float
    product_sku: str
    order_status: OrderStatusEnum
    error_message: Optional[str] = None
    order_id: Optional[str] = None
    alipay_trade_no: Optional[str] = None
    receiver_name: Optional[str] = None
    receiver_address: Optional[str] = None
    receiver_phone: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# 下单任务列表响应模型
class OrderTaskListResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    tasks: list[OrderTaskDetail] = []
    total: int = 0

# 更新下单状态请求模型
class UpdateOrderStatusRequest(BaseModel):
    order_status: OrderStatusEnum
    error_message: Optional[str] = None
    order_id: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "order_status": "完成",
                "order_id": "ORDER123456"
            }
        }

# 更新订单信息请求模型
class UpdateOrderInfoRequest(BaseModel):
    task_uuid: str = Field(..., description="任务UUID")
    order_id: Optional[str] = Field(None, description="订单号")
    alipay_trade_no: Optional[str] = Field(None, description="支付宝交易号")
    receiver_name: Optional[str] = Field(None, max_length=100, description="收货人姓名")
    receiver_address: Optional[str] = Field(None, max_length=500, description="收货地址")
    receiver_phone: Optional[str] = Field(None, max_length=20, description="收货人手机号")
    order_status: Optional[OrderStatusEnum] = Field(None, description="订单状态")
    error_message: Optional[str] = Field(None, description="失败原因")

    class Config:
        schema_extra = {
            "example": {
                "task_uuid": "550e8400-e29b-41d4-a716-446655440001",
                "order_id": "2856526176708641363",
                "alipay_trade_no": "2025073122001895161402512358",
                "receiver_name": "王毅恒",
                "receiver_address": "北京 北京市 通州区 市 旭辉御锦4号楼3单元502室 北京市",
                "receiver_phone": "17858286773",
                "order_status": 2
            }
        }

# 下单任务统计模型
class OrderTaskStats(BaseModel):
    processing_count: int = 0
    completed_count: int = 0
    failed_count: int = 0
    total_count: int = 0

# 下单任务统计响应模型
class OrderTaskStatsResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    stats: OrderTaskStats
