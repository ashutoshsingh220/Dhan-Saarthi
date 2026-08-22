import logging
from app.schemas.market import MarketAssetSchema, MarketInsightSchema, PulseType

logger = logging.getLogger(__name__)

class MarketInsightService:
    """
    100% Deterministic Market Insight & Pulse Evaluation Engine.
    No LLM is used for numerical calculations or observation generation.
    """

    @staticmethod
    def calculate_market_pulse(assets: list[MarketAssetSchema]) -> tuple[PulseType, str]:
        if not assets:
            return "UNAVAILABLE", "Market data is currently unavailable."

        up_count = sum(1 for a in assets if a.direction == "UP")
        down_count = sum(1 for a in assets if a.direction == "DOWN")
        flat_count = sum(1 for a in assets if a.direction == "FLAT")
        total = len(assets)

        avg_pct = sum(a.percentage_change for a in assets) / total if total > 0 else 0.0

        if abs(avg_pct) < 0.1 and flat_count >= 3:
            pulse = "CALM"
            summary = "Market movements across tracked assets are calm with minimal price fluctuations today."
        elif up_count >= 3:
            pulse = "POSITIVE"
            summary = "Indian equity and commodity markets show positive upward momentum today."
        elif down_count >= 3:
            pulse = "NEGATIVE"
            summary = "Tracked Indian market assets are experiencing downward price pressure today."
        else:
            pulse = "MIXED"
            summary = "Tracked assets show mixed performance today with selective gains and losses."

        return pulse, summary

    @staticmethod
    def generate_market_insights(
        assets: list[MarketAssetSchema],
        explanation_level: str = "SIMPLE"
    ) -> list[MarketInsightSchema]:
        if not assets:
            return []

        asset_map = {a.symbol: a for a in assets}
        nifty = asset_map.get("NIFTY50")
        sensex = asset_map.get("SENSEX")
        gold = asset_map.get("GOLD")
        silver = asset_map.get("SILVER")
        usdinr = asset_map.get("USDINR")

        insights = []

        # 1. Equity Market Insight
        if nifty and sensex:
            if nifty.direction == "UP" and sensex.direction == "UP":
                if explanation_level == "SIMPLE":
                    obs = f"Both NIFTY 50 (up {nifty.percentage_change}%) and SENSEX (up {sensex.percentage_change}%) are moving upward today."
                    note = "When major stock market indices go up, it indicates overall positive growth in top Indian companies."
                elif explanation_level == "DETAILED":
                    obs = f"Equity market benchmarks NIFTY 50 (+{nifty.percentage_change}%) and SENSEX (+{sensex.percentage_change}%) reflect positive market sentiment."
                    note = "Index gains reflect broader buying activity across large-cap Indian stocks relative to previous close."
                else:  # BALANCED
                    obs = f"Indian stock market indices NIFTY 50 (+{nifty.percentage_change}%) and SENSEX (+{sensex.percentage_change}%) are trading higher today."
                    note = "Rising stock indices generally signal positive investor confidence in major listed businesses."
                insights.append(MarketInsightSchema(
                    title="Stock Market Benchmarks",
                    observation=obs,
                    educational_note=note
                ))
            elif nifty.direction == "DOWN" and sensex.direction == "DOWN":
                if explanation_level == "SIMPLE":
                    obs = f"NIFTY 50 (down {nifty.percentage_change}%) and SENSEX (down {sensex.percentage_change}%) have declined today."
                    note = "Market declines are normal economic fluctuations and do not mean permanent loss if you invest long term."
                else:
                    obs = f"Equity benchmarks NIFTY 50 ({nifty.percentage_change}%) and SENSEX ({sensex.percentage_change}%) show downward trends today."
                    note = "Short-term equity pullbacks occur due to profit booking or global economic cues."
                insights.append(MarketInsightSchema(
                    title="Stock Market Benchmarks",
                    observation=obs,
                    educational_note=note
                ))
            else:
                insights.append(MarketInsightSchema(
                    title="Stock Market Benchmarks",
                    observation=f"NIFTY 50 ({nifty.percentage_change}%) and SENSEX ({sensex.percentage_change}%) are showing divergent trends today.",
                    educational_note="Divergent index movements indicate mixed stock performance across sector leaders."
                ))

        # 2. Precious Metals Insight
        if gold and silver:
            if gold.direction == silver.direction and gold.direction != "FLAT":
                action = "gaining" if gold.direction == "UP" else "declining"
                if explanation_level == "SIMPLE":
                    obs = f"Precious metals Gold ({gold.percentage_change}%) and Silver ({silver.percentage_change}%) are both {action} today."
                    note = "Gold and Silver are traditional store-of-value assets often used as a hedge during economic uncertainty."
                else:
                    obs = f"Commodity track shows Gold ({gold.percentage_change}%) and Silver ({silver.percentage_change}%) moving in tandem."
                    note = "Precious metals reflect global inflation expectations, currency strength, and central bank demand."
                insights.append(MarketInsightSchema(
                    title="Gold & Silver Trends",
                    observation=obs,
                    educational_note=note
                ))
            else:
                if explanation_level == "SIMPLE":
                    obs = f"Gold price ({gold.percentage_change}%) and Silver price ({silver.percentage_change}%) are moving in different directions today."
                    note = "Gold is primarily seen as a safe-haven asset, while Silver also has industrial demand applications."
                else:
                    obs = f"Precious metals display mixed movement with Gold at {gold.current_price} INR and Silver at {silver.current_price} INR."
                    note = "Gold and silver prices respond to international spot prices and Indian Rupee exchange rates."
                insights.append(MarketInsightSchema(
                    title="Gold & Silver Trends",
                    observation=obs,
                    educational_note=note
                ))

        # 3. Currency Insight
        if usdinr:
            if explanation_level == "SIMPLE":
                obs = f"The US Dollar to Indian Rupee exchange rate is at ₹{usdinr.current_price} ({usdinr.direction})."
                note = "A stronger USD makes imports like crude oil pricier, while a stronger INR lowers import costs."
            else:
                obs = f"USD/INR currency pair is trading at ₹{usdinr.current_price} ({usdinr.percentage_change}%)."
                note = "Rupee valuation is influenced by foreign institutional investments, trade deficit, and global USD strength."
            insights.append(MarketInsightSchema(
                title="Currency & Foreign Exchange",
                observation=obs,
                educational_note=note
            ))

        return insights
