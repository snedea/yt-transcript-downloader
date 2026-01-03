"""add_user_id_to_transcripts

Revision ID: update_transcripts
Revises: 1234567890ab
Create Date: 2024-05-22 10:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'update_transcripts'
down_revision: Union[str, None] = '1234567890ab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('transcripts', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.String(36), nullable=True))
        batch_op.create_foreign_key('fk_transcripts_users', 'users', ['user_id'], ['id'])
        batch_op.create_index(batch_op.f('ix_transcripts_user_id'), ['user_id'], unique=False)


def downgrade() -> None:
    with op.batch_alter_table('transcripts', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_transcripts_user_id'))
        batch_op.drop_constraint('fk_transcripts_users', type_='foreignkey')
        batch_op.drop_column('user_id')
