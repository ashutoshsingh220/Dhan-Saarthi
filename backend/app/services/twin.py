from app.models.user import UserProfile


def calculate_initial_twin(profile: UserProfile) -> tuple[int, str, str]:
    """Transparent prototype score only; it is not financial advice."""
    income, expenses, savings = float(profile.monthly_income), float(profile.monthly_expenses), float(profile.savings)
    expense_ratio = expenses / income if income else 1.0
    surplus = max(income - expenses, 0)
    savings_buffer = savings / expenses if expenses else 3.0
    score = 30 + min(25, round(surplus / income * 25) if income else 0) + min(30, round(savings_buffer / 3 * 30))
    score += {"low": 8, "moderate": 10, "high": 6}.get(profile.risk_preference, 0)
    score = max(0, min(100, score))
    risk = "Balanced" if profile.risk_preference == "moderate" else profile.risk_preference.capitalize()
    summary = f"Your prototype view shows ₹{surplus:,.0f} estimated monthly surplus, an expense ratio of {expense_ratio:.0%}, and a savings buffer of {savings_buffer:.1f} months. Your primary goal is {profile.financial_goal}."
    return score, risk, summary
