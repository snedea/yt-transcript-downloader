"""
Transcript Cache Service

Provides persistent storage for downloaded transcripts using SQLite.
"""

import os
import json
import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Database path - use environment variable or local data directory
# In Docker: /app/data/transcripts.db
# Local development: ./data/transcripts.db (relative to backend folder)
_default_db_path = Path(__file__).parent.parent.parent / "data" / "transcripts.db"
DB_PATH = Path(os.getenv("DB_PATH", str(_default_db_path)))


class TranscriptCacheService:
    """
    Service for caching transcripts in SQLite.

    Provides persistent storage that survives container restarts.
    """

    def __init__(self, db_path: Path = DB_PATH):
        """Initialize the cache service."""
        self.db_path = db_path
        self._ensure_db_exists()

    def _ensure_db_exists(self):
        """Create database and tables if they don't exist."""
        # Ensure directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS transcripts (
                    video_id TEXT PRIMARY KEY,
                    video_title TEXT NOT NULL,
                    author TEXT,
                    upload_date TEXT,
                    transcript TEXT NOT NULL,
                    transcript_data TEXT,
                    tokens_used INTEGER DEFAULT 0,
                    is_cleaned INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    last_accessed TEXT NOT NULL,
                    access_count INTEGER DEFAULT 1,
                    analysis_result TEXT,
                    analysis_date TEXT
                )
            """)

            # Add analysis columns if they don't exist (for existing databases)
            try:
                conn.execute("ALTER TABLE transcripts ADD COLUMN analysis_result TEXT")
            except sqlite3.OperationalError:
                pass  # Column already exists
            try:
                conn.execute("ALTER TABLE transcripts ADD COLUMN analysis_date TEXT")
            except sqlite3.OperationalError:
                pass  # Column already exists

            # Add summary columns if they don't exist (for content summary feature)
            try:
                conn.execute("ALTER TABLE transcripts ADD COLUMN summary_result TEXT")
            except sqlite3.OperationalError:
                pass  # Column already exists
            try:
                conn.execute("ALTER TABLE transcripts ADD COLUMN summary_date TEXT")
            except sqlite3.OperationalError:
                pass  # Column already exists

            # Create index for faster lookups
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_last_accessed
                ON transcripts(last_accessed DESC)
            """)

            # Create FTS5 virtual table for full-text search
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS transcripts_fts USING fts5(
                    video_id,
                    video_title,
                    author,
                    transcript,
                    tags,
                    content_type,
                    content='transcripts',
                    content_rowid='rowid'
                )
            """)

            # Create triggers to keep FTS in sync
            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS transcripts_fts_ai AFTER INSERT ON transcripts BEGIN
                    INSERT INTO transcripts_fts(rowid, video_id, video_title, author, transcript, tags, content_type)
                    VALUES (new.rowid, new.video_id, new.video_title, COALESCE(new.author, ''), new.transcript, '', '');
                END
            """)

            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS transcripts_fts_ad AFTER DELETE ON transcripts BEGIN
                    INSERT INTO transcripts_fts(transcripts_fts, rowid, video_id, video_title, author, transcript, tags, content_type)
                    VALUES ('delete', old.rowid, old.video_id, old.video_title, COALESCE(old.author, ''), old.transcript, '', '');
                END
            """)

            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS transcripts_fts_au AFTER UPDATE ON transcripts BEGIN
                    INSERT INTO transcripts_fts(transcripts_fts, rowid, video_id, video_title, author, transcript, tags, content_type)
                    VALUES ('delete', old.rowid, old.video_id, old.video_title, COALESCE(old.author, ''), old.transcript, '', '');
                    INSERT INTO transcripts_fts(rowid, video_id, video_title, author, transcript, tags, content_type)
                    VALUES (new.rowid, new.video_id, new.video_title, COALESCE(new.author, ''), new.transcript, '', '');
                END
            """)

            conn.commit()
            logger.info(f"Database initialized at {self.db_path}")

            # Rebuild FTS index if it's empty but transcripts exist
            self._ensure_fts_populated()

    @contextmanager
    def _get_connection(self):
        """Get a database connection with context manager."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def get(self, video_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a cached transcript by video ID.

        Updates last_accessed and access_count on retrieval.
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM transcripts WHERE video_id = ?",
                (video_id,)
            )
            row = cursor.fetchone()

            if row:
                # Update access stats
                now = datetime.utcnow().isoformat()
                conn.execute(
                    """
                    UPDATE transcripts
                    SET last_accessed = ?, access_count = access_count + 1
                    WHERE video_id = ?
                    """,
                    (now, video_id)
                )
                conn.commit()

                # Convert to dict
                result = dict(row)

                # Parse transcript_data JSON if present
                if result.get('transcript_data'):
                    try:
                        result['transcript_data'] = json.loads(result['transcript_data'])
                    except json.JSONDecodeError:
                        result['transcript_data'] = None

                # Parse analysis_result JSON if present
                if result.get('analysis_result'):
                    try:
                        result['analysis_result'] = json.loads(result['analysis_result'])
                    except json.JSONDecodeError:
                        result['analysis_result'] = None

                # Parse summary_result JSON if present
                if result.get('summary_result'):
                    try:
                        result['summary_result'] = json.loads(result['summary_result'])
                    except json.JSONDecodeError:
                        result['summary_result'] = None

                # Convert is_cleaned to bool
                result['is_cleaned'] = bool(result.get('is_cleaned', 0))

                logger.info(f"Cache hit for video {video_id}")
                return result

            logger.info(f"Cache miss for video {video_id}")
            return None

    def save(
        self,
        video_id: str,
        video_title: str,
        transcript: str,
        author: Optional[str] = None,
        upload_date: Optional[str] = None,
        transcript_data: Optional[List[Dict]] = None,
        tokens_used: int = 0,
        is_cleaned: bool = False
    ) -> bool:
        """
        Save a transcript to the cache.

        Uses INSERT OR REPLACE to update existing entries.
        """
        now = datetime.utcnow().isoformat()

        # Serialize transcript_data to JSON
        transcript_data_json = None
        if transcript_data:
            transcript_data_json = json.dumps(transcript_data)

        try:
            with self._get_connection() as conn:
                # Check if exists to preserve access_count
                cursor = conn.execute(
                    "SELECT access_count, created_at FROM transcripts WHERE video_id = ?",
                    (video_id,)
                )
                existing = cursor.fetchone()

                if existing:
                    # Update existing entry
                    conn.execute(
                        """
                        UPDATE transcripts SET
                            video_title = ?,
                            author = ?,
                            upload_date = ?,
                            transcript = ?,
                            transcript_data = ?,
                            tokens_used = ?,
                            is_cleaned = ?,
                            last_accessed = ?,
                            access_count = access_count + 1
                        WHERE video_id = ?
                        """,
                        (
                            video_title, author, upload_date, transcript,
                            transcript_data_json, tokens_used, int(is_cleaned),
                            now, video_id
                        )
                    )
                else:
                    # Insert new entry
                    conn.execute(
                        """
                        INSERT INTO transcripts (
                            video_id, video_title, author, upload_date,
                            transcript, transcript_data, tokens_used, is_cleaned,
                            created_at, last_accessed, access_count
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                        """,
                        (
                            video_id, video_title, author, upload_date,
                            transcript, transcript_data_json, tokens_used,
                            int(is_cleaned), now, now
                        )
                    )

                conn.commit()
                logger.info(f"Saved transcript for video {video_id} to cache")
                return True

        except Exception as e:
            logger.error(f"Failed to save transcript to cache: {e}")
            return False

    def get_history(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get transcript history, ordered by last accessed."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT video_id, video_title, author, is_cleaned,
                       created_at, last_accessed, access_count,
                       CASE WHEN analysis_result IS NOT NULL THEN 1 ELSE 0 END as has_analysis,
                       CASE WHEN summary_result IS NOT NULL THEN 1 ELSE 0 END as has_summary
                FROM transcripts
                ORDER BY last_accessed DESC
                LIMIT ? OFFSET ?
                """,
                (limit, offset)
            )

            items = []
            for row in cursor.fetchall():
                item = dict(row)
                item['is_cleaned'] = bool(item.get('is_cleaned', 0))
                item['has_analysis'] = bool(item.get('has_analysis', 0))
                item['has_summary'] = bool(item.get('has_summary', 0))
                items.append(item)

            return items

    def get_total_count(self) -> int:
        """Get total number of cached transcripts."""
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM transcripts")
            return cursor.fetchone()[0]

    def delete(self, video_id: str) -> bool:
        """Delete a cached transcript."""
        try:
            with self._get_connection() as conn:
                conn.execute(
                    "DELETE FROM transcripts WHERE video_id = ?",
                    (video_id,)
                )
                conn.commit()
                logger.info(f"Deleted transcript {video_id} from cache")
                return True
        except Exception as e:
            logger.error(f"Failed to delete transcript: {e}")
            return False

    def clear_all(self) -> bool:
        """Clear all cached transcripts."""
        try:
            with self._get_connection() as conn:
                conn.execute("DELETE FROM transcripts")
                conn.commit()
                logger.info("Cleared all cached transcripts")
                return True
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return False

    def search(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search transcripts by title or content."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT video_id, video_title, author, is_cleaned,
                       created_at, last_accessed, access_count
                FROM transcripts
                WHERE video_title LIKE ? OR transcript LIKE ?
                ORDER BY last_accessed DESC
                LIMIT ?
                """,
                (f"%{query}%", f"%{query}%", limit)
            )

            items = []
            for row in cursor.fetchall():
                item = dict(row)
                item['is_cleaned'] = bool(item.get('is_cleaned', 0))
                items.append(item)

            return items

    def save_analysis(self, video_id: str, analysis_result: Dict[str, Any]) -> bool:
        """
        Save rhetorical analysis results for a video.

        Args:
            video_id: YouTube video ID
            analysis_result: The complete analysis result dictionary

        Returns:
            True if saved successfully, False otherwise
        """
        now = datetime.utcnow().isoformat()
        analysis_json = json.dumps(analysis_result)

        try:
            with self._get_connection() as conn:
                conn.execute(
                    """
                    UPDATE transcripts
                    SET analysis_result = ?, analysis_date = ?
                    WHERE video_id = ?
                    """,
                    (analysis_json, now, video_id)
                )
                conn.commit()

                if conn.total_changes > 0:
                    logger.info(f"Saved analysis for video {video_id}")
                    return True
                else:
                    logger.warning(f"No transcript found to save analysis for video {video_id}")
                    return False

        except Exception as e:
            logger.error(f"Failed to save analysis: {e}")
            return False

    def get_analysis(self, video_id: str) -> Optional[Dict[str, Any]]:
        """
        Get cached analysis results for a video.

        Returns:
            Analysis result dict or None if not found
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT analysis_result, analysis_date FROM transcripts WHERE video_id = ?",
                (video_id,)
            )
            row = cursor.fetchone()

            if row and row['analysis_result']:
                try:
                    return {
                        'analysis': json.loads(row['analysis_result']),
                        'analysis_date': row['analysis_date']
                    }
                except json.JSONDecodeError:
                    return None

            return None

    def has_analysis(self, video_id: str) -> bool:
        """Check if a video has cached analysis."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT 1 FROM transcripts WHERE video_id = ? AND analysis_result IS NOT NULL",
                (video_id,)
            )
            return cursor.fetchone() is not None

    def save_summary(self, video_id: str, summary_result: Dict[str, Any]) -> bool:
        """
        Save content summary results for a video.

        Args:
            video_id: YouTube video ID
            summary_result: The complete summary result dictionary

        Returns:
            True if saved successfully, False otherwise
        """
        now = datetime.utcnow().isoformat()
        summary_json = json.dumps(summary_result)

        try:
            with self._get_connection() as conn:
                conn.execute(
                    """
                    UPDATE transcripts
                    SET summary_result = ?, summary_date = ?
                    WHERE video_id = ?
                    """,
                    (summary_json, now, video_id)
                )
                conn.commit()

                if conn.total_changes > 0:
                    logger.info(f"Saved summary for video {video_id}")
                    return True
                else:
                    logger.warning(f"No transcript found to save summary for video {video_id}")
                    return False

        except Exception as e:
            logger.error(f"Failed to save summary: {e}")
            return False

    def get_summary(self, video_id: str) -> Optional[Dict[str, Any]]:
        """
        Get cached summary results for a video.

        Returns:
            Summary result dict or None if not found
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT summary_result, summary_date FROM transcripts WHERE video_id = ?",
                (video_id,)
            )
            row = cursor.fetchone()

            if row and row['summary_result']:
                try:
                    return {
                        'summary': json.loads(row['summary_result']),
                        'summary_date': row['summary_date']
                    }
                except json.JSONDecodeError:
                    return None

            return None

    def has_summary(self, video_id: str) -> bool:
        """Check if a video has cached summary."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT 1 FROM transcripts WHERE video_id = ? AND summary_result IS NOT NULL",
                (video_id,)
            )
            return cursor.fetchone() is not None

    def _ensure_fts_populated(self):
        """Ensure FTS index is populated with existing transcript data."""
        with self._get_connection() as conn:
            # Check if FTS is empty but transcripts exist
            fts_count = conn.execute("SELECT COUNT(*) FROM transcripts_fts").fetchone()[0]
            transcript_count = conn.execute("SELECT COUNT(*) FROM transcripts").fetchone()[0]

            if transcript_count > 0 and fts_count == 0:
                logger.info(f"Rebuilding FTS index for {transcript_count} transcripts...")
                self._rebuild_fts_index_internal(conn)

    def _rebuild_fts_index_internal(self, conn):
        """Internal method to rebuild FTS index with an existing connection."""
        cursor = conn.execute("""
            SELECT
                rowid,
                video_id,
                video_title,
                author,
                transcript,
                summary_result
            FROM transcripts
        """)

        for row in cursor.fetchall():
            tags = ""
            content_type = ""
            if row['summary_result']:
                try:
                    summary = json.loads(row['summary_result'])
                    keywords = summary.get('keywords', [])
                    tags = ' '.join(keywords) if keywords else ''
                    content_type = summary.get('content_type', '') or ''
                except (json.JSONDecodeError, TypeError):
                    pass

            conn.execute("""
                INSERT INTO transcripts_fts(rowid, video_id, video_title, author, transcript, tags, content_type)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (row['rowid'], row['video_id'], row['video_title'],
                  row['author'] or '', row['transcript'], tags, content_type))

        conn.commit()
        logger.info("FTS index rebuilt successfully")

    def rebuild_fts_index(self):
        """Rebuild the FTS index from scratch."""
        with self._get_connection() as conn:
            # Clear existing FTS data
            conn.execute("DELETE FROM transcripts_fts")
            self._rebuild_fts_index_internal(conn)

    def advanced_search(
        self,
        query: str = "",
        content_types: Optional[List[str]] = None,
        has_summary: Optional[bool] = None,
        has_analysis: Optional[bool] = None,
        tags: Optional[List[str]] = None,
        limit: int = 50,
        offset: int = 0,
        order_by: str = "last_accessed"
    ) -> List[Dict[str, Any]]:
        """
        Advanced search with filters and full-text search.

        Args:
            query: Full-text search query (searches title, transcript, tags)
            content_types: Filter by content type(s)
            has_summary: Filter by whether summary exists
            has_analysis: Filter by whether analysis exists
            tags: Filter by specific tags (all must match)
            limit: Max results
            offset: Pagination offset
            order_by: 'last_accessed', 'created_at', 'title'
        """
        with self._get_connection() as conn:
            conditions = []
            params = []

            # Full-text search using FTS5
            if query and query.strip():
                # Escape special FTS5 characters and add prefix matching
                safe_query = query.replace('"', '""').strip()
                conditions.append("""
                    video_id IN (
                        SELECT video_id FROM transcripts_fts
                        WHERE transcripts_fts MATCH ?
                    )
                """)
                # Use prefix matching for partial words
                params.append(f'"{safe_query}"*')

            # Content type filter
            if content_types:
                placeholders = ','.join(['?' for _ in content_types])
                conditions.append(f"""
                    json_extract(summary_result, '$.content_type') IN ({placeholders})
                """)
                params.extend(content_types)

            # Has summary filter
            if has_summary is not None:
                if has_summary:
                    conditions.append("summary_result IS NOT NULL")
                else:
                    conditions.append("summary_result IS NULL")

            # Has analysis filter
            if has_analysis is not None:
                if has_analysis:
                    conditions.append("analysis_result IS NOT NULL")
                else:
                    conditions.append("analysis_result IS NULL")

            # Tag filter (all tags must be present in keywords)
            if tags:
                for tag in tags:
                    conditions.append("""
                        json_extract(summary_result, '$.keywords') LIKE ?
                    """)
                    params.append(f'%"{tag}"%')

            # Build WHERE clause
            where_clause = ""
            if conditions:
                where_clause = "WHERE " + " AND ".join(conditions)

            # Order by clause
            order_clause = {
                'last_accessed': 'ORDER BY last_accessed DESC',
                'created_at': 'ORDER BY created_at DESC',
                'title': 'ORDER BY video_title ASC'
            }.get(order_by, 'ORDER BY last_accessed DESC')

            sql = f"""
                SELECT
                    video_id,
                    video_title,
                    author,
                    is_cleaned,
                    created_at,
                    last_accessed,
                    access_count,
                    CASE WHEN analysis_result IS NOT NULL THEN 1 ELSE 0 END as has_analysis,
                    CASE WHEN summary_result IS NOT NULL THEN 1 ELSE 0 END as has_summary,
                    json_extract(summary_result, '$.content_type') as content_type,
                    json_extract(summary_result, '$.keywords') as keywords,
                    json_extract(summary_result, '$.tldr') as tldr
                FROM transcripts
                {where_clause}
                {order_clause}
                LIMIT ? OFFSET ?
            """
            params.extend([limit, offset])

            cursor = conn.execute(sql, params)

            items = []
            for row in cursor.fetchall():
                item = dict(row)
                item['is_cleaned'] = bool(item.get('is_cleaned', 0))
                item['has_analysis'] = bool(item.get('has_analysis', 0))
                item['has_summary'] = bool(item.get('has_summary', 0))
                # Parse keywords JSON
                if item.get('keywords'):
                    try:
                        item['keywords'] = json.loads(item['keywords'])
                    except (json.JSONDecodeError, TypeError):
                        item['keywords'] = []
                else:
                    item['keywords'] = []
                items.append(item)

            return items

    def get_all_tags(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all unique tags with their counts for faceted search."""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT
                    value as tag,
                    COUNT(*) as count
                FROM transcripts, json_each(json_extract(summary_result, '$.keywords'))
                WHERE summary_result IS NOT NULL
                GROUP BY value
                ORDER BY count DESC
                LIMIT ?
            """, (limit,))
            return [{'tag': row['tag'], 'count': row['count']} for row in cursor.fetchall()]

    def get_content_type_counts(self) -> Dict[str, int]:
        """Get count of videos per content type."""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT
                    json_extract(summary_result, '$.content_type') as content_type,
                    COUNT(*) as count
                FROM transcripts
                WHERE summary_result IS NOT NULL
                GROUP BY content_type
            """)
            return {row['content_type']: row['count'] for row in cursor.fetchall() if row['content_type']}

    def get_stats(self) -> Dict[str, int]:
        """Get library statistics."""
        with self._get_connection() as conn:
            total = conn.execute("SELECT COUNT(*) FROM transcripts").fetchone()[0]
            with_summary = conn.execute(
                "SELECT COUNT(*) FROM transcripts WHERE summary_result IS NOT NULL"
            ).fetchone()[0]
            with_analysis = conn.execute(
                "SELECT COUNT(*) FROM transcripts WHERE analysis_result IS NOT NULL"
            ).fetchone()[0]

            return {
                'total': total,
                'with_summary': with_summary,
                'with_analysis': with_analysis
            }


# Singleton instance
_cache_service: Optional[TranscriptCacheService] = None


def get_cache_service() -> TranscriptCacheService:
    """Get or create the cache service singleton."""
    global _cache_service
    if _cache_service is None:
        _cache_service = TranscriptCacheService()
    return _cache_service
