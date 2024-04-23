"""make filing institution_snapshot_id field nullable

Revision ID: 4cd30d188352
Revises: 0040045eae14
Create Date: 2024-04-16 09:33:16.055484

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "4cd30d188352"
down_revision: Union[str, None] = "0040045eae14"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("filing", schema=None) as batch_op:
        batch_op.alter_column("institution_snapshot_id", existing_nullable=False, nullable=True)


def downgrade() -> None:
    with op.batch_alter_table("filing", schema=None) as batch_op:
        batch_op.alter_column("institution_snapshot_id", existing_nullable=True, nullable=False)
