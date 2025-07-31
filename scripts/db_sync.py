#!/usr/bin/env python3
"""
数据库同步脚本
用于自动检测模型变更并同步到数据库
"""

import os
import sys
import subprocess
import argparse
from datetime import datetime

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

def run_command(cmd, cwd=None):
    """执行命令并返回结果"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            cwd=cwd or project_root,
            capture_output=True, 
            text=True, 
            encoding='utf-8'
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_alembic_setup():
    """检查 Alembic 是否已设置"""
    alembic_dir = os.path.join(project_root, "alembic")
    alembic_ini = os.path.join(project_root, "alembic.ini")
    
    if not os.path.exists(alembic_dir) or not os.path.exists(alembic_ini):
        print("❌ Alembic 未初始化，请先运行: alembic init alembic")
        return False
    return True

def generate_migration(message=None):
    """生成迁移文件"""
    if not message:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        message = f"Auto migration {timestamp}"
    
    print(f"🔍 检测模型变更并生成迁移: {message}")
    
    cmd = f'alembic revision --autogenerate -m "{message}"'
    success, stdout, stderr = run_command(cmd)
    
    if success:
        print("✅ 迁移文件生成成功")
        print(stdout)
        return True
    else:
        print("❌ 迁移文件生成失败")
        print(stderr)
        return False

def apply_migration():
    """应用迁移到数据库"""
    print("🚀 应用迁移到数据库...")
    
    cmd = "alembic upgrade head"
    success, stdout, stderr = run_command(cmd)
    
    if success:
        print("✅ 数据库迁移成功")
        print(stdout)
        return True
    else:
        print("❌ 数据库迁移失败")
        print(stderr)
        return False

def show_migration_status():
    """显示迁移状态"""
    print("📊 当前迁移状态:")
    
    cmd = "alembic current"
    success, stdout, stderr = run_command(cmd)
    
    if success:
        print(f"当前版本: {stdout.strip()}")
    else:
        print("无法获取当前版本")
    
    cmd = "alembic history"
    success, stdout, stderr = run_command(cmd)
    
    if success:
        print("\n迁移历史:")
        print(stdout)

def rollback_migration(steps=1):
    """回滚迁移"""
    print(f"⏪ 回滚 {steps} 个迁移...")
    
    if steps == 1:
        cmd = "alembic downgrade -1"
    else:
        cmd = f"alembic downgrade -{steps}"
    
    success, stdout, stderr = run_command(cmd)
    
    if success:
        print("✅ 回滚成功")
        print(stdout)
        return True
    else:
        print("❌ 回滚失败")
        print(stderr)
        return False

def merge_changes(message=None):
    """一键合并：生成迁移 + 应用到数据库"""
    print("🔄 开始一键合并本地模型变更到数据库...")
    
    # 1. 检查 Alembic 设置
    if not check_alembic_setup():
        return False
    
    # 2. 生成迁移
    if not generate_migration(message):
        return False
    
    # 3. 应用迁移
    if not apply_migration():
        return False
    
    print("🎉 数据库同步完成！")
    return True

def main():
    parser = argparse.ArgumentParser(description="数据库同步工具")
    parser.add_argument("action", choices=["merge", "generate", "apply", "status", "rollback"], 
                       help="操作类型")
    parser.add_argument("-m", "--message", help="迁移消息")
    parser.add_argument("-s", "--steps", type=int, default=1, help="回滚步数")
    
    args = parser.parse_args()
    
    if args.action == "merge":
        merge_changes(args.message)
    elif args.action == "generate":
        generate_migration(args.message)
    elif args.action == "apply":
        apply_migration()
    elif args.action == "status":
        show_migration_status()
    elif args.action == "rollback":
        rollback_migration(args.steps)

if __name__ == "__main__":
    main()
