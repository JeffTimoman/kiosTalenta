"""empty message

Revision ID: 4b959a8c2d5d
Revises: 35a3d332a646
Create Date: 2023-08-30 12:59:09.895674

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '4b959a8c2d5d'
down_revision = '35a3d332a646'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_rooms',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=30), nullable=True),
    sa.Column('date_created', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('room',
               existing_type=mysql.VARCHAR(length=10),
               type_=sa.Integer(),
               existing_nullable=True)
        batch_op.create_foreign_key(None, 'user_rooms', ['room'], ['id'], ondelete='SET NULL')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.alter_column('room',
               existing_type=sa.Integer(),
               type_=mysql.VARCHAR(length=10),
               existing_nullable=True)

    op.drop_table('user_rooms')
    # ### end Alembic commands ###
