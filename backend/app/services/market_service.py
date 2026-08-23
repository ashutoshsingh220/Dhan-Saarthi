import json
import logging
import os
from datetime import datetime, timezone, timedelta
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.market import MarketSnapshot
from app.models.user import User
from app.providers.market_data_provider import AlphaVantageMarketDataProvider, PublicMarketDataProvider
from app.schemas.market import (
    FreshnessType,
    MarketAssetSchema,
    MarketOverviewResponse,
)
from app.services.market_insight_service import MarketInsightService
from app.services.personalization_service import build_personalization_context


logger = logging.getLogger(__name__)

MARKET_CACHE_TTL_SECONDS = int(os.getenv("MARKET_CACHE_TTL_SECONDS", "300"))

# Global in-memory cache structure
_CACHE = {
    "snapshot": None,
    "fetched_at": None,
    "freshness": "UNAVAILABLE",
    "source": "NONE"
}

class MarketService:
    """
    Main Service for Managing Market Intelligence, Alpha Vantage API Caching, and Insights.
    """

    @staticmethod
    def get_market_overview(db: Session, user: User | None = None, force_refresh: bool = False) -> MarketOverviewResponse:
        """
        Fetch market overview with in-memory caching (300s TTL), DB snapshot fallback, and explanation level adaptation.
        """
        now = datetime.now(timezone.utc)
        cache_valid = False

        if not force_refresh and _CACHE["snapshot"] is not None and _CACHE["fetched_at"] is not None:
            age_seconds = (now - _CACHE["fetched_at"]).total_seconds()
            if age_seconds < MARKET_CACHE_TTL_SECONDS:
                cache_valid = True
                logger.info(f"Serving market data from IN_MEMORY_CACHE (TTL: {MARKET_CACHE_TTL_SECONDS}s, age: {age_seconds:.1f}s, source: {_CACHE['source']}, freshness: {_CACHE['freshness']}, fetched_at: {_CACHE['fetched_at'].isoformat()})")

        if not cache_valid:
            logger.info(f"Cache miss or force_refresh requested (force_refresh={force_refresh}). Fetching fresh market data snapshot...")
            provider = AlphaVantageMarketDataProvider()
            raw_assets, source_name, is_live = provider.fetch_market_snapshot()

            if not is_live:
                logger.info("Alpha Vantage provider returned fallback snapshot. Attempting PublicMarketDataProvider for live public market data...")
                public_provider = PublicMarketDataProvider()
                raw_assets, source_name, is_live = public_provider.fetch_market_snapshot()

            if is_live:
                freshness: FreshnessType = "LIVE"
            else:
                freshness: FreshnessType = "STALE"


            assets_list = []
            now_str = now.isoformat()
            for key, item in raw_assets.items():
                asset_obj = MarketAssetSchema(
                    symbol=item["symbol"],
                    display_name=item["display_name"],
                    asset_type=item["asset_type"],
                    current_price=item["current_price"],
                    currency=item.get("currency", "INR"),
                    absolute_change=item["absolute_change"],
                    percentage_change=item["percentage_change"],
                    direction=item["direction"],
                    market_status=item.get("market_status", "OPEN"),
                    updated_at=now_str,
                    source=source_name,
                )
                assets_list.append(asset_obj)

            pulse, pulse_summary = MarketInsightService.calculate_market_pulse(assets_list)
            logger.info(f"Market snapshot evaluated: source={source_name}, is_live={is_live}, freshness={freshness}, pulse={pulse}, fetched_at={now_str}")

            try:
                assets_json_str = json.dumps([a.model_dump() for a in assets_list])
                snapshot = MarketSnapshot(
                    source=source_name,
                    freshness=freshness,
                    market_pulse=pulse,
                    pulse_summary=pulse_summary,
                    assets_json=assets_json_str,
                    insights_json="[]",
                    fetched_at=now,
                )
                db.add(snapshot)
                db.commit()
            except Exception as ex:
                db.rollback()
                logger.warning(f"Failed to persist MarketSnapshot to DB: {ex}")

            _CACHE["snapshot"] = {
                "assets": assets_list,
                "pulse": pulse,
                "pulse_summary": pulse_summary,
            }
            _CACHE["fetched_at"] = now
            _CACHE["freshness"] = freshness
            _CACHE["source"] = source_name


        explanation_level = "SIMPLE"
        if user and user.profile:
            pctx = build_personalization_context(user.profile, language=getattr(user, "preferred_language", "English"))
            explanation_level = pctx.get("communication_level", "SIMPLE")



        cached_assets = _CACHE["snapshot"]["assets"]
        pulse = _CACHE["snapshot"]["pulse"]
        pulse_summary = _CACHE["snapshot"]["pulse_summary"]

        insights = MarketInsightService.generate_market_insights(cached_assets, explanation_level=explanation_level)

        fetched_at_str = _CACHE["fetched_at"].isoformat() if _CACHE["fetched_at"] else now.isoformat()
        is_stale = _CACHE["freshness"] in ["STALE", "UNAVAILABLE"]

        return MarketOverviewResponse(
            market_pulse=pulse,
            pulse_summary=pulse_summary,
            freshness=_CACHE["freshness"],
            is_stale=is_stale,
            fetched_at=fetched_at_str,
            source=_CACHE["source"],
            tracked_assets=cached_assets,
            insights=insights,
            explanation_level=explanation_level,
        )

    @staticmethod
    def get_asset_detail(db: Session, symbol: str, user: User | None = None) -> MarketAssetSchema | None:
        """Retrieve detailed information for a single symbol."""
        overview = MarketService.get_market_overview(db, user=user)
        sym_upper = symbol.upper()
        for asset in overview.tracked_assets:
            if asset.symbol.upper() == sym_upper:
                return asset
        return None
