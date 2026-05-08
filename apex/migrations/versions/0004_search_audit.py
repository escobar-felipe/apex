"""search audit

Revision ID: 0004_search_audit
Revises: 0003_encrypt_creds
Create Date: 2026-05-08 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "0004_search_audit"
down_revision = "0003_encrypt_creds"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "search_audit",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("query", sa.String(length=512), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("provider", sa.String(length=80), nullable=True),
        sa.Column("result_counts", sa.JSON(), nullable=True),
        sa.Column("error_message", sa.String(length=512), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenant.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_search_audit_tenant_id", "search_audit", ["tenant_id"], unique=False)
    op.create_index("ix_search_audit_user_id", "search_audit", ["user_id"], unique=False)
    op.create_index("ix_search_audit_tenant_created_at", "search_audit", ["tenant_id", "created_at"], unique=False)
    op.create_index("ix_search_audit_user_created_at", "search_audit", ["user_id", "created_at"], unique=False)


def downgrade():
    op.drop_index("ix_search_audit_user_created_at", table_name="search_audit")
    op.drop_index("ix_search_audit_tenant_created_at", table_name="search_audit")
    op.drop_index("ix_search_audit_user_id", table_name="search_audit")
    op.drop_index("ix_search_audit_tenant_id", table_name="search_audit")
    op.drop_table("search_audit")
