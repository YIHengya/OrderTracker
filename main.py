#!/usr/bin/env python3
"""
OrderTracker FastAPI应用
"""

from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
import uvicorn
from datetime import datetime
from contextlib import asynccontextmanager

# 导入自定义模块
from src.database import get_db, OrderTask, OrderStatus, create_tables
from src.models import (
    ProductRequest, ProductResponse, OrderTaskDetail,
    OrderTaskListResponse, UpdateOrderStatusRequest, UpdateOrderInfoRequest,
    OrderTaskStats, OrderTaskStatsResponse, OrderStatusEnum
)

# 应用生命周期管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时的初始化操作
    try:
        create_tables()
        print("✅ 数据库表创建/检查完成")
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")

    yield

    # 关闭时的清理操作
    print("🔄 应用正在关闭...")

# 创建FastAPI应用实例
app = FastAPI(
    title="OrderTracker API",
    description="订单跟踪系统API - 商品下单任务管理",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "service": "OrderTracker"}

@app.post("/product", response_model=ProductResponse)
async def create_product(product: ProductRequest, db: Session = Depends(get_db)):
    """
    创建商品下单任务

    接收商品信息并创建下单任务
    """
    try:
        # 创建新的下单任务
        new_task = OrderTask(
            user_name=product.user_name,
            shop_name=product.shop_name,
            product_url=str(product.product_url),
            product_price=product.product_price,
            product_sku=product.product_sku,
            order_status=OrderStatus.PROCESSING
        )

        # 保存到数据库
        db.add(new_task)
        db.commit()
        db.refresh(new_task)

        print(f"✅ 创建下单任务成功:")
        print(f"  任务ID: {new_task.id}")
        print(f"  任务UUID: {new_task.task_uuid}")
        print(f"  用户名: {new_task.user_name}")
        print(f"  店铺名称: {new_task.shop_name}")
        print(f"  商品链接: {new_task.product_url}")
        print(f"  商品价格: {new_task.product_price}")
        print(f"  商品SKU: {new_task.product_sku}")

        return ProductResponse(
            success=True,
            message="商品下单任务创建成功",
            task_id=new_task.id,
            task_uuid=new_task.task_uuid
        )

    except Exception as e:
        db.rollback()
        print(f"❌ 创建下单任务失败: {str(e)}")
        return ProductResponse(success=False, message=f"创建任务失败: {str(e)}")


@app.put("/order/update", response_model=ProductResponse)
async def update_order_info(order_info: UpdateOrderInfoRequest, db: Session = Depends(get_db)):
    """
    更新订单信息

    根据task_uuid查询并更新订单的详细信息，包括订单号、支付宝交易号、收货信息等
    """
    try:
        # 根据task_uuid查询任务
        task = db.query(OrderTask).filter(OrderTask.task_uuid == order_info.task_uuid).first()

        if not task:
            print(f"❌ 未找到任务: {order_info.task_uuid}")
            return ProductResponse(
                success=False,
                message=f"未找到任务UUID: {order_info.task_uuid}"
            )

        # 更新字段（只更新提供的非空字段）
        updated_fields = []

        if order_info.order_id is not None:
            task.order_id = order_info.order_id
            updated_fields.append(f"订单号: {order_info.order_id}")

        if order_info.alipay_trade_no is not None:
            task.alipay_trade_no = order_info.alipay_trade_no
            updated_fields.append(f"支付宝交易号: {order_info.alipay_trade_no}")

        if order_info.receiver_name is not None:
            task.receiver_name = order_info.receiver_name
            updated_fields.append(f"收货人: {order_info.receiver_name}")

        if order_info.receiver_address is not None:
            task.receiver_address = order_info.receiver_address
            updated_fields.append(f"收货地址: {order_info.receiver_address}")

        if order_info.receiver_phone is not None:
            task.receiver_phone = order_info.receiver_phone
            updated_fields.append(f"收货电话: {order_info.receiver_phone}")

        # 智能判断订单状态
        if order_info.order_status is not None:
            # 用户明确指定了状态
            if order_info.order_status == "完成":
                task.order_status = OrderStatus.COMPLETED
                task.completed_at = func.now()
            elif order_info.order_status == "失败":
                task.order_status = OrderStatus.FAILED
            elif order_info.order_status == "进行中":
                task.order_status = OrderStatus.PROCESSING
            updated_fields.append(f"订单状态: {order_info.order_status}")
        else:
            # 用户没有指定状态，根据提供的信息智能判断
            if (order_info.order_id is not None and
                order_info.alipay_trade_no is not None and
                order_info.receiver_name is not None):
                # 如果提供了订单号、支付宝交易号和收货人信息，自动设置为完成
                task.order_status = OrderStatus.COMPLETED
                task.completed_at = func.now()
                updated_fields.append("订单状态: 完成 (自动设置)")

        if order_info.error_message is not None:
            task.error_message = order_info.error_message
            updated_fields.append(f"错误信息: {order_info.error_message}")

        # 保存更改
        db.commit()
        db.refresh(task)

        print(f"✅ 更新订单信息成功:")
        print(f"  任务UUID: {task.task_uuid}")
        for field in updated_fields:
            print(f"  {field}")

        return ProductResponse(
            success=True,
            message=f"订单信息更新成功，共更新 {len(updated_fields)} 个字段",
            task_id=task.id,
            task_uuid=task.task_uuid
        )

    except Exception as e:
        db.rollback()
        print(f"❌ 更新订单信息失败: {str(e)}")
        return ProductResponse(success=False, message=f"更新订单信息失败: {str(e)}")


if __name__ == "__main__":
    print("🚀 启动OrderTracker API服务...")
    print("📖 API文档地址: http://localhost:8000/docs")
    print("🔍 交互式文档: http://localhost:8000/redoc")
    print("❤️  健康检查: http://localhost:8000/health")
    print("=" * 50)

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )