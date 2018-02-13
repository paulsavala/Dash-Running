"""Recreated run and user tables

Revision ID: 236c1726ba02
Revises: 
Create Date: 2018-02-12 19:59:26.590353

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '236c1726ba02'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    op.create_table('run',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=140), nullable=True),
    sa.Column('date', sa.Date(), nullable=True),
    sa.Column('time', sa.Time(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('distance', sa.Float(), nullable=True),
    sa.Column('elevation_gain', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_run_date'), 'run', ['date'], unique=False)
    op.create_index(op.f('ix_run_distance'), 'run', ['distance'], unique=False)
    op.create_index(op.f('ix_run_elevation_gain'), 'run', ['elevation_gain'], unique=False)
    op.create_index(op.f('ix_run_time'), 'run', ['time'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_run_time'), table_name='run')
    op.drop_index(op.f('ix_run_elevation_gain'), table_name='run')
    op.drop_index(op.f('ix_run_distance'), table_name='run')
    op.drop_index(op.f('ix_run_date'), table_name='run')
    op.drop_table('run')
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    # ### end Alembic commands ###
