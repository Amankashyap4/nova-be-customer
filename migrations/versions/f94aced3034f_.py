"""empty message

Revision ID: f94aced3034f
Revises: 5551ef8f34a9
Create Date: 2023-01-09 18:17:32.037423

"""
from alembic import op
import sqlalchemy as sa
import app


# revision identifiers, used by Alembic.
revision = 'f94aced3034f'
down_revision = '5551ef8f34a9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('promotion',
    sa.Column('id', app.utils.guid.GUID(), nullable=False),
    sa.Column('tittle', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('image', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('safety',
    sa.Column('id', app.utils.guid.GUID(), nullable=False),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('image', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('safety')
    op.drop_table('promotion')
    # ### end Alembic commands ###