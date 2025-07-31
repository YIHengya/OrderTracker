"""add_timezone_support_to_timestamp_fields

Revision ID: c5e50f614f22
Revises: bae2446b3ee3
Create Date: 2025-07-31 20:14:28.799889

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c5e50f614f22'
down_revision: Union[str, Sequence[str], None] = 'bae2446b3ee3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema to add timezone support to timestamp fields."""
    # 注意：MySQL的TIMESTAMP字段默认就支持时区，但为了确保一致性
    # 我们可以明确指定时区支持
    # 在MySQL中，TIMESTAMP字段会自动转换为UTC存储

    # 由于MySQL的TIMESTAMP已经支持时区转换，这里主要是确保
    # 应用层正确处理时区问题，数据库层面不需要修改
    pass


def downgrade() -> None:
    """Downgrade schema."""
    # 由于没有实际的数据库结构变更，downgrade也不需要操作
    pass
