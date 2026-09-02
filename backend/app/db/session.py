from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

options = {"pool_pre_ping": True}
if settings.database_url.startswith("sqlite"):
    options["connect_args"] = {"check_same_thread": False}
else:
    # High-load connection pool settings for PostgreSQL
    options["pool_size"] = 20
    options["max_overflow"] = 30

engine = create_engine(settings.database_url, **options)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
