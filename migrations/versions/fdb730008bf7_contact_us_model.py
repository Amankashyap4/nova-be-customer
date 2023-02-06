"""contact_us_model

Revision ID: fdb730008bf7
Revises: c3b4fa25b3ee
Create Date: 2023-01-12 13:17:10.275812

"""
import sqlalchemy as sa
from alembic import op

import app

# revision identifiers, used by Alembic.
revision = "fdb730008bf7"
# down_revision = "c3b4fa25b3ee"
down_revision = "f94aced3034f"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "contact_us",
        sa.Column("id", app.utils.guid.GUID(), nullable=False),
        sa.Column("name", sa.String(length=60), nullable=True),
        sa.Column("email", sa.String(length=60), nullable=True),
        sa.Column("subject", sa.String(), nullable=True),
        sa.Column("compose_email", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("contact_us")
    # ### end Alembic commands ###
