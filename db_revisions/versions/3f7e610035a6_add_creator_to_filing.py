"""add creator to filing

Revision ID: 3f7e610035a6
Revises: 102fb94a24cc
Create Date: 2024-04-22 13:03:16.328778

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "3f7e610035a6"
down_revision: Union[str, None] = "102fb94a24cc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("filing", schema=None) as batch_op:
        batch_op.add_column(sa.Column("creator_id", sa.Integer, nullable=False))
        batch_op.create_foreign_key("filing_creator_fkey", "user_action", ["creator_id"], ["id"])


def downgrade() -> None:
    pass
