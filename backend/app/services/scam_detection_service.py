import re
from typing import Dict, List, Tuple


class ScamDetectionService:
    # Rule definitions: (indicator_type, regex_pattern, points, severity)
    RULES: List[Tuple[str, str, int, str]] = [
        (
            "URGENCY_PRESSURE",
            r"\b(urgent|urgently|immediately|act now|today only|within 24 hours|last warning|final notice|expires? today|hurry|instant action)\b",
            10,
            "medium",
        ),
        (
            "FINANCIAL_THREAT",
            r"\b(account (is |will be )?(blocked|suspended)|account (blocked|suspended)|kyc (failure|expired|pending)|pan verification (failure|required)|card (is )?(blocked|suspended)|payment failed|legal action|unauthorized access|account deactivated)\b",
            15,
            "high",
        ),
        (
            "SUSPICIOUS_REWARD",
            r"\b(congratulations|you won|claim (your )?reward|cash prize|free money|guaranteed return|instant reward|lottery|jackpot|bonus credit)\b",
            10,
            "medium",
        ),
        (
            "SENSITIVE_INFO_REQUEST",
            r"\b(otp|pin|cvv|password|bank details|card number|aadhaar|aadhaar number|net banking password|secret pin|share credentials)\b",
            20,
            "critical",
        ),
        (
            "PAYMENT_REQUEST",
            r"\b(pay now|send money|transfer money|processing fee|verification fee|security deposit|send ₹|send rs|pay ₹|pay rs|deposit ₹|pay rupees)\b",
            20,
            "critical",
        ),
        (
            "SUSPICIOUS_URL",
            r"(https?://\S+|bit\.ly/\S+|tinyurl\.com/\S+|t\.co/\S+|is\.gd/\S+|cutt\.ly/\S+|goo\.gl/\S+|rb\.gy/\S+|\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b)",
            20,
            "high",
        ),
    ]

    # Impersonation keywords
    IMPERSONATION_PATTERN = r"\b(rbi|reserve bank|sbi|hdfc|icici|axis bank|bank support|customer care|income tax|income tax department|police|cyber crime|government|wallet support|paytm|phonepe|gpay)\b"

    @classmethod
    def analyze(cls, text: str) -> Dict:
        normalized_text = text.lower()
        indicators = []
        indicator_types_found = set()
        raw_score = 0

        # Check standard rules
        for ind_type, pattern, points, severity in cls.RULES:
            match = re.search(pattern, normalized_text, re.IGNORECASE)
            if match:
                matched_str = match.group(0)
                indicators.append({
                    "indicator_type": ind_type,
                    "matched_text": matched_str,
                    "severity": severity,
                    "points": points,
                })
                indicator_types_found.add(ind_type)
                raw_score += points

        # Check Impersonation (only increases risk if combined with threat, urgency, sensitive info, payment, or URL)
        imp_match = re.search(cls.IMPERSONATION_PATTERN, normalized_text, re.IGNORECASE)
        if imp_match and len(indicator_types_found) > 0:
            indicators.append({
                "indicator_type": "IMPERSONATION",
                "matched_text": imp_match.group(0),
                "severity": "high",
                "points": 15,
            })
            indicator_types_found.add("IMPERSONATION")
            raw_score += 15

        # Escalation bonus if 3+ distinct indicator types detected
        if len(indicator_types_found) >= 3:
            raw_score += 10

        # Cap score at 100
        risk_score = min(100, max(0, raw_score))

        # Classify risk level
        if risk_score >= 75:
            risk_level = "CRITICAL"
        elif risk_score >= 50:
            risk_level = "HIGH"
        elif risk_score >= 25:
            risk_level = "MODERATE"
        else:
            risk_level = "LOW"

        # Generate recommendations deterministically
        recommendations = cls._generate_recommendations(indicator_types_found, risk_level)

        # Generate summary deterministically
        summary = cls._generate_summary(risk_score, risk_level, indicator_types_found)

        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "indicators": indicators,
            "recommended_actions": recommendations,
            "summary": summary,
        }

    @classmethod
    def _generate_recommendations(cls, types_found: set, risk_level: str) -> List[str]:
        recs = []
        if "SENSITIVE_INFO_REQUEST" in types_found:
            recs.append("Do not share OTP, PIN, CVV, passwords, or banking credentials under any circumstances.")
        if "SUSPICIOUS_URL" in types_found:
            recs.append("Do not tap or open links in unverified messages. Access your bank only through its official app or website.")
        if "URGENCY_PRESSURE" in types_found:
            recs.append("Do not act under pressure or hurry. Legitimate financial institutions provide official notice periods.")
        if "PAYMENT_REQUEST" in types_found:
            recs.append("Do not send money or processing fees to claim rewards, unblock accounts, or verify KYC.")
        if "IMPERSONATION" in types_found or "FINANCIAL_THREAT" in types_found:
            recs.append("Verify the claim independently by contacting your bank using the official phone number on your debit card or official bank website.")

        if risk_level in ["HIGH", "CRITICAL"] and len(recs) < 3:
            recs.append("Exercise extreme caution before taking any action or responding to this message.")

        if not recs:
            recs.append("No obvious high-risk financial scam indicators detected. Always verify suspicious requests through official banking apps or websites.")

        return recs

    @classmethod
    def _generate_summary(cls, score: int, level: str, types_found: set) -> str:
        if level == "LOW":
            return "This message appears to be low risk. No major suspicious financial scam indicators were detected."
        
        ind_names = [t.replace("_", " ").title() for t in types_found]
        ind_str = ", ".join(ind_names) if ind_names else "suspicious patterns"
        
        if level == "CRITICAL":
            return f"CRITICAL SCAM RISK (Score {score}/100): This message exhibits severe fraudulent indicators including {ind_str}. Do not take action."
        elif level == "HIGH":
            return f"HIGH RISK WARNING (Score {score}/100): This message contains multiple suspicious scam signals ({ind_str}). Proceed with caution."
        else:
            return f"MODERATE RISK (Score {score}/100): This message includes potential risk indicators ({ind_str}). Verify before taking action."
