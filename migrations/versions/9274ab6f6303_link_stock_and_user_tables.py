"""link stock and user tables

Revision ID: 9274ab6f6303
Revises: b84bb0bda0fb
Create Date: 2020-11-19 12:22:56.295278

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9274ab6f6303'
down_revision = 'b84bb0bda0fb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('stocks', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'stocks', 'users', ['user_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'stocks', type_='foreignkey')
    op.drop_column('stocks', 'user_id')
    # ### end Alembic commands ###
