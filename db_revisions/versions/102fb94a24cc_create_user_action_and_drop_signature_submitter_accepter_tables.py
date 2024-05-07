"""create user_action table to replace Signatures, Submitter, and Accepter tables

Revision ID: 102fb94a24cc
Revises: 4cd30d188352
Create Date: 2024-04-12 13:33:20.053959

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "102fb94a24cc"
down_revision: Union[str, None] = "4cd30d188352"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

action_type = postgresql.ENUM(
    "SUBMIT",
    "ACCEPT",
    "SIGN",
    name="useractiontype",
    create_type=False,
)


def upgrade() -> None:
    action_type.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "user_action",
        sa.Column("id", sa.INTEGER, autoincrement=True),
        sa.Column("user_id", sa.String, nullable=False),
        sa.Column("user_name", sa.String, nullable=False),
        sa.Column("user_email", sa.String, nullable=False),
        sa.Column(
            "action_type",
            action_type,
        ),
        sa.Column("timestamp", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="user_action_pkey"),
    )

    op.create_table(
        "filing_signature",
        sa.Column("user_action", sa.INTEGER, primary_key=True, unique=True, nullable=False),
        sa.Column("filing", sa.Integer, nullable=False),
        sa.PrimaryKeyConstraint("user_action", name="filing_signatures_pkey"),
        sa.ForeignKeyConstraint(["user_action"], ["user_action.id"], name="filing_signatures_user_action_fkey"),
        sa.ForeignKeyConstraint(["filing"], ["filing.id"], name="filing_signatures_filing_fkey"),
    )

    with op.batch_alter_table("submission", schema=None) as batch_op:
        batch_op.add_column(sa.Column("submitter_id", sa.Integer, nullable=False))
        batch_op.add_column(sa.Column("accepter_id", sa.Integer))
        batch_op.create_foreign_key("submission_submitter_fkey", "user_action", ["submitter_id"], ["id"])
        batch_op.create_foreign_key("submission_accepter_fkey", "user_action", ["accepter_id"], ["id"])

    op.drop_table("accepter")
    op.drop_table("signature")
    op.drop_table("submitter")


def downgrade() -> None:
    op.create_table(
        "submitter",
        sa.Column("id", sa.INTEGER, autoincrement=True),
        sa.Column("submitter", sa.String, nullable=False),
        sa.Column("submitter_name", sa.String, nullable=True),
        sa.Column("submitter_email", sa.String, nullable=False),
        sa.Column("submission", sa.Integer, unique=True),
        sa.PrimaryKeyConstraint("id", name="submitter_pkey"),
        sa.ForeignKeyConstraint(["submission"], ["submission.id"], name="submitter_submission_fkey"),
    )

    op.create_table(
        "signature",
        sa.Column("id", sa.INTEGER, autoincrement=True),
        sa.Column("filing", sa.Integer),
        sa.Column("signer_id", sa.String, nullable=False),
        sa.Column("signer_name", sa.String),
        sa.Column("signer_email", sa.String, nullable=False),
        sa.Column("signed_date", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="signature_pkey"),
        sa.ForeignKeyConstraint(["filing"], ["filing.id"], name="signature_filing_fkey"),
    )

    op.create_table(
        "accepter",
        sa.Column("id", sa.INTEGER, autoincrement=True),
        sa.Column("accepter", sa.String, nullable=False),
        sa.Column("accepter_name", sa.String, nullable=True),
        sa.Column("accepter_email", sa.String, nullable=False),
        sa.Column("submission", sa.Integer, unique=True),
        sa.Column("acception_time", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="accepter_pkey"),
        sa.ForeignKeyConstraint(["submission"], ["submission.id"], name="accepter_submission_fkey"),
    )

    op.drop_constraint(constraint_name="submission_submitter_fkey", table_name="submission")
    op.drop_constraint(constraint_name="submission_accepter_fkey", table_name="submission")
    op.drop_column("submission", "submitter_id")
    op.drop_column("submission", "accepter_id")

    op.drop_table("filing_signature")
    op.drop_table("user_action")
    action_type.drop(op.get_bind(), checkfirst=False)
