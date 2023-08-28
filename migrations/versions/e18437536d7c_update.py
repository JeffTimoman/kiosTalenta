"""Update

Revision ID: e18437536d7c
Revises: 8f72b8c7c6b1
Create Date: 2023-08-25 10:51:36.014943

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'e18437536d7c'
down_revision = '8f72b8c7c6b1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('active',
               existing_type=mysql.INTEGER(display_width=11),
               type_=sa.Boolean(),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('active',
               existing_type=sa.Boolean(),
               type_=mysql.INTEGER(display_width=11),
               existing_nullable=True)

    # ### end Alembic commands ###
