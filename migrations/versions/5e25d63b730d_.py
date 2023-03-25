"""empty message

Revision ID: 5e25d63b730d
Revises: 5974a8319295
Create Date: 2023-03-18 23:18:50.497793

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5e25d63b730d'
down_revision = '5974a8319295'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('comments', schema=None) as batch_op:
        batch_op.alter_column('timestamp',
               existing_type=sa.DATETIME(),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('comments', schema=None) as batch_op:
        batch_op.alter_column('timestamp',
               existing_type=sa.DATETIME(),
               nullable=True)

    # ### end Alembic commands ###
