"""Initial migration

Revision ID: 366286f94954
Revises:
Create Date: 2022-06-25 22:20:58.302708

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '366286f94954'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('author',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('display_name', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('url', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('file_stats',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('extracted_size', sa.Integer(), nullable=True),
    sa.Column('zip_size', sa.Integer(), nullable=True),
    sa.Column('extra_dirs', sa.ARRAY(sa.String(), dimensions=1), nullable=True),
    sa.Column('md5', sa.String(), nullable=True),
    sa.Column('sha256', sa.String(), nullable=True),
    sa.Column('package_type', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('repos',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('host', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_repos_host'), 'repos', ['host'], unique=False)
    op.create_table('application',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('slug', sa.String(), nullable=False),
    sa.Column('repo_id', sa.String(), nullable=True),
    sa.Column('date_added', sa.DateTime(), nullable=True),
    sa.Column('date_updated', sa.DateTime(), nullable=True),
    sa.Column('rating', sa.Integer(), nullable=True),
    sa.Column('downloads', sa.Integer(), nullable=True),
    sa.Column('category', sa.String(), nullable=False),
    sa.Column('version', sa.Integer(), nullable=True),
    sa.Column('theme', sa.Boolean(), nullable=True),
    sa.Column('author_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['author_id'], ['author.id'], ),
    sa.ForeignKeyConstraint(['repo_id'], ['repos.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('slug')
    )
    op.create_index(op.f('ix_application_category'), 'application', ['category'], unique=False)
    op.create_index(op.f('ix_application_repo_id'), 'application', ['repo_id'], unique=False)
    op.create_table('analytics',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('application_id', sa.Integer(), nullable=True),
    sa.Column('date', sa.DateTime(), nullable=True),
    sa.Column('type', sa.String(), nullable=False),
    sa.Column('value', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['application_id'], ['application.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('metadata',
    sa.Column('application_id', sa.Integer(), nullable=False),
    sa.Column('display_name', sa.String(), nullable=False),
    sa.Column('display_version', sa.String(), nullable=False),
    sa.Column('short_description', sa.String(), nullable=True),
    sa.Column('long_description', sa.String(), nullable=True),
    sa.Column('contributors', sa.String(), nullable=True),
    sa.Column('file_uuid', sa.String(), nullable=True),
    sa.Column('controllers', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['application_id'], ['application.id'], ),
    sa.ForeignKeyConstraint(['file_uuid'], ['file_stats.id'], ),
    sa.PrimaryKeyConstraint('application_id')
    )
    op.create_table('title_ids',
    sa.Column('application_id', sa.Integer(), nullable=False),
    sa.Column('sd_title', sa.String(), nullable=False),
    sa.Column('nand_title', sa.String(), nullable=False),
    sa.Column('forwarder_title', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['application_id'], ['application.id'], ),
    sa.PrimaryKeyConstraint('application_id')
    )


def downgrade():
    op.drop_table('title_ids')
    op.drop_table('metadata')
    op.drop_table('analytics')
    op.drop_index(op.f('ix_application_repo_id'), table_name='application')
    op.drop_index(op.f('ix_application_category'), table_name='application')
    op.drop_table('application')
    op.drop_index(op.f('ix_repos_host'), table_name='repos')
    op.drop_table('repos')
    op.drop_table('file_stats')
    op.drop_table('author')
