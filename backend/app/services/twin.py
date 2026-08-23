from app.models.user import UserProfile


def calculate_initial_twin(profile: UserProfile) -> tuple[int, str, str]:
    """Transparent deterministic Financial Twin score (0-100); it is not financial advice."""
    income = float(profile.monthly_income)
    expenses = float(profile.monthly_expenses)

    # Monthly savings vs Total accumulated savings
    monthly_savings = float(getattr(profile, "monthly_savings", None) or profile.savings or 0.0)
    total_savings = float(getattr(profile, "total_savings", None) or 0.0)

    # If total_savings is 0 but profile.savings exists from legacy record, use profile.savings as total_savings
    if total_savings == 0.0 and float(profile.savings or 0.0) > 0:
        total_savings = float(profile.savings)

    expense_ratio = expenses / income if income > 0 else 1.0
    surplus = max(income - expenses, 0.0)

    # Emergency buffer is calculated from Total Accumulated Savings
    savings_buffer = total_savings / expenses if expenses > 0 else 3.0

    score = 30
    # 1. Surplus / Income rating (up to 25 pts)
    score += min(25, round((surplus / income) * 25)) if income > 0 else 0

    # 2. Accumulated Liquid Savings Buffer (up to 30 pts)
    score += min(30, round((savings_buffer / 3.0) * 30))

    # 3. Risk preference alignment (up to 10 pts)
    score += {"low": 8, "moderate": 10, "high": 6}.get(profile.risk_preference, 0)

    # Bounds: 0 to 100
    score = max(0, min(100, score))
    risk = "Balanced" if profile.risk_preference == "moderate" else profile.risk_preference.capitalize()

    summary = (
        f"Your Financial Twin indicates ₹{surplus:,.0f} estimated monthly surplus (₹{monthly_savings:,.0f} reported monthly savings), "
        f"₹{total_savings:,.0f} in total accumulated savings (approx. {savings_buffer:.1f} months emergency buffer), "
        f"and age {profile.age}. Your primary goal is {profile.financial_goal}."
    )
    return score, risk, summary
