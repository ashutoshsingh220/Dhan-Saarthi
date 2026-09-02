import json
import logging
import math
from typing import Dict, List, Optional
from google import genai

from app.core.config import settings

logger = logging.getLogger(__name__)

# Lightweight in-memory RAG Knowledge Base
SCAM_KNOWLEDGE_BASE = [
    {
        "id": "skb-001",
        "category": "OTP Phishing",
        "title": "Account Blocking Threat",
        "description": "Scammers claim your bank account will be blocked today unless you verify KYC via an OTP or link.",
        "example": "Dear Customer, your SBI account will be blocked today. Please update your PAN/KYC immediately by clicking here http://fake-link and share OTP.",
        "risk_indicators": ["Urgency", "Financial Threat", "Link", "OTP request"],
        "recommended_action": "Do not click the link or share OTP. Contact your bank directly using the official number.",
        "is_scam": True
    },
    {
        "id": "skb-002",
        "category": "Fake Customer Care",
        "title": "Refund / Technical Support Scam",
        "description": "Fraudsters pretend to be customer support for a wallet or bank and ask you to download a remote access app to process a refund.",
        "example": "For Paytm refund support, please call our toll-free number immediately. Do not share your PIN.",
        "risk_indicators": ["Impersonation", "Urgency"],
        "recommended_action": "Never search for customer care numbers on Google. Only use the official app to contact support.",
        "is_scam": True
    },
    {
        "id": "skb-003",
        "category": "UPI Collect Request",
        "title": "Fake Payment Receipt / OLX Scam",
        "description": "Scammers tell you to enter your UPI PIN to 'receive' money, often on platforms like OLX.",
        "example": "To receive your payment of Rs 5000, please open PhonePe and enter your UPI PIN to accept the cash transfer.",
        "risk_indicators": ["UPI PIN request", "Receiving money", "Payment request"],
        "recommended_action": "You NEVER need to enter a UPI PIN to receive money. Only enter a PIN when sending money.",
        "is_scam": True
    },
    {
        "id": "skb-004",
        "category": "Legitimate Notification",
        "title": "Standard Bank Transaction",
        "description": "A normal SMS sent by banks when a transaction occurs on your account.",
        "example": "Your A/c XX1234 is credited with INR 50,000.00 on 10-Oct-23. Info: NEFT. Available Bal INR 1,50,000.00.",
        "risk_indicators": [],
        "recommended_action": "This is a standard notification. No action required.",
        "is_scam": False
    },
    {
        "id": "skb-005",
        "category": "Job / Task Scam",
        "title": "Part-Time Job WhatsApp Scam",
        "description": "Fraudsters offer part-time jobs liking YouTube videos, then ask for a 'security deposit' or 'prepaid task fee'.",
        "example": "Earn Rs 3000 daily working from home! Just like 3 YouTube videos. Pay a small registration fee of Rs 500 to start.",
        "risk_indicators": ["Easy money", "Advance fee", "WhatsApp job"],
        "recommended_action": "Block the number. Legitimate jobs do not ask you to pay money to work.",
        "is_scam": True
    },
    {
        "id": "skb-006",
        "category": "Legitimate Notification",
        "title": "Monthly Account Statement",
        "description": "A normal bank email or SMS indicating that a monthly statement is ready to view.",
        "example": "Your monthly bank statement for September is ready. You can view it securely through the official HDFC banking application.",
        "risk_indicators": [],
        "recommended_action": "This is a standard informational message. View your statement in your official app.",
        "is_scam": False
    },
    {
        "id": "skb-007",
        "category": "Loan Fraud",
        "title": "Unsolicited Pre-Approved Loan",
        "description": "Messages offering instant cash or zero-file-charge loans with a link to download an unverified APK.",
        "example": "Congratulations! You are pre-approved for an instant loan of Rs 2 Lakhs. Zero file charges. Click here to download app and get funds today.",
        "risk_indicators": ["Suspicious Reward", "Unsolicited Loan", "Urgency"],
        "recommended_action": "Do not download apps from SMS links. Only use RBI-registered official lending apps from the Play Store.",
        "is_scam": True
    }
]

class ScamRagService:
    def __init__(self):
        self._embeddings_cache: Dict[str, List[float]] = {}
        self._client = None
        if settings.gemini_api_key and not settings.gemini_api_key.startswith("replace_"):
            self._client = genai.Client(api_key=settings.gemini_api_key)
        
        self._is_initialized = False

    def _get_embedding(self, text: str) -> List[float]:
        """Fetch embedding from Gemini."""
        if not self._client:
            return []
        try:
            response = self._client.models.embed_content(
                model='text-embedding-004',
                contents=text,
            )
            return response.embeddings[0].values
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            return []

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        mag1 = math.sqrt(sum(a * a for a in vec1))
        mag2 = math.sqrt(sum(b * b for b in vec2))
        
        if mag1 == 0 or mag2 == 0:
            return 0.0
        return dot_product / (mag1 * mag2)

    def _initialize_index(self):
        """Lazy load embeddings for the knowledge base."""
        if self._is_initialized or not self._client:
            return
        
        logger.info("Initializing Scam RAG embeddings...")
        for item in SCAM_KNOWLEDGE_BASE:
            text_to_embed = f"Category: {item['category']}. Title: {item['title']}. Description: {item['description']}. Example: {item['example']}"
            embedding = self._get_embedding(text_to_embed)
            if embedding:
                self._embeddings_cache[item['id']] = embedding
        
        self._is_initialized = True

    def retrieve_similar_pattern(self, query: str, top_k: int = 1, threshold: float = 0.65) -> List[Dict]:
        """Retrieve the most semantically similar scam pattern from the KB."""
        if not self._is_initialized:
            self._initialize_index()
            
        if not self._embeddings_cache:
            return [] # Fallback if embeddings failed
            
        query_embedding = self._get_embedding(query)
        if not query_embedding:
            return []
            
        results = []
        for item in SCAM_KNOWLEDGE_BASE:
            item_emb = self._embeddings_cache.get(item['id'])
            if item_emb:
                score = self._cosine_similarity(query_embedding, item_emb)
                if score >= threshold:
                    results.append((score, item))
                    
        # Sort by similarity descending
        results.sort(key=lambda x: x[0], reverse=True)
        
        # Return top_k items
        return [item for score, item in results[:top_k]]

rag_service = ScamRagService()
