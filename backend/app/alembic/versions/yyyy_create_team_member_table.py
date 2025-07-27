"""Create team_member table migration."""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'yyyy_create_team_member_table'
down_revision = 'xxxx_create_team_table'
branch_labels = None
depends_on = ('xxxx_create_team_table',)

def upgrade():
    op.create_table(
        'team_member',
        sa.Column('team_id', sa.UUID(), sa.ForeignKey('team.id', ondelete='CASCADE'), primary_key=True, nullable=False),
        sa.Column('user_id', sa.UUID(), sa.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True, nullable=False),
    )
def downgrade():
    op.drop_table('team_member')
