"""create filing period table

Revision ID: 5a775dd75356
Revises:
Create Date: 2024-01-08 13:49:42.475381

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "5a775dd75356"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

filing_type = postgresql.ENUM("ANNUAL", name="filingtype", create_type=False)


def upgrade() -> None:
    filing_type.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "filing_period",
        sa.Column("code", sa.String, nullable=False),
        sa.Column("description", sa.String, nullable=False),
        sa.Column("start_period", sa.DateTime, nullable=False),
        sa.Column("end_period", sa.DateTime, nullable=False),
        sa.Column("due", sa.DateTime, nullable=False),
        sa.Column("filing_type", filing_type, server_default="ANNUAL"),
        sa.PrimaryKeyConstraint("code", name="filing_period_pkey"),
    )


def downgrade() -> None:
    op.drop_table("filing_period")

    filing_type.drop(op.get_bind(), checkfirst=False)
