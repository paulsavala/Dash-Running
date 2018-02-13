"""empty message

Revision ID: e42559deeb98
Revises: 87d084ae21fd
Create Date: 2018-02-12 19:53:21.728670

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e42559deeb98'
down_revision = '87d084ae21fd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('run', sa.Column('date', sa.Date(), nullable=True))
    op.add_column('run', sa.Column('distance', sa.Float(), nullable=True))
    op.add_column('run', sa.Column('elevation_gain', sa.Float(), nullable=True))
    op.add_column('run', sa.Column('time', sa.Time(), nullable=True))
    op.create_index(op.f('ix_run_date'), 'run', ['date'], unique=False)
    op.create_index(op.f('ix_run_distance'), 'run', ['distance'], unique=False)
    op.create_index(op.f('ix_run_elevation_gain'), 'run', ['elevation_gain'], unique=False)
    op.create_index(op.f('ix_run_time'), 'run', ['time'], unique=False)
    op.drop_index('ix_run_timestamp', table_name='run')
    op.drop_column('run', 'timestamp')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('run', sa.Column('timestamp', sa.DATETIME(), nullable=True))
    op.create_index('ix_run_timestamp', 'run', ['timestamp'], unique=False)
    op.drop_index(op.f('ix_run_time'), table_name='run')
    op.drop_index(op.f('ix_run_elevation_gain'), table_name='run')
    op.drop_index(op.f('ix_run_distance'), table_name='run')
    op.drop_index(op.f('ix_run_date'), table_name='run')
    op.drop_column('run', 'time')
    op.drop_column('run', 'elevation_gain')
    op.drop_column('run', 'distance')
    op.drop_column('run', 'date')
    # ### end Alembic commands ###
