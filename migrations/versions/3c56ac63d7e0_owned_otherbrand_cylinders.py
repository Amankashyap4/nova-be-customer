"""owned_otherbrand_cylinders

Revision ID: 3c56ac63d7e0
Revises: 3ae9c71cc82c
Create Date: 2023-04-14 12:06:21.384029

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '3c56ac63d7e0'
down_revision = '3ae9c71cc82c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('owned_otherbrand_cylinders', 'customer_id',
               existing_type=postgresql.UUID(),
               nullable=False)
    op.alter_column('owned_otherbrand_cylinders', 'size',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('owned_otherbrand_cylinders', 'type',
               existing_type=sa.VARCHAR(length=60),
               nullable=True)
    op.create_index(op.f('ix_owned_otherbrand_cylinders_customer_id'), 'owned_otherbrand_cylinders', ['customer_id'], unique=False)
    op.create_foreign_key(None, 'owned_otherbrand_cylinders', 'customers', ['customer_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'owned_otherbrand_cylinders', type_='foreignkey')
    op.drop_index(op.f('ix_owned_otherbrand_cylinders_customer_id'), table_name='owned_otherbrand_cylinders')
    op.alter_column('owned_otherbrand_cylinders', 'type',
               existing_type=sa.VARCHAR(length=60),
               nullable=False)
    op.alter_column('owned_otherbrand_cylinders', 'size',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('owned_otherbrand_cylinders', 'customer_id',
               existing_type=postgresql.UUID(),
               nullable=True)
    # ### end Alembic commands ###
