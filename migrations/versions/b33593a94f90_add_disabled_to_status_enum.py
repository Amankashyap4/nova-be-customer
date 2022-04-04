"""add disabled to status enum

Revision ID: b33593a94f90
Revises: 9418af9c22e3
Create Date: 2022-04-01 16:00:27.655484

"""
# import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "b33593a94f90"
down_revision = "9418af9c22e3"
branch_labels = None
depends_on = None


def upgrade():
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE status ADD VALUE 'disabled'")


def downgrade():
    op.execute("ALTER TYPE status RENAME TO status_old")
    op.execute(
        "CREATE TYPE status AS ENUM('active', 'inactive', 'blocked', 'first_time', 'disabled')"
    )
    op.execute(
        (
            "ALTER TABLE customers ALTER COLUMN status TYPE status USING "
            "status::text::status"
        )
    )
    op.execute("DROP TYPE status_old")
