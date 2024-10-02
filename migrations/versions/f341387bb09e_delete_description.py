"""delete description

Revision ID: f341387bb09e
Revises: ebe490a1842a
Create Date: 2024-09-28 17:34:25.231141

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f341387bb09e'
down_revision = 'ebe490a1842a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.drop_column('description')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.add_column(sa.Column('description', sa.VARCHAR(length=255), nullable=False))

    # ### end Alembic commands ###
