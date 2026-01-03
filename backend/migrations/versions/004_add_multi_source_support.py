"""add_multi_source_support

Revision ID: 004_multi_source
Revises: 003_composite_pk
Create Date: 2026-01-03 12:00:00.000000

Add support for multiple content source types (PDF, web, plain text) in addition
to YouTube videos. Adds source_type, file storage paths, and metadata fields.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision: str = '004_multi_source'
down_revision: Union[str, None] = '003_composite_pk'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Add multi-source support to transcripts table.

    Steps:
    1. Add source_type column (youtube, pdf, web_url, plain_text)
    2. Add file storage paths (file_path, thumbnail_path)
    3. Add content metadata (word_count, character_count, page_count)
    4. Add source_url for original filename/URL reference
    5. Backfill source_type='youtube' for existing records
    6. Backfill word_count from existing transcripts
    7. Create indexes for efficient querying
    """
    connection = op.get_bind()

    # Step 1: Add source_type column
    op.add_column('transcripts', sa.Column('source_type', sa.String(20), nullable=True))

    # Step 2: Add file storage paths
    op.add_column('transcripts', sa.Column('source_url', sa.String(500), nullable=True))
    op.add_column('transcripts', sa.Column('file_path', sa.String(500), nullable=True))
    op.add_column('transcripts', sa.Column('thumbnail_path', sa.String(500), nullable=True))

    # Step 3: Add content metadata
    op.add_column('transcripts', sa.Column('word_count', sa.Integer(), nullable=True))
    op.add_column('transcripts', sa.Column('character_count', sa.Integer(), nullable=True))
    op.add_column('transcripts', sa.Column('page_count', sa.Integer(), nullable=True))

    # Step 4: Backfill source_type='youtube' for all existing records
    connection.execute(text(
        "UPDATE transcripts SET source_type = 'youtube' WHERE source_type IS NULL"
    ))

    # Step 5: Set default values for word_count and character_count
    connection.execute(text(
        "UPDATE transcripts SET word_count = 0 WHERE word_count IS NULL"
    ))
    connection.execute(text(
        "UPDATE transcripts SET character_count = 0 WHERE character_count IS NULL"
    ))

    # Step 6: Backfill word_count from existing transcript text
    # SQLite-compatible word count calculation
    connection.execute(text("""
        UPDATE transcripts
        SET word_count = (
            LENGTH(transcript) - LENGTH(REPLACE(transcript, ' ', '')) +
            CASE WHEN LENGTH(TRIM(transcript)) > 0 THEN 1 ELSE 0 END
        )
        WHERE word_count = 0 AND transcript IS NOT NULL AND LENGTH(TRIM(transcript)) > 0
    """))

    # Step 7: Backfill character_count from existing transcript text
    connection.execute(text("""
        UPDATE transcripts
        SET character_count = LENGTH(transcript)
        WHERE character_count = 0 AND transcript IS NOT NULL
    """))

    # Step 8: Make source_type NOT NULL now that all rows have values
    # SQLite doesn't support ALTER COLUMN directly, but we can set default for new rows
    # Existing rows already have 'youtube' from Step 4

    # Step 9: Create indexes for efficient filtering
    op.create_index('idx_transcripts_source_type', 'transcripts', ['source_type'])
    op.create_index('idx_transcripts_user_source', 'transcripts', ['user_id', 'source_type'])

    print("✅ Migration 004 complete:")
    print("  - Added source_type, file_path, thumbnail_path columns")
    print("  - Added word_count, character_count, page_count columns")
    print("  - Backfilled source_type='youtube' for existing videos")
    print("  - Backfilled word counts from transcript text")
    print("  - Created indexes on source_type")


def downgrade() -> None:
    """
    Rollback multi-source support changes.
    """
    # Drop indexes
    op.drop_index('idx_transcripts_user_source', table_name='transcripts')
    op.drop_index('idx_transcripts_source_type', table_name='transcripts')

    # Drop columns
    op.drop_column('transcripts', 'page_count')
    op.drop_column('transcripts', 'character_count')
    op.drop_column('transcripts', 'word_count')
    op.drop_column('transcripts', 'thumbnail_path')
    op.drop_column('transcripts', 'file_path')
    op.drop_column('transcripts', 'source_url')
    op.drop_column('transcripts', 'source_type')

    print("✅ Migration 004 rolled back")
