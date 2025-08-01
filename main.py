#!/usr/bin/env python3
"""
OrderTracker FastAPI应用
"""

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
import uvicorn
from datetime import datetime, timedelta, timezone
from contextlib import asynccontextmanager

# 导入自定义模块
from src.database import get_db, OrderTask, create_tables
from src.models import (
    ProductRequest, ProductResponse, OrderTaskDetail,
    UpdateOrderInfoRequest, CurrentTaskResponse
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

@app.post("/orders", response_model=ProductResponse)
async def create_order_task(product: ProductRequest, db: Session = Depends(get_db)):
    """
    创建订单任务

    接收商品信息并创建下单任务
    如果同一用户在同一店铺已有下单任务，则返回失败
    不同用户可以在同一店铺下单
    """
    try:
        # 检查用户名和店铺名的组合在24小时内是否已经下过单
        # 计算24小时前的时间点（使用UTC时间确保与数据库时间一致）
        now_utc = datetime.now(timezone.utc)
        twenty_four_hours_ago = now_utc - timedelta(hours=24)

        # 查询该用户在该店铺最近24小时内的下单记录
        recent_task = db.query(OrderTask).filter(
            OrderTask.user_name == product.user_name,
            OrderTask.shop_name == product.shop_name,
            OrderTask.created_at > twenty_four_hours_ago
        ).order_by(OrderTask.created_at.desc()).first()

        if recent_task:
            # 计算距离可以重新下单还需要多长时间
            # 确保时间计算的一致性，将数据库时间转换为UTC进行比较
            if recent_task.created_at.tzinfo is None:
                # 如果数据库时间是naive datetime，假设它是UTC时间
                recent_task_utc = recent_task.created_at.replace(tzinfo=timezone.utc)
            else:
                recent_task_utc = recent_task.created_at.astimezone(timezone.utc)

            time_since_last_order = now_utc - recent_task_utc
            remaining_time = timedelta(hours=24) - time_since_last_order
            remaining_hours = int(remaining_time.total_seconds() // 3600)
            remaining_minutes = int((remaining_time.total_seconds() % 3600) // 60)

            print(f"❌ 用户 '{product.user_name}' 在店铺 '{product.shop_name}' 24小时内已有下单任务")
            # 显示本地时间给用户看
            local_time = recent_task_utc.astimezone()
            print(f"   最近下单时间: {local_time.strftime('%Y-%m-%d %H:%M:%S')} (本地时间)")
            print(f"   还需等待: {remaining_hours}小时{remaining_minutes}分钟")

            return ProductResponse(
                success=False,
                message=f"用户 '{product.user_name}' 在店铺 '{product.shop_name}' 24小时内已有下单任务，还需等待 {remaining_hours}小时{remaining_minutes}分钟后才能重新下单",
                task_uuid=recent_task.task_uuid  # 返回最新订单的UUID
            )

        # 创建新的下单任务
        new_task = OrderTask(
            user_name=product.user_name,
            shop_name=product.shop_name,
            product_url=str(product.product_url),
            product_price=product.product_price,
            product_sku=product.product_sku,
            order_status=1  # 进行中
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


@app.patch("/orders/{task_uuid}", response_model=ProductResponse)
async def update_order_info(task_uuid: str, order_info: UpdateOrderInfoRequest, db: Session = Depends(get_db)):
    """
    更新订单信息

    根据task_uuid更新订单的详细信息，包括订单号、支付宝交易号、收货信息等
    """
    try:
        # 根据task_uuid查询任务
        task = db.query(OrderTask).filter(OrderTask.task_uuid == task_uuid).first()

        if not task:
            print(f"❌ 未找到任务: {task_uuid}")
            return ProductResponse(
                success=False,
                message=f"未找到任务UUID: {task_uuid}"
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
            if order_info.order_status == 2:  # 完成
                task.order_status = 2
                task.completed_at = func.now()
            elif order_info.order_status == 3:  # 失败
                task.order_status = 3
            elif order_info.order_status == 1:  # 进行中
                task.order_status = 1
            updated_fields.append(f"订单状态: {order_info.order_status}")
        else:
            # 用户没有指定状态，根据提供的信息智能判断
            if (order_info.order_id is not None and
                order_info.alipay_trade_no is not None and
                order_info.receiver_name is not None):
                # 如果提供了订单号、支付宝交易号和收货人信息，自动设置为完成
                task.order_status = 2  # 完成
                task.completed_at = func.now()
                updated_fields.append("订单状态: 2 (完成-自动设置)")

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


@app.get("/users/{user_name}/orders/current", response_model=CurrentTaskResponse)
async def get_user_current_order(user_name: str, db: Session = Depends(get_db)):
    """
    获取用户当前进行中的订单

    根据用户名查询当前状态为"进行中"(order_status=1)的订单
    返回订单的完整信息，包括任务ID、UUID、店铺名称、商品链接、价格、SKU等
    """
    try:
        # 查询该用户当前进行中的任务（按创建时间倒序，取最新的一条）
        current_task = db.query(OrderTask).filter(
            OrderTask.user_name == user_name,
            OrderTask.order_status == 1  # 1 = 进行中
        ).order_by(OrderTask.created_at.desc()).first()

        if not current_task:
            print(f"❌ 用户 '{user_name}' 当前没有进行中的任务")
            return CurrentTaskResponse(
                success=False,
                message=f"用户 '{user_name}' 当前没有进行中的任务",
                task=None
            )

        # 转换为响应模型
        task_detail = OrderTaskDetail.model_validate(current_task)

        print(f"✅ 获取用户当前任务成功:")
        print(f"  用户名: {current_task.user_name}")
        print(f"  任务ID: {current_task.id}")
        print(f"  任务UUID: {current_task.task_uuid}")
        print(f"  店铺名称: {current_task.shop_name}")
        print(f"  商品链接: {current_task.product_url}")
        print(f"  商品价格: {current_task.product_price}")
        print(f"  商品SKU: {current_task.product_sku}")

        return CurrentTaskResponse(
            success=True,
            message=f"成功获取用户 '{user_name}' 的当前进行中任务",
            task=task_detail
        )

    except Exception as e:
        print(f"❌ 获取用户当前任务失败: {str(e)}")
        return CurrentTaskResponse(
            success=False,
            message=f"获取用户当前任务失败: {str(e)}",
            task=None
        )


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