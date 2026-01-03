"""add_content_metadata

Revision ID: 006_content_metadata
Revises: 005_raw_content
Create Date: 2026-01-03 16:00:00.000000

Add content_type, keywords, and tldr fields to support content categorization
and filtering in the library view.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '006_content_metadata'
down_revision: Union[str, None] = '005_raw_content'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Add content metadata columns to transcripts table.

    - content_type: Category of content (e.g., programming_technical, tutorial_howto, educational)
    - keywords: JSON array of extracted keywords/tags from content
    - tldr: Short summary/preview text for library cards
    """
    # Add content_type column (nullable, extracted from summaries or set manually)
    op.add_column('transcripts', sa.Column('content_type', sa.String(50), nullable=True))

    # Add keywords column (JSON stored as text)
    op.add_column('transcripts', sa.Column('keywords', sa.Text(), nullable=True))

    # Add tldr column (short summary for cards)
    op.add_column('transcripts', sa.Column('tldr', sa.Text(), nullable=True))

    print("✅ Migration 006 complete:")
    print("  - Added content_type column for content categorization")
    print("  - Added keywords column for tag-based filtering")
    print("  - Added tldr column for card previews")


def downgrade() -> None:
    """
    Rollback content metadata additions.
    """
    op.drop_column('transcripts', 'tldr')
    op.drop_column('transcripts', 'keywords')
    op.drop_column('transcripts', 'content_type')

    print("✅ Migration 006 rolled back")
