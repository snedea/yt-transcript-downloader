"""composite_primary_key_and_data_migration

Revision ID: 003_composite_pk
Revises: update_transcripts
Create Date: 2026-01-02 10:00:00.000000

IMPORTANT: This migration restructures the transcripts table to use a composite
primary key (video_id, user_id) and migrates existing data.

Existing transcripts with NULL user_id will be assigned to a default system user.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy import text
import uuid

# revision identifiers, used by Alembic.
revision: str = '003_composite_pk'
down_revision: Union[str, None] = 'update_transcripts'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Upgrade to composite primary key schema.

    Steps:
    1. Create a default system user for orphaned transcripts
    2. Update NULL user_id values to the system user
    3. Create new transcripts table with composite PK
    4. Migrate data from old table to new table
    5. Drop old table and rename new table
    """
    connection = op.get_bind()

    # Step 1: Create system user for orphaned transcripts
    # Check if system user already exists
    system_user_id = str(uuid.uuid4())
    result = connection.execute(text(
        "SELECT id FROM users WHERE email = 'system@transcripts.local'"
    ))
    existing_user = result.fetchone()

    if existing_user:
        system_user_id = str(existing_user[0])
        print(f"Using existing system user: {system_user_id}")
    else:
        # Create system user
        connection.execute(text(
            """
            INSERT INTO users (id, email, username, is_active, is_verified, created_at)
            VALUES (:id, :email, :username, :is_active, :is_verified, datetime('now'))
            """
        ), {
            "id": system_user_id,
            "email": "system@transcripts.local",
            "username": "system",
            "is_active": True,
            "is_verified": True
        })
        print(f"Created system user: {system_user_id}")

    # Step 2: Update NULL user_id values
    result = connection.execute(text(
        "UPDATE transcripts SET user_id = :system_user_id WHERE user_id IS NULL"
    ), {"system_user_id": system_user_id})

    updated_count = result.rowcount
    if updated_count > 0:
        print(f"Assigned {updated_count} orphaned transcripts to system user")

    # Step 3: Create new table with composite primary key
    # Using batch mode for SQLite compatibility
    with op.batch_alter_table('transcripts', schema=None) as batch_op:
        # First, ensure user_id is not nullable
        batch_op.alter_column('user_id', nullable=False)

    # Step 4: Recreate table with composite primary key
    # SQLite doesn't support ALTER TABLE for primary keys, so we need to recreate

    # Create temporary table with new schema
    op.create_table('transcripts_new',
        sa.Column('video_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('video_title', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('author', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('upload_date', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('transcript', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('transcript_data', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('tokens_used', sa.Integer(), nullable=False),
        sa.Column('is_cleaned', sa.Boolean(), nullable=False),
        sa.Column('analysis_result', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('analysis_date', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('summary_result', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('summary_date', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('manipulation_result', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('manipulation_date', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('discovery_result', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('discovery_date', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('health_observation_result', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('health_observation_date', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('prompts_result', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('prompts_date', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('last_accessed', sa.DateTime(), nullable=False),
        sa.Column('access_count', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('video_id', 'user_id', name='pk_transcripts')
    )

    # Create indexes
    op.create_index('ix_transcripts_new_video_id', 'transcripts_new', ['video_id'], unique=False)
    op.create_index('ix_transcripts_new_user_id', 'transcripts_new', ['user_id'], unique=False)

    # Step 5: Copy data from old table to new table
    connection.execute(text(
        """
        INSERT INTO transcripts_new (
            video_id, user_id, video_title, author, upload_date, transcript,
            transcript_data, tokens_used, is_cleaned,
            analysis_result, analysis_date, summary_result, summary_date,
            manipulation_result, manipulation_date, discovery_result, discovery_date,
            health_observation_result, health_observation_date,
            prompts_result, prompts_date,
            created_at, last_accessed, access_count
        )
        SELECT
            video_id, user_id, video_title, author, upload_date, transcript,
            transcript_data, tokens_used, is_cleaned,
            analysis_result, analysis_date, summary_result, summary_date,
            manipulation_result, manipulation_date, discovery_result, discovery_date,
            health_observation_result, health_observation_date,
            prompts_result, prompts_date,
            created_at, last_accessed, access_count
        FROM transcripts
        """
    ))

    # Step 6: Drop old table and rename new table
    op.drop_index('ix_transcripts_user_id', table_name='transcripts')
    op.drop_table('transcripts')
    op.rename_table('transcripts_new', 'transcripts')

    print("Migration complete: transcripts table now uses composite primary key (video_id, user_id)")


def downgrade() -> None:
    """
    Downgrade from composite primary key schema.

    WARNING: This will lose data if multiple users have transcripts for the same video_id.
    Only the first user's transcript for each video will be preserved.
    """
    connection = op.get_bind()

    # Create old-style table with single primary key
    op.create_table('transcripts_old',
        sa.Column('video_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('video_title', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('author', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('upload_date', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('transcript', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('transcript_data', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('tokens_used', sa.Integer(), nullable=False),
        sa.Column('is_cleaned', sa.Boolean(), nullable=False),
        sa.Column('analysis_result', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('analysis_date', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('summary_result', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('summary_date', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('manipulation_result', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('manipulation_date', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('discovery_result', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('discovery_date', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('health_observation_result', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('health_observation_date', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('prompts_result', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('prompts_date', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('last_accessed', sa.DateTime(), nullable=False),
        sa.Column('access_count', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('video_id')
    )

    op.create_index('ix_transcripts_old_user_id', 'transcripts_old', ['user_id'], unique=False)

    # Copy data - this will LOSE duplicates (only first user's transcript per video is kept)
    connection.execute(text(
        """
        INSERT INTO transcripts_old (
            video_id, video_title, author, upload_date, transcript,
            transcript_data, tokens_used, is_cleaned,
            analysis_result, analysis_date, summary_result, summary_date,
            manipulation_result, manipulation_date, discovery_result, discovery_date,
            health_observation_result, health_observation_date,
            prompts_result, prompts_date,
            created_at, last_accessed, access_count, user_id
        )
        SELECT
            video_id, video_title, author, upload_date, transcript,
            transcript_data, tokens_used, is_cleaned,
            analysis_result, analysis_date, summary_result, summary_date,
            manipulation_result, manipulation_date, discovery_result, discovery_date,
            health_observation_result, health_observation_date,
            prompts_result, prompts_date,
            created_at, last_accessed, access_count, user_id
        FROM transcripts
        GROUP BY video_id
        """
    ))

    # Drop new table and rename old table
    op.drop_index('ix_transcripts_new_user_id', table_name='transcripts')
    op.drop_index('ix_transcripts_new_video_id', table_name='transcripts')
    op.drop_table('transcripts')
    op.rename_table('transcripts_old', 'transcripts')

    print("WARNING: Downgrade complete. Duplicate transcripts have been lost.")
