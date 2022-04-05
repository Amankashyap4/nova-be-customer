"""add otp token fields

Revision ID: 51394c606b08
Revises: 27ee3740b5c8
Create Date: 2022-04-04 15:33:19.069912

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "51394c606b08"
down_revision = "27ee3740b5c8"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("registration", sa.Column("otp_token", sa.String(), nullable=True))
    op.add_column(
        "registration",
        sa.Column("otp_token_expiration", sa.DateTime(timezone=True), nullable=True),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("registration", "otp_token_expiration")
    op.drop_column("registration", "otp_token")
    # ### end Alembic commands ###