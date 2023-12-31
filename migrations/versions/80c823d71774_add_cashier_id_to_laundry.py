"""Add Cashier Id TO Laundry

Revision ID: 80c823d71774
Revises: 456cc0579fe3
Create Date: 2023-09-11 20:04:28.823170

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '80c823d71774'
down_revision = '456cc0579fe3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('laundry_transactions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('cashiser_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'users', ['cashiser_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('laundry_transactions', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('cashiser_id')

    # ### end Alembic commands ###
