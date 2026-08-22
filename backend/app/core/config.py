import os
from pathlib import Path

from dotenv import load_dotenv

environment_directory = Path(__file__).resolve().parents[2]
load_dotenv(environment_directory / ".env")
# Local overrides are ignored by Git and take precedence over shared defaults.
load_dotenv(environment_directory / ".env.local", override=True)


class Settings:
    database_url = os.getenv("DATABASE_URL", "postgresql+psycopg://dhan_saarthi:change_me@localhost:5432/dhan_saarthi")
    jwt_secret_key = os.getenv("JWT_SECRET_KEY", "local-development-secret-change-me")
    jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    cors_allow_origins = [item.strip() for item in os.getenv("CORS_ALLOW_ORIGINS", "http://localhost:8081").split(",") if item.strip()]
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    alpha_vantage_api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    market_cache_ttl_seconds = int(os.getenv("MARKET_CACHE_TTL_SECONDS", "300"))


settings = Settings()

