import json
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any, Union
import uuid
from sqlmodel import Session, select, col, or_

from app.models.cache import Transcript
from app.models.auth import User

logger = logging.getLogger(__name__)

class TranscriptCacheService:
    """
    Service for caching transcripts using SQLModel.
    """
    
    # Helper to parse JSON fields safely
    def _parse_json(self, json_str: Optional[str]) -> Any:
        if not json_str:
            return None
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return None

    def _to_dict(self, transcript: Transcript) -> Dict[str, Any]:
        """Convert Transcript model to dictionary with parsed JSON fields."""
        from app.services.file_storage_service import get_file_storage_service

        file_storage = get_file_storage_service()

        # Build dictionary explicitly to ensure all fields are included
        result = {
            'video_id': transcript.video_id,
            'user_id': transcript.user_id,
            'video_title': transcript.video_title,
            'author': transcript.author,
            'upload_date': transcript.upload_date,
            'transcript': transcript.transcript,
            'tokens_used': transcript.tokens_used,
            'is_cleaned': transcript.is_cleaned,
            'created_at': transcript.created_at,
            'last_accessed': transcript.last_accessed,
            'access_count': transcript.access_count,
            'analysis_date': transcript.analysis_date,
            'summary_date': transcript.summary_date,
            'manipulation_date': transcript.manipulation_date,
            'discovery_date': transcript.discovery_date,
            'health_observation_date': transcript.health_observation_date,
            'prompts_date': transcript.prompts_date,
            # Multi-source fields
            'source_type': transcript.source_type,
            'source_url': transcript.source_url,
            'file_path': transcript.file_path,
            'thumbnail_path': transcript.thumbnail_path,
            'thumbnail_url': file_storage.get_thumbnail_url(transcript.thumbnail_path),  # Convert path to URL
            'raw_content_text': transcript.raw_content_text,
            'word_count': transcript.word_count,
            'character_count': transcript.character_count,
            'page_count': transcript.page_count,
            # Content metadata for library filtering
            'content_type': transcript.content_type,
            'tldr': transcript.tldr,
        }

        # Parse JSON string fields back to dicts/lists
        result['transcript_data'] = self._parse_json(transcript.transcript_data)
        result['analysis_result'] = self._parse_json(transcript.analysis_result)
        result['summary_result'] = self._parse_json(transcript.summary_result)
        result['manipulation_result'] = self._parse_json(transcript.manipulation_result)
        result['discovery_result'] = self._parse_json(transcript.discovery_result)
        result['health_observation_result'] = self._parse_json(transcript.health_observation_result)
        result['prompts_result'] = self._parse_json(transcript.prompts_result)
        result['keywords'] = self._parse_json(transcript.keywords)

        return result

    def get(self, session: Session, video_id: str, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get a cached transcript by video ID and user ID.
        """
        # Build query
        # If user_id provided, filter by it. If not (e.g. system usage?), maybe allow?
        # For now, strict user scoping as per plan.
        query = select(Transcript).where(Transcript.video_id == video_id)
        if user_id:
            query = query.where(Transcript.user_id == user_id)
            
        transcript = session.exec(query).first()

        if transcript:
            # Update access stats
            transcript.last_accessed = datetime.utcnow()
            transcript.access_count += 1
            session.add(transcript)
            session.commit()
            
            logger.info(f"Cache hit for video {video_id}")
            return self._to_dict(transcript)

        logger.info(f"Cache miss for video {video_id}")
        return None

    def save(
        self,
        session: Session,
        video_id: str,
        video_title: str,
        transcript_text: str,
        user_id: str,
        author: Optional[str] = None,
        upload_date: Optional[str] = None,
        transcript_data: Optional[List[Dict]] = None,
        tokens_used: int = 0,
        is_cleaned: bool = False,
        # Multi-source support parameters
        source_type: str = "youtube",
        source_url: Optional[str] = None,
        file_path: Optional[str] = None,
        thumbnail_path: Optional[str] = None,
        raw_content_text: Optional[str] = None,
        word_count: int = 0,
        character_count: int = 0,
        page_count: Optional[int] = None
    ) -> bool:
        """
        Save or update content in the cache (videos, PDFs, etc.).

        Supports multi-source content types: youtube, pdf, web_url, plain_text.
        """
        try:
            # Check for existing
            query = select(Transcript).where(Transcript.video_id == video_id, Transcript.user_id == user_id)
            existing = session.exec(query).first()

            transcript_data_json = json.dumps(transcript_data) if transcript_data else None
            now = datetime.utcnow()

            # Calculate word_count if not provided and transcript exists
            if word_count == 0 and transcript_text:
                word_count = len(transcript_text.split())

            # Calculate character_count if not provided
            if character_count == 0 and transcript_text:
                character_count = len(transcript_text)

            if existing:
                existing.video_title = video_title
                existing.author = author
                existing.upload_date = upload_date
                existing.transcript = transcript_text
                existing.transcript_data = transcript_data_json
                existing.tokens_used = tokens_used
                existing.is_cleaned = is_cleaned
                existing.source_type = source_type
                existing.source_url = source_url
                existing.file_path = file_path
                existing.thumbnail_path = thumbnail_path
                existing.raw_content_text = raw_content_text
                existing.word_count = word_count
                existing.character_count = character_count
                existing.page_count = page_count
                existing.last_accessed = now
                existing.access_count += 1
                session.add(existing)
            else:
                new_transcript = Transcript(
                    video_id=video_id,
                    user_id=user_id,
                    video_title=video_title,
                    author=author,
                    upload_date=upload_date,
                    transcript=transcript_text,
                    transcript_data=transcript_data_json,
                    tokens_used=tokens_used,
                    is_cleaned=is_cleaned,
                    source_type=source_type,
                    source_url=source_url,
                    file_path=file_path,
                    thumbnail_path=thumbnail_path,
                    raw_content_text=raw_content_text,
                    word_count=word_count,
                    character_count=character_count,
                    page_count=page_count,
                    created_at=now,
                    last_accessed=now,
                    access_count=1
                )
                session.add(new_transcript)

            session.commit()
            logger.info(f"Saved transcript for video {video_id} to cache")
            return True

        except Exception as e:
            logger.error(f"Failed to save transcript to cache: {e}")
            return False

    def get_history(self, session: Session, user_id: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get transcript history for user."""
        query = select(Transcript).where(Transcript.user_id == user_id).order_by(Transcript.last_accessed.desc()).offset(offset).limit(limit)
        transcripts = session.exec(query).all()

        # Minimal data for history
        items = []
        for t in transcripts:
            item = self._to_dict(t)
            # Add 'has_X' flags
            item['has_analysis'] = bool(t.analysis_result)
            item['has_summary'] = bool(t.summary_result)
            item['has_manipulation'] = bool(t.manipulation_result)
            item['has_rhetorical'] = bool(t.analysis_result) # Mapped from analysis_result? Old code did this.
            item['has_discovery'] = bool(t.discovery_result)
            item['has_health'] = bool(t.health_observation_result)
            item['has_prompts'] = bool(t.prompts_result)

            # Extract keywords and other metadata from summary
            if item['summary_result']:
                summary = item['summary_result']
                item['keywords'] = summary.get('keywords', [])
                item['content_type'] = summary.get('content_type')
                item['tldr'] = summary.get('tldr')
            else:
                item['keywords'] = []
                item['content_type'] = None
                item['tldr'] = None

            items.append(item)

        return items

    def get_total_count(self, session: Session, user_id: str) -> int:
        """Get total number of cached transcripts for user."""
        # This is inefficient for large tables, but fine to start
        # Ideally use select(func.count())...
        # But for SQLModel/Pydantic, we can use standard count query
        # session.exec(select([func.count()]).where(...)).one()
        # For simplicity/speed without extra imports, checking logic.
        transcripts = session.exec(select(Transcript).where(Transcript.user_id == user_id)).all()
        return len(transcripts)

    def delete(self, session: Session, video_id: str, user_id: str) -> bool:
        """Delete a cached transcript."""
        try:
            transcript = session.exec(select(Transcript).where(Transcript.video_id == video_id, Transcript.user_id == user_id)).first()
            if transcript:
                session.delete(transcript)
                session.commit()
                logger.info(f"Deleted transcript {video_id} from cache")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete transcript: {e}")
            return False

    def clear_all(self, session: Session, user_id: str) -> bool:
        """Clear all cached transcripts for user."""
        try:
            transcripts = session.exec(select(Transcript).where(Transcript.user_id == user_id)).all()
            for t in transcripts:
                session.delete(t)
            session.commit()
            logger.info(f"Cleared all cached transcripts for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return False

    def search(self, session: Session, query_str: str, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search transcripts by title or content."""
        # Simple LIKE search
        query = select(Transcript).where(
            Transcript.user_id == user_id,
            or_(col(Transcript.video_title).contains(query_str), col(Transcript.transcript).contains(query_str))
        ).order_by(Transcript.last_accessed.desc()).limit(limit)

        transcripts = session.exec(query).all()

        # Convert to dict and add 'has_X' flags
        items = []
        for t in transcripts:
            item = self._to_dict(t)
            # Add 'has_X' flags
            item['has_analysis'] = bool(t.analysis_result)
            item['has_summary'] = bool(t.summary_result)
            item['has_manipulation'] = bool(t.manipulation_result)
            item['has_rhetorical'] = bool(t.analysis_result)
            item['has_discovery'] = bool(t.discovery_result)
            item['has_health'] = bool(t.health_observation_result)
            item['has_prompts'] = bool(t.prompts_result)

            # Extract keywords and metadata from summary
            if item['summary_result']:
                summary = item['summary_result']
                item['keywords'] = summary.get('keywords', [])
                item['content_type'] = summary.get('content_type')
                item['tldr'] = summary.get('tldr')
            else:
                item['keywords'] = []
                item['content_type'] = None
                item['tldr'] = None

            items.append(item)

        return items

    # Analysis helpers
    def save_analysis(self, session: Session, video_id: str, analysis_result: Dict[str, Any], user_id: str) -> bool:
        transcript = session.exec(select(Transcript).where(Transcript.video_id == video_id, Transcript.user_id == user_id)).first()
        if transcript:
            transcript.analysis_result = json.dumps(analysis_result)
            transcript.analysis_date = datetime.utcnow().isoformat()
            session.add(transcript)
            session.commit()
            return True
        return False

    def get_analysis(self, session: Session, video_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        transcript = session.exec(select(Transcript).where(Transcript.video_id == video_id, Transcript.user_id == user_id)).first()
        if transcript and transcript.analysis_result:
             return {
                 'analysis': self._parse_json(transcript.analysis_result),
                 'analysis_date': transcript.analysis_date
             }
        return None

    def save_summary(self, session: Session, video_id: str, summary_result: Dict[str, Any], user_id: str) -> bool:
        transcript = session.exec(select(Transcript).where(Transcript.video_id == video_id, Transcript.user_id == user_id)).first()
        if transcript:
            transcript.summary_result = json.dumps(summary_result)
            transcript.summary_date = datetime.utcnow().isoformat()

            # Extract metadata from summary for library filtering
            if isinstance(summary_result, dict):
                # Extract content type
                if 'content_type' in summary_result:
                    transcript.content_type = summary_result['content_type']

                # Extract keywords/tags
                if 'keywords' in summary_result:
                    transcript.keywords = json.dumps(summary_result['keywords']) if isinstance(summary_result['keywords'], list) else None
                elif 'tags' in summary_result:
                    transcript.keywords = json.dumps(summary_result['tags']) if isinstance(summary_result['tags'], list) else None

                # Extract TLDR
                if 'tldr' in summary_result:
                    transcript.tldr = summary_result['tldr']
                elif 'one_sentence_summary' in summary_result:
                    transcript.tldr = summary_result['one_sentence_summary']

            session.add(transcript)
            session.commit()
            return True
        return False

    def get_summary(self, session: Session, video_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        transcript = session.exec(select(Transcript).where(Transcript.video_id == video_id, Transcript.user_id == user_id)).first()
        if transcript and transcript.summary_result:
             return {
                 'summary': self._parse_json(transcript.summary_result),
                 'summary_date': transcript.summary_date
             }
        return None
    
    def save_manipulation(self, session: Session, video_id: str, manipulation_result: Dict[str, Any], user_id: str) -> bool:
        transcript = session.exec(select(Transcript).where(Transcript.video_id == video_id, Transcript.user_id == user_id)).first()
        if transcript:
            transcript.manipulation_result = json.dumps(manipulation_result)
            transcript.manipulation_date = datetime.utcnow().isoformat()
            session.add(transcript)
            session.commit()
            return True
        return False

    def get_manipulation(self, session: Session, video_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        transcript = session.exec(select(Transcript).where(Transcript.video_id == video_id, Transcript.user_id == user_id)).first()
        if transcript and transcript.manipulation_result:
             return {
                 'manipulation': self._parse_json(transcript.manipulation_result),
                 'manipulation_date': transcript.manipulation_date
             }
        return None
        
    def save_discovery(self, session: Session, video_id: str, discovery_result: Dict[str, Any], user_id: str) -> bool:
        transcript = session.exec(select(Transcript).where(Transcript.video_id == video_id, Transcript.user_id == user_id)).first()
        if transcript:
            transcript.discovery_result = json.dumps(discovery_result)
            transcript.discovery_date = datetime.utcnow().isoformat()
            session.add(transcript)
            session.commit()
            return True
        return False

    def get_discovery(self, session: Session, video_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        transcript = session.exec(select(Transcript).where(Transcript.video_id == video_id, Transcript.user_id == user_id)).first()
        if transcript and transcript.discovery_result:
             return {
                 'discovery': self._parse_json(transcript.discovery_result),
                 'discovery_date': transcript.discovery_date
             }
        return None
    
    def save_prompts(self, session: Session, video_id: str, prompts_result: Dict[str, Any], user_id: str) -> bool:
        transcript = session.exec(select(Transcript).where(Transcript.video_id == video_id, Transcript.user_id == user_id)).first()
        if transcript:
            transcript.prompts_result = json.dumps(prompts_result)
            transcript.prompts_date = datetime.utcnow().isoformat()
            session.add(transcript)
            session.commit()
            return True
        return False
        
    def get_prompts(self, session: Session, video_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        transcript = session.exec(select(Transcript).where(Transcript.video_id == video_id, Transcript.user_id == user_id)).first()
        if transcript and transcript.prompts_result:
             return {
                 'prompts': self._parse_json(transcript.prompts_result),
                 'prompts_date': transcript.prompts_date
             }
        return None

    def save_health_observation(self, session: Session, video_id: str, health_result: Dict[str, Any], user_id: str) -> bool:
        transcript = session.exec(select(Transcript).where(Transcript.video_id == video_id, Transcript.user_id == user_id)).first()
        if transcript:
            transcript.health_observation_result = json.dumps(health_result)
            transcript.health_observation_date = datetime.utcnow().isoformat()
            session.add(transcript)
            session.commit()
            return True
        return False

    def get_health_observation(self, session: Session, video_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        transcript = session.exec(select(Transcript).where(Transcript.video_id == video_id, Transcript.user_id == user_id)).first()
        if transcript and transcript.health_observation_result:
             return self._parse_json(transcript.health_observation_result)
        return None


    # FTS methods - skipped real impl for SQLModel for now unless we do raw SQL execution
    # For now, just a placeholder.
    def rebuild_fts_index(self):
        pass

    def advanced_search(self, session: Session, query: str, user_id: str, **kwargs) -> List[Dict[str, Any]]:
        # Simplified implementation using standard search
        return self.search(session, query, user_id)
        
    def get_all_tags(self, session: Session, limit: int = 100, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all unique tags/keywords from summaries with counts."""
        # Get all transcripts for the user (or all if no user specified)
        query = select(Transcript)
        if user_id:
            query = query.where(Transcript.user_id == user_id)

        transcripts = session.exec(query).all()

        # Collect all keywords with counts
        tag_counts: Dict[str, int] = {}
        for t in transcripts:
            if t.summary_result:
                summary = self._parse_json(t.summary_result)
                if summary and 'keywords' in summary:
                    for keyword in summary['keywords']:
                        tag_counts[keyword] = tag_counts.get(keyword, 0) + 1

        # Convert to list of dicts sorted by count
        tags = [{'tag': tag, 'count': count} for tag, count in tag_counts.items()]
        tags.sort(key=lambda x: x['count'], reverse=True)

        return tags[:limit]

    def get_content_type_counts(self, session: Session, user_id: Optional[str] = None) -> Dict[str, int]:
        """Get content type distribution."""
        query = select(Transcript)
        if user_id:
            query = query.where(Transcript.user_id == user_id)

        transcripts = session.exec(query).all()

        # Count content types
        type_counts: Dict[str, int] = {}
        for t in transcripts:
            if t.summary_result:
                summary = self._parse_json(t.summary_result)
                if summary and 'content_type' in summary:
                    content_type = summary['content_type']
                    if content_type:
                        type_counts[content_type] = type_counts.get(content_type, 0) + 1

        return type_counts
        
    def get_stats(self, session: Session, user_id: str) -> Dict[str, int]:
         transcripts = session.exec(select(Transcript).where(Transcript.user_id == user_id)).all()
         total = len(transcripts)
         with_summary = sum(1 for t in transcripts if t.summary_result)
         with_analysis = sum(1 for t in transcripts if t.analysis_result)
         
         return {
             "total": total,
             "with_summary": with_summary,
             "with_analysis": with_analysis
         }

# Singleton instance for dependency? No, now we want stateless.
# But keeping the class stateless allows simple instantiation.
cache_service = TranscriptCacheService()

def get_cache_service() -> TranscriptCacheService:
    return cache_service
