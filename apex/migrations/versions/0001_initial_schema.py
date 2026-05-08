"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-05-04 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "tenant",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("slug", sa.String(length=80), nullable=False),
        sa.Column("domain", sa.String(length=255), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("domain"),
    )
    op.create_index(op.f("ix_tenant_slug"), "tenant", ["slug"], unique=True)

    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=True),
        sa.Column("username", sa.String(length=80), nullable=False),
        sa.Column("password", sa.String(length=512), nullable=True),
        sa.Column("api_key", sa.String(length=2048), nullable=True),
        sa.Column("serpapi_key", sa.String(length=2048), nullable=True),
        sa.Column("email", sa.String(length=512), nullable=True),
        sa.Column("stmp_password", sa.String(length=2048), nullable=True),
        sa.Column("admin", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenant.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "username", name="uq_user_tenant_username"),
    )
    op.create_index(op.f("ix_user_tenant_id"), "user", ["tenant_id"], unique=False)

    op.create_table(
        "searchresults",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(length=512), nullable=True),
        sa.Column("result_id", sa.String(length=512), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenant.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_searchresults_tenant_id"), "searchresults", ["tenant_id"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_searchresults_tenant_id"), table_name="searchresults")
    op.drop_table("searchresults")
    op.drop_index(op.f("ix_user_tenant_id"), table_name="user")
    op.drop_table("user")
    op.drop_index(op.f("ix_tenant_slug"), table_name="tenant")
    op.drop_table("tenant")
