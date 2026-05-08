"""email audit

Revision ID: 0005_email_audit
Revises: 0004_search_audit
Create Date: 2026-05-08 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "0005_email_audit"
down_revision = "0004_search_audit"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "email_audit",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("search_result_id", sa.Integer(), nullable=True),
        sa.Column("celery_task_id", sa.String(length=512), nullable=True),
        sa.Column("recipient", sa.String(length=512), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("error_message", sa.String(length=512), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenant.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.ForeignKeyConstraint(["search_result_id"], ["searchresults.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_email_audit_tenant_id", "email_audit", ["tenant_id"], unique=False)
    op.create_index("ix_email_audit_user_id", "email_audit", ["user_id"], unique=False)
    op.create_index("ix_email_audit_search_result_id", "email_audit", ["search_result_id"], unique=False)
    op.create_index("ix_email_audit_celery_task_id", "email_audit", ["celery_task_id"], unique=False)
    op.create_index("ix_email_audit_tenant_created_at", "email_audit", ["tenant_id", "created_at"], unique=False)
    op.create_index("ix_email_audit_user_created_at", "email_audit", ["user_id", "created_at"], unique=False)
    op.create_index("ix_email_audit_search_result_created_at", "email_audit", ["search_result_id", "created_at"], unique=False)


def downgrade():
    op.drop_index("ix_email_audit_search_result_created_at", table_name="email_audit")
    op.drop_index("ix_email_audit_user_created_at", table_name="email_audit")
    op.drop_index("ix_email_audit_tenant_created_at", table_name="email_audit")
    op.drop_index("ix_email_audit_celery_task_id", table_name="email_audit")
    op.drop_index("ix_email_audit_search_result_id", table_name="email_audit")
    op.drop_index("ix_email_audit_user_id", table_name="email_audit")
    op.drop_index("ix_email_audit_tenant_id", table_name="email_audit")
    op.drop_table("email_audit")
