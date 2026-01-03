"""initial_auth

Revision ID: 1234567890ab
Revises: 
Create Date: 2024-05-22 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '1234567890ab'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users Table
    op.create_table('users',
        sa.Column('email', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('username', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_verified', sa.Boolean(), nullable=False),
        sa.Column('full_name', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('avatar_url', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('hashed_password', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    # OAuth Accounts Table
    op.create_table('oauth_accounts',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('oauth_name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('oauth_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('oauth_email', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('access_token', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('expires_at', sa.Integer(), nullable=True),
        sa.Column('refresh_token', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('account_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('account_email', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Refresh Tokens Table
    op.create_table('refresh_tokens',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('token_hash', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('revoked', sa.Boolean(), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_refresh_tokens_token_hash'), 'refresh_tokens', ['token_hash'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_refresh_tokens_token_hash'), table_name='refresh_tokens')
    op.drop_table('refresh_tokens')
    op.drop_table('oauth_accounts')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
