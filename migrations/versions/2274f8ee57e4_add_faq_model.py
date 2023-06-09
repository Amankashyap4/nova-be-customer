"""add_faq_model

Revision ID: 2274f8ee57e4
Revises: fdb730008bf7
Create Date: 2023-01-19 12:24:24.132176

"""
import sqlalchemy as sa
from alembic import op

import app

# revision identifiers, used by Alembic.
revision = "2274f8ee57e4"
down_revision = "fdb730008bf7"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "faq",
        sa.Column("id", app.utils.guid.GUID(), nullable=False),
        sa.Column("question", sa.String(), nullable=True),
        sa.Column("answer", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("faq")
    # ### end Alembic commands ###
