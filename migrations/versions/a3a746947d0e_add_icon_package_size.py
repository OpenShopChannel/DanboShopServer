"""Add icon/package size

Revision ID: a3a746947d0e
Revises: 366286f94954
Create Date: 2022-06-25 17:32:27.284383

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a3a746947d0e'
down_revision = '366286f94954'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('file_stats', sa.Column('icon_size', sa.Integer(), nullable=True))
    op.add_column('file_stats', sa.Column('package_size', sa.Integer(), nullable=True))

def downgrade():
    op.drop_column('file_stats', 'package_size')
    op.drop_column('file_stats', 'icon_size')
