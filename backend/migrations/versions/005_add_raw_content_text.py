"""add_raw_content_text

Revision ID: 005_raw_content
Revises: 004_multi_source
Create Date: 2026-01-03 14:00:00.000000

Add raw_content_text field to store original pasted text content.
This enables retrieval of the exact content users pasted, preserving
formatting and allowing re-processing if needed.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '005_raw_content'
down_revision: Union[str, None] = '004_multi_source'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Add raw_content_text column to transcripts table.

    This stores the original pasted text when source_type is 'plain_text',
    allowing users to retrieve exactly what they pasted.
    """
    # Add raw_content_text column (nullable, only used for plain_text source_type)
    op.add_column('transcripts', sa.Column('raw_content_text', sa.Text(), nullable=True))

    print("✅ Migration 005 complete:")
    print("  - Added raw_content_text column for storing original pasted text")


def downgrade() -> None:
    """
    Rollback raw_content_text addition.
    """
    op.drop_column('transcripts', 'raw_content_text')

    print("✅ Migration 005 rolled back")
