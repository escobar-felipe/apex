"""expand encrypted credentials

Revision ID: 0003_encrypt_creds
Revises: 0002_add_query_indexes
Create Date: 2026-05-08 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "0003_encrypt_creds"
down_revision = "0002_add_query_indexes"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("user") as batch_op:
        batch_op.alter_column("api_key", existing_type=sa.String(length=512), type_=sa.String(length=2048))
        batch_op.alter_column("serpapi_key", existing_type=sa.String(length=512), type_=sa.String(length=2048))
        batch_op.alter_column("stmp_password", existing_type=sa.String(length=512), type_=sa.String(length=2048))


def downgrade():
    with op.batch_alter_table("user") as batch_op:
        batch_op.alter_column("api_key", existing_type=sa.String(length=2048), type_=sa.String(length=512))
        batch_op.alter_column("serpapi_key", existing_type=sa.String(length=2048), type_=sa.String(length=512))
        batch_op.alter_column("stmp_password", existing_type=sa.String(length=2048), type_=sa.String(length=512))
