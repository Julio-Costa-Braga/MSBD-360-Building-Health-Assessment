"""add sub_location to measurements

Revision ID: a1b2c3d4e5f6
Revises: 51dba621fe7d
Create Date: 2026-07-10

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "51dba621fe7d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("measurements", sa.Column("sub_location", sa.String(50), nullable=True))


def downgrade() -> None:
    op.drop_column("measurements", "sub_location")
