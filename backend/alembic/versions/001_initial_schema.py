"""Initial schema creation

Revision ID: 001
Revises:
Create Date: 2026-07-13

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "hcps",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("specialty", sa.String(length=255), nullable=True),
        sa.Column("organization", sa.String(length=255), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_hcps_name"), "hcps", ["name"], unique=False)

    op.create_table(
        "interactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("hcp_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", sa.String(length=255), nullable=False),
        sa.Column(
            "interaction_type",
            postgresql.ENUM(
                "meeting", "call", "email", "conference", "sample_drop", name="interactiontype"
            ),
            nullable=False,
        ),
        sa.Column(
            "channel",
            postgresql.ENUM("in_person", "phone", "video", "email", name="channel"),
            nullable=False,
        ),
        sa.Column("interaction_date", sa.DateTime(), nullable=False),
        sa.Column("subject", sa.String(length=500), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "sentiment",
            postgresql.ENUM("positive", "neutral", "negative", name="sentiment"),
            nullable=True,
        ),
        sa.Column("products", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("follow_up_actions", postgresql.JSON(), nullable=True),
        sa.Column("ai_summary", sa.Text(), nullable=True),
        sa.Column(
            "source",
            postgresql.ENUM("form", "ai_assistant", name="source"),
            nullable=False,
        ),
        sa.Column(
            "status", postgresql.ENUM("draft", "logged", name="status"), nullable=False
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["hcp_id"],
            ["hcps.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_interactions_hcp_id"), "interactions", ["hcp_id"], unique=False)
    op.create_index(
        op.f("ix_interactions_interaction_date"),
        "interactions",
        ["interaction_date"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_interactions_interaction_date"), table_name="interactions")
    op.drop_index(op.f("ix_interactions_hcp_id"), table_name="interactions")
    op.drop_table("interactions")
    op.drop_index(op.f("ix_hcps_name"), table_name="hcps")
    op.drop_table("hcps")
