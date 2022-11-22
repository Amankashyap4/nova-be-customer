"""modify_customers_history

Revision ID: 4a76cad0d5db
Revises: 0a45ec67be6d
Create Date: 2022-08-10 12:35:19.564363

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "4a76cad0d5db"
down_revision = "0a45ec67be6d"
branch_labels = None
depends_on = None

create_trigger = """
    CREATE OR REPLACE TRIGGER customer_history_ AFTER INSERT OR UPDATE OF phone_number,
    email ON customers
    FOR EACH ROW EXECUTE PROCEDURE customer_history();
"""
trigger_function = """
 CREATE OR REPLACE FUNCTION customer_history() RETURNS TRIGGER AS $customer_history$
    BEGIN
        IF (TG_OP = 'INSERT') THEN
            INSERT INTO customers_history (id, customer_id, phone_number, email, action,
            status, valid_from) VALUES(gen_random_uuid(), NEW.id, NEW.phone_number,
            NEW.email, 'insert', 'active', NEW.created);
        ELSIF (TG_OP = 'UPDATE') THEN
            UPDATE customers_history SET valid_to = NEW.modified, status ='inactive'
             where id IN (SELECT id FROM customers_history WHERE customer_id = NEW.id
             ORDER BY created DESC LIMIT 1);
            INSERT INTO customers_history (id, customer_id, phone_number, email, action,
            status, valid_from) VALUES(gen_random_uuid(), NEW.id, NEW.phone_number,
            NEW.email, 'update', 'active', NEW.modified);
        END IF;
        RETURN NEW;
    END;
$customer_history$ LANGUAGE plpgsql;
"""
drop_function = """
    DROP FUNCTION customer_history CASCADE
"""


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("customers_history", sa.Column("status", sa.String(), nullable=False))
    op.add_column(
        "customers_history",
        sa.Column(
            "created",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.alter_column(
        "customers_history", "phone_number", existing_type=sa.VARCHAR(), nullable=False
    )
    op.alter_column(
        "customers_history",
        "action",
        existing_type=sa.VARCHAR(length=60),
        nullable=False,
    )
    op.alter_column(
        "customers_history",
        "valid_to",
        existing_type=postgresql.TIMESTAMP(timezone=True),
        nullable=True,
    )
    op.execute("ALTER TABLE customers_history ALTER COLUMN valid_to DROP DEFAULT")
    # op.execute(trigger_function)
    # op.execute(create_trigger)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "customers_history",
        "valid_to",
        existing_type=postgresql.TIMESTAMP(timezone=True),
        nullable=True,
        existing_server_default=sa.text("now()"),
    )
    op.alter_column(
        "customers_history", "action", existing_type=sa.VARCHAR(length=60), nullable=True
    )
    op.alter_column(
        "customers_history", "phone_number", existing_type=sa.VARCHAR(), nullable=True
    )
    op.drop_column("customers_history", "created")
    op.drop_column("customers_history", "status")
    # op.execute(drop_function)
    # op.execute("TRUNCATE customers CASCADE;")
    # ### end Alembic commands ###
