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
        }

        # Parse JSON string fields back to dicts/lists
        result['transcript_data'] = self._parse_json(transcript.transcript_data)
        result['analysis_result'] = self._parse_json(transcript.analysis_result)
        result['summary_result'] = self._parse_json(transcript.summary_result)
        result['manipulation_result'] = self._parse_json(transcript.manipulation_result)
        result['discovery_result'] = self._parse_json(transcript.discovery_result)
        result['health_observation_result'] = self._parse_json(transcript.health_observation_result)
        result['prompts_result'] = self._parse_json(transcript.prompts_result)

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
        is_cleaned: bool = False
    ) -> bool:
        """
        Save or update a transcript in the cache.
        """
        try:
            # Check for existing
            query = select(Transcript).where(Transcript.video_id == video_id, Transcript.user_id == user_id)
            existing = session.exec(query).first()
            
            transcript_data_json = json.dumps(transcript_data) if transcript_data else None
            now = datetime.utcnow()

            if existing:
                existing.video_title = video_title
                existing.author = author
                existing.upload_date = upload_date
                existing.transcript = transcript_text
                existing.transcript_data = transcript_data_json
                existing.tokens_used = tokens_used
                existing.is_cleaned = is_cleaned
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
        return [self._to_dict(t) for t in transcripts]

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
        
    def get_all_tags(self, session: Session, limit: int = 100) -> Dict[str, int]:
        return {} # Tags not implemented in new model yet
        
    def get_content_type_counts(self, session: Session) -> Dict[str, int]:
        return {}
        
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
