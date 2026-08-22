# conftest.py — patch settings and engine before tests run, ensuring SQLite isolation.
# load_dotenv with override=True in config.py always wins over os.environ, so we must
# patch the already-instantiated Settings object and recreate the engine.
import os
import pytest

# Patch at import time so the session module uses SQLite when re-imported.
# This file is loaded by pytest before any test module.
os.environ["DATABASE_URL"] = "sqlite:///./test_dhan_saarthi.db"
os.environ["JWT_SECRET_KEY"] = "test-secret"
os.environ["JWT_ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "60"
os.environ["CORS_ALLOW_ORIGINS"] = "http://localhost:8081"
os.environ["GEMINI_API_KEY"] = "test-mock-gemini-key"

# Import and patch the settings singleton BEFORE any other test module imports it.
from app.core import config as _config
_config.settings.database_url = "sqlite:///./test_dhan_saarthi.db"
_config.settings.jwt_secret_key = "test-secret"
_config.settings.gemini_api_key = "test-mock-gemini-key"

# Re-create the engine and session factory using the patched URL.
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import app.db.session as _session

_test_engine = create_engine(
    "sqlite:///./test_dhan_saarthi.db",
    connect_args={"check_same_thread": False},
    pool_pre_ping=True,
)
_test_session = sessionmaker(autocommit=False, autoflush=False, bind=_test_engine)
_session.engine = _test_engine
_session.SessionLocal = _test_session
