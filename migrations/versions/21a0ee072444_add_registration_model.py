"""add registration model

Revision ID: 21a0ee072444
Revises: 217b92a9c173
Create Date: 2022-04-04 15:23:04.520839

"""
import sqlalchemy as sa
from alembic import op

import app

# revision identifiers, used by Alembic.
revision = "21a0ee072444"
down_revision = "217b92a9c173"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "registration",
        sa.Column("id", app.utils.guid.GUID(), nullable=False),
        sa.Column("phone_number", sa.String(), nullable=False),
        sa.Column(
            "created",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "modified",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("phone_number"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("registration")
    # ### end Alembic commands ###
