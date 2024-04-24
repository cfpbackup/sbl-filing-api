"""alter contact_info phone to phone_number

Revision ID: e1b0d044c840
Revises: 3f7e610035a6
Create Date: 2024-04-24 14:36:55.388541

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e1b0d044c840"
down_revision: Union[str, None] = "3f7e610035a6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("contact_info") as batch_op:
        batch_op.alter_column("phone", nullable=False, new_column_name="phone_number")


def downgrade() -> None:
    with op.batch_alter_table("contact_info") as batch_op:
        batch_op.alter_column("phone_number", nullable=False, new_column_name="phone")
