"""Description of changes

Revision ID: 9ea5725f2fdd
Revises: 
Create Date: 2024-09-27 22:47:29.329951

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '9ea5725f2fdd'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.drop_table('product')

def downgrade():
    # Optionally, you can re-create the table structure here if you want to allow downgrading
    op.create_table(
        'product',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=100), nullable=False, unique=True),
        sa.Column('description', sa.String(length=255), nullable=False),
        sa.Column('price', sa.Float(), nullable=False)
    )

