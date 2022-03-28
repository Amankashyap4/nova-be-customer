"""empty message

Revision ID: 2fb2c8f4b629
Revises: e1eddb03d6c4
Create Date: 2021-12-08 22:08:38.036093

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2fb2c8f4b629"
down_revision = "e1eddb03d6c4"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "customer", sa.Column("new_phone_number", sa.String(length=60), nullable=True)
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("customer", "new_phone_number")
    # ### end Alembic commands ###
