from alembic import op
import sqlalchemy as sa

# Revision identifiers, used by Alembic.
revision = 'a7816612b704'
down_revision = None  # Set this to the last successful migration ID
branch_labels = None
depends_on = None


def upgrade():
    # Rename column in users table
    with op.batch_alter_table('users') as batch_op:
        batch_op.alter_column('users', 'id', new_column_name='user_id', existing_type=sa.Integer)


    # Update foreign keys in related tables
    with op.batch_alter_table('cart') as batch_op:
        batch_op.drop_constraint('fk_cart_user', type_='foreignkey')  # Use actual constraint name
        batch_op.create_foreign_key('fk_cart_user', 'users', ['user_id'], ['user_id'], ondelete='CASCADE')

    with op.batch_alter_table('clients') as batch_op:
        batch_op.drop_constraint('clients_ibfk_1', type_='foreignkey')
        batch_op.create_foreign_key('clients_ibfk_1', 'users', ['user_id'], ['user_id'], ondelete='CASCADE')

    with op.batch_alter_table('orders') as batch_op:
        batch_op.drop_constraint('orders_ibfk_1', type_='foreignkey')
        batch_op.create_foreign_key('orders_ibfk_1', 'users', ['user_id'], ['user_id'])

    with op.batch_alter_table('transactions') as batch_op:
        batch_op.drop_constraint('transactions_ibfk_1', type_='foreignkey')
        batch_op.create_foreign_key('transactions_ibfk_1', 'users', ['user_id'], ['user_id'])


def downgrade():
    # Revert column name change
    with op.batch_alter_table('users') as batch_op:
        batch_op.alter_column('user_id', new_column_name='id', existing_type=sa.Integer())

    # Revert foreign keys
    with op.batch_alter_table('cart') as batch_op:
        batch_op.drop_constraint('fk_cart_user', type_='foreignkey')
        batch_op.create_foreign_key('fk_cart_user', 'users', ['user_id'], ['id'], ondelete='CASCADE')

    with op.batch_alter_table('clients') as batch_op:
        batch_op.drop_constraint('clients_ibfk_1', type_='foreignkey')
        batch_op.create_foreign_key('clients_ibfk_1', 'users', ['user_id'], ['id'], ondelete='CASCADE')

    with op.batch_alter_table('orders') as batch_op:
        batch_op.drop_constraint('orders_ibfk_1', type_='foreignkey')
        batch_op.create_foreign_key('orders_ibfk_1', 'users', ['user_id'], ['id'])

    with op.batch_alter_table('transactions') as batch_op:
        batch_op.drop_constraint('transactions_ibfk_1', type_='foreignkey')
        batch_op.create_foreign_key('transactions_ibfk_1', 'users', ['user_id'], ['id'])
