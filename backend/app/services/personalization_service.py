from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import UserProfile

EDUCATION_LEVELS = frozenset({
    'PRIMARY_OR_BELOW','SECONDARY','HIGHER_SECONDARY','DIPLOMA',
    'UNDERGRADUATE','POSTGRADUATE','DOCTORATE','OTHER','PREFER_NOT_TO_SAY',
})
FINANCIAL_KNOWLEDGE_LEVELS = frozenset({'BEGINNER','BASIC','INTERMEDIATE','ADVANCED'})
EXPLANATION_LEVELS = frozenset({'SIMPLE','BALANCED','DETAILED'})
OCCUPATION_STATUSES = frozenset({
    'STUDENT','SALARIED','SELF_EMPLOYED','BUSINESS_OWNER','FARMER',
    'HOMEMAKER','RETIRED','UNEMPLOYED','OTHER','PREFER_NOT_TO_SAY',
})

def calculate_age(dob: date, today: date | None = None) -> int:
    if today is None:
        today = date.today()
    birthday_occurred = (today.month, today.day) >= (dob.month, dob.day)
    return today.year - dob.year - (0 if birthday_occurred else 1)

_RESPONSE_RULES: dict[str, list[str]] = {
    'SIMPLE': [
        'Use short sentences.',
        'Explain one concept at a time.',
        'Avoid unexplained jargon.',
        'Define necessary financial terms before using them.',
        'Use practical, everyday examples.',
        'Prefer step-by-step guidance.',
        'Do not assume prior financial knowledge.',
    ],
    'BALANCED': [
        'Use standard financial terminology.',
        'Briefly explain important terms when first introduced.',
        'Include practical context and real-world examples.',
        'Avoid unnecessary technical detail.',
        'Assume basic financial awareness (savings, budgeting, income).',
    ],
    'DETAILED': [
        'Allow deeper, structured explanation.',
        'Include assumptions and reasoning when useful.',
        'Explain formulas or calculations when relevant.',
        'Use structured comparisons and trade-offs where appropriate.',
        'Technical terminology is acceptable; define specialized terms.',
        'Assume comfort with common financial products and investing concepts.',
    ],
}
_DEFAULT_EXPLANATION_LEVEL = 'BALANCED'

def _life_stage_context(age: int | None) -> str:
    if age is None:
        return 'Life stage: unavailable'
    if age < 22:
        return 'Life stage: early adulthood — examples related to education funding and first savings steps may be relevant'
    if age < 35:
        return 'Life stage: early career — examples related to starting savings, building emergency funds, and first investments may be relevant'
    if age < 50:
        return 'Life stage: mid-career — examples related to wealth accumulation, home ownership, and family financial planning may be relevant'
    if age < 60:
        return 'Life stage: pre-retirement — examples related to retirement corpus building and insurance planning may be relevant'
    return 'Life stage: retirement/senior — examples related to cash-flow stability, medical expenses, and estate planning may be relevant'

def _occupation_context(occupation_status: str | None) -> str:
    if not occupation_status or occupation_status == 'PREFER_NOT_TO_SAY':
        return 'Occupation context: unavailable'
    labels = {
        'STUDENT': 'Student — examples related to education budgeting and early savings goals may be relevant',
        'SALARIED': 'Salaried employee — examples related to salary-based savings and benefits may be relevant',
        'SELF_EMPLOYED': 'Self-employed — examples related to variable income planning may be relevant',
        'BUSINESS_OWNER': 'Business owner — examples related to business-personal finance separation may be relevant',
        'FARMER': 'Farmer — examples related to seasonal income cycles may be relevant in future prompts',
        'HOMEMAKER': 'Homemaker — examples related to household budget management may be relevant',
        'RETIRED': 'Retired — examples related to fixed income, pensions, and cash-flow may be relevant',
        'UNEMPLOYED': 'Currently unemployed — examples related to emergency funds and expense reduction may be relevant',
        'OTHER': 'Occupation: other',
    }
    return labels.get(occupation_status, f'Occupation: {occupation_status}')

def _education_context(education_level: str | None) -> str:
    if not education_level or education_level == 'PREFER_NOT_TO_SAY':
        return 'Education context: unavailable'
    labels = {
        'PRIMARY_OR_BELOW': 'Education: Primary or below',
        'SECONDARY': 'Education: Secondary',
        'HIGHER_SECONDARY': 'Education: Higher Secondary',
        'DIPLOMA': 'Education: Diploma',
        'UNDERGRADUATE': 'Education: Undergraduate',
        'POSTGRADUATE': 'Education: Postgraduate',
        'DOCTORATE': 'Education: Doctorate',
        'OTHER': 'Education: Other',
    }
    return labels.get(education_level, f'Education: {education_level}')

def build_personalization_context(profile: 'UserProfile', language: str = 'English') -> dict:
    derived_age: int | None = None
    if profile.date_of_birth is not None:
        derived_age = calculate_age(profile.date_of_birth)
    explanation_level = profile.preferred_explanation_level or _DEFAULT_EXPLANATION_LEVEL
    if explanation_level not in EXPLANATION_LEVELS:
        explanation_level = _DEFAULT_EXPLANATION_LEVEL
    financial_knowledge = profile.financial_knowledge_level or 'BASIC'
    if financial_knowledge not in FINANCIAL_KNOWLEDGE_LEVELS:
        financial_knowledge = 'BASIC'
    return {
        'age': derived_age,
        'life_stage_context': _life_stage_context(derived_age),
        'education_context': _education_context(profile.education_level),
        'occupation_context': _occupation_context(profile.occupation_status),
        'financial_knowledge_level': financial_knowledge,
        'communication_level': explanation_level,
        'language_preference': language,
        'response_rules': _RESPONSE_RULES[explanation_level],
    }
