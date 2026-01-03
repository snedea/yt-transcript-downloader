from typing import Generator
from sqlmodel import create_engine, Session
from .config import settings

# Use DB_PATH from environment or default to local data directory
# Note: config.py doesn't currently export DB_PATH, so we might need to update config.py
# or import the logic. For now, we will duplicate the logic slightly or use a direct env var,
# but ideally we should update Settings in config.py.
# However, to avoid circular imports or complex refactors right now, we'll follow 
# the pattern in cache_service.py but move it here.

import os
from pathlib import Path

_default_db_path = Path(__file__).parent.parent / "data" / "transcripts.db"
DB_PATH = Path(os.getenv("DB_PATH", str(_default_db_path)))
sqlite_url = f"sqlite:///{DB_PATH}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
