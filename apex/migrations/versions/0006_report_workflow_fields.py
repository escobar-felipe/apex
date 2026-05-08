"""report workflow fields

Revision ID: 0006_report_workflow_fields
Revises: 0005_email_audit
Create Date: 2026-05-08 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "0006_report_workflow_fields"
down_revision = "0005_email_audit"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("searchresults", sa.Column("status", sa.String(length=40), nullable=False, server_default="generating"))
    op.add_column("searchresults", sa.Column("report_type", sa.String(length=80), nullable=True, server_default="monitoring"))
    op.add_column("searchresults", sa.Column("audience", sa.String(length=160), nullable=True))
    op.add_column("searchresults", sa.Column("objective", sa.String(length=512), nullable=True))
    op.add_column("searchresults", sa.Column("tone", sa.String(length=80), nullable=True, server_default="executive"))
    op.add_column("searchresults", sa.Column("report_data", sa.JSON(), nullable=True))
    op.add_column("searchresults", sa.Column("report_html", sa.Text(), nullable=True))
    op.add_column("searchresults", sa.Column("reviewed_at", sa.DateTime(), nullable=True))
    op.add_column("searchresults", sa.Column("sent_at", sa.DateTime(), nullable=True))
    op.create_index("ix_searchresults_status_created_at", "searchresults", ["status", "created_at"], unique=False)


def downgrade():
    op.drop_index("ix_searchresults_status_created_at", table_name="searchresults")
    op.drop_column("searchresults", "sent_at")
    op.drop_column("searchresults", "reviewed_at")
    op.drop_column("searchresults", "report_html")
    op.drop_column("searchresults", "report_data")
    op.drop_column("searchresults", "tone")
    op.drop_column("searchresults", "objective")
    op.drop_column("searchresults", "audience")
    op.drop_column("searchresults", "report_type")
    op.drop_column("searchresults", "status")
