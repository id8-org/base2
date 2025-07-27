"""Create team table migration."""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'xxxx_create_team_table'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'team',
        sa.Column('id', sa.UUID(), primary_key=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(length=1000)),
        sa.Column('is_public', sa.Boolean(), default=True),
        sa.Column('owner_id', sa.UUID(), sa.ForeignKey('user.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
def downgrade():
    op.drop_table('team')
