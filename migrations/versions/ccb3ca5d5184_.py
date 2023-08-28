"""empty message

Revision ID: ccb3ca5d5184
Revises: e18437536d7c
Create Date: 2023-08-25 15:03:18.230627

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ccb3ca5d5184'
down_revision = 'e18437536d7c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('product_transaction_attributes', schema=None) as batch_op:
        batch_op.drop_constraint('product_transaction_attributes_ibfk_2', type_='foreignkey')
        batch_op.drop_constraint('product_transaction_attributes_ibfk_3', type_='foreignkey')
        batch_op.create_foreign_key(None, 'users', ['payment_approve_by'], ['id'], ondelete='CASCADE')
        batch_op.create_foreign_key(None, 'users', ['deliver_by'], ['id'], ondelete='CASCADE')

    with op.batch_alter_table('product_transactions', schema=None) as batch_op:
        batch_op.drop_constraint('product_transactions_ibfk_2', type_='foreignkey')
        batch_op.drop_constraint('product_transactions_ibfk_1', type_='foreignkey')
        batch_op.create_foreign_key(None, 'users', ['user_id'], ['id'], ondelete='CASCADE')
        batch_op.create_foreign_key(None, 'users', ['cashier_id'], ['id'], ondelete='CASCADE')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('product_transactions', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('product_transactions_ibfk_1', 'users', ['user_id'], ['id'])
        batch_op.create_foreign_key('product_transactions_ibfk_2', 'users', ['cashier_id'], ['id'])

    with op.batch_alter_table('product_transaction_attributes', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('product_transaction_attributes_ibfk_3', 'users', ['deliver_by'], ['id'])
        batch_op.create_foreign_key('product_transaction_attributes_ibfk_2', 'users', ['payment_approve_by'], ['id'])

    # ### end Alembic commands ###
