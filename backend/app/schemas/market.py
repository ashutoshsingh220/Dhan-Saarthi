from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field

DirectionType = Literal["UP", "DOWN", "FLAT", "UNAVAILABLE"]
FreshnessType = Literal["LIVE", "CACHED", "STALE", "UNAVAILABLE"]
PulseType = Literal["POSITIVE", "NEGATIVE", "MIXED", "CALM", "UNAVAILABLE"]
MarketStatusType = Literal["OPEN", "CLOSED", "PRE_MARKET", "POST_MARKET", "UNKNOWN"]

class MarketAssetSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    symbol: str
    display_name: str
    asset_type: str  # EQUITY_INDEX, COMMODITY, CURRENCY
    current_price: float
    currency: str = "INR"
    absolute_change: float
    percentage_change: float
    direction: DirectionType
    market_status: MarketStatusType = "UNKNOWN"
    updated_at: str
    source: str = "YAHOO_FINANCE"

class MarketInsightSchema(BaseModel):
    title: str
    observation: str
    educational_note: str

class MarketOverviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    market_pulse: PulseType
    pulse_summary: str
    freshness: FreshnessType
    is_stale: bool
    fetched_at: str
    source: str
    tracked_assets: list[MarketAssetSchema] = Field(default_factory=list)
    insights: list[MarketInsightSchema] = Field(default_factory=list)
    explanation_level: str = "SIMPLE"
    disclaimer: str = (
        "Market information is for awareness and educational purposes only. "
        "Prices may be delayed and can change rapidly. Past performance does not guarantee future returns. "
        "Dhan Saarthi does not execute trades or guarantee financial returns."
    )
