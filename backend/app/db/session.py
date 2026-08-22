from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

options = {"pool_pre_ping": True}
if settings.database_url.startswith("sqlite"):
    options["connect_args"] = {"check_same_thread": False}
engine = create_engine(settings.database_url, **options)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
