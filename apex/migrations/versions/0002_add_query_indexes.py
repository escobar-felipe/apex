"""add query indexes

Revision ID: 0002_add_query_indexes
Revises: 0001_initial_schema
Create Date: 2026-05-04 00:01:00.000000

"""
from alembic import op


revision = "0002_add_query_indexes"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index("ix_user_tenant_admin", "user", ["tenant_id", "admin"], unique=False)
    op.create_index("ix_searchresults_user_created_at", "searchresults", ["user_id", "created_at"], unique=False)
    op.create_index("ix_searchresults_tenant_created_at", "searchresults", ["tenant_id", "created_at"], unique=False)
    op.create_index("ix_searchresults_result_id", "searchresults", ["result_id"], unique=False)


def downgrade():
    op.drop_index("ix_searchresults_result_id", table_name="searchresults")
    op.drop_index("ix_searchresults_tenant_created_at", table_name="searchresults")
    op.drop_index("ix_searchresults_user_created_at", table_name="searchresults")
    op.drop_index("ix_user_tenant_admin", table_name="user")
