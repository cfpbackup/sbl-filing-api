"""create user_action table to replace Signatures, Submitter, and Accepter tables

Revision ID: 102fb94a24cc
Revises: ccc50ec18a7e
Create Date: 2024-04-12 13:33:20.053959

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "102fb94a24cc"
down_revision: Union[str, None] = "ccc50ec18a7e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user_action",
        sa.Column("id", sa.INTEGER, autoincrement=True),
        sa.Column("user_id", sa.String, nullable=False),
        sa.Column("user_name", sa.String, nullable=False),
        sa.Column("user_email", sa.String, nullable=False),
        sa.Column(
            "action_type",
            sa.Enum(
                "SUBMIT",
                "ACCEPT",
                "SIGN",
                name="useractionstate",
            ),
        ),
        sa.PrimaryKeyConstraint("id", name="user_action_pkey"),
        sa.ForeignKeyConstraint(["filing"], ["filing.id"], name="submission_filing_fkey"),
    )


def downgrade() -> None:
    op.drop_table("user_action")
