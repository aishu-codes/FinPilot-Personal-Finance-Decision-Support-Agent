"""
Smart SMS Transaction Agent & Fraud Detection Engine for FinPilot
Processes incoming SMS, extracts financial transaction details, detects scams/suspicious links,
sanitizes sensitive data (OTPs/PINs), and integrates with FinPilot categorization.
"""

import re
import uuid
from typing import Dict, Any, List, Tuple
from datetime import datetime

from backend.models.schemas import SMSLogItem, Transaction
from backend.engine.categorizer import categorize_transaction

# --- SECURITY & PRIVACY REDACTION ---
def sanitize_sensitive_info(text: str) -> str:
    """
    Redacts sensitive details such as OTPs, PINs, CVVs, and passwords from SMS text.
    """
    sanitized = text
    # Redact OTP / PIN numbers anywhere in sentence
    sanitized = re.sub(
        r'\b(otp|code|pin|cvv|one time password|secret)\b.*?\b(\d{4,8})\b',
        lambda m: m.group(0).replace(m.group(2), '******'),
        sanitized,
        flags=re.IGNORECASE
    )
    # Redact passwords
    sanitized = re.sub(r'\b(password|pwd)\s*(is\s*)?:?\s*(\S+)\b', r'\1: ******', sanitized, flags=re.IGNORECASE)
    return sanitized

# --- FRAUD & SUSPICIOUS MESSAGE DETECTION ---
def detect_fraud_and_scams(sms_text: str, sender: str = "") -> Tuple[float, List[str]]:
    """
    Analyzes SMS for phishing, fake bank alerts, suspicious URLs, and request for credentials.
    Returns (fraud_score: 0.0 to 1.0, suspicious_reasons: List[str]).
    """
    reasons = []
    fraud_score = 0.0
    text_lower = sms_text.lower()

    # 1. Suspicious / Non-standard URLs
    urls = re.findall(r'https?://[^\s]+|www\.[^\s]+|[a-zA-Z0-9-]+\.(?:xyz|top|club|info|link|site|work|click|cf|ga|ml|gq|tk|ru|cn)/[^\s]*', sms_text)
    if urls:
        for url in urls:
            if not any(trusted in url.lower() for trusted in ["hdfcbank.com", "icicibank.com", "sbi.co.in", "axisbank.com", "amazon.in", "paytm.com"]):
                reasons.append(f"Suspicious URL detected: {url[:30]}...")
                fraud_score += 0.45

    # 2. Urgent account-blocking / KYC expiry language
    urgent_keywords = ["account blocked", "account suspended", "kyc expired", "kyc update", "pan blocked", "deactivated within 24 hours", "click here to verify", "avoid disconnection"]
    for kw in urgent_keywords:
        if kw in text_lower:
            reasons.append(f"Urgent account-blocking or KYC threat language ('{kw}')")
            fraud_score += 0.40
            break

    # 3. Requests for OTP, PIN, CVV, or Password
    if any(k in text_lower for k in ["share otp", "tell your pin", "provide cvv", "send password", "verify otp"]):
        reasons.append("Requests user credentials (OTP / PIN / CVV)")
        fraud_score += 0.60

    # 4. Fake Cashback / Lottery / Prize Scams
    if any(k in text_lower for k in ["you won", "congratulations lottery", "claim cashback click", "free reward points", "refund approved click"]):
        if urls or "click" in text_lower or "link" in text_lower:
            reasons.append("Fake rewards, lottery or instant cashback claim scam")
            fraud_score += 0.50

    # 5. Sender anomaly check (e.g. standard 10-digit personal phone number sending bank claims)
    if sender and re.match(r'^\+?[0-9]{10,12}$', sender.strip()) and any(k in text_lower for k in ["bank", "account", "debited", "credited"]):
        reasons.append(f"Bank notification sent from personal phone number ({sender}) instead of official bank sender ID")
        fraud_score += 0.30

    fraud_score = min(1.0, round(fraud_score, 2))
    return fraud_score, reasons

# --- TRANSACTION INFORMATION EXTRACTION ---
def parse_and_extract_sms(sms_text: str) -> Dict[str, Any]:
    """
    Extracts structured transaction details from financial SMS.
    """
    text_lower = sms_text.lower()
    
    # 1. Extract Amount
    amount = 0.0
    amt_match = re.search(r'(?:rs\.?|inr|₹|usd|\$)\s*([\d,]+(?:\.\d{1,2})?)', sms_text, re.IGNORECASE)
    if not amt_match:
        amt_match = re.search(r'\b([\d,]+\.\d{2})\b', sms_text)
    
    if amt_match:
        try:
            clean_amt = amt_match.group(1).replace(',', '')
            amount = float(clean_amt)
        except ValueError:
            amount = 0.0

    # 2. Transaction Type & Mode Detection
    tx_type = "expense"
    payment_mode = "OTHER"
    is_failed = any(k in text_lower for k in ["failed", "declined", "unsuccessful", "reversed", "returned"])

    if any(k in text_lower for k in ["credited", "received", "deposited", "refunded", "cashback"]):
        tx_type = "income"
    elif any(k in text_lower for k in ["debited", "spent", "paid", "withdrawn", "purchase of", "charged", "sent to"]):
        tx_type = "expense"

    # Specific Payment Mode Checks
    if "atm" in text_lower and any(k in text_lower for k in ["withdraw", "withdrawn", "cash"]):
        payment_mode = "ATM"
        tx_type = "expense"
    elif "cash deposit" in text_lower or "cdm" in text_lower:
        payment_mode = "CASH"
        tx_type = "income"
    elif any(k in text_lower for k in ["upi", "vpa", "@okicici", "@ybl", "@upi", "gpay", "phonepe", "paytm"]):
        payment_mode = "UPI"
    elif any(k in text_lower for k in ["card", "debit card", "credit card", "visa", "mastercard"]):
        payment_mode = "CARD"
    elif any(k in text_lower for k in ["neft", "rtgs", "imps", "bank transfer", "a/c transfer"]):
        payment_mode = "BANK_TRANSFER"

    # 3. Extract Merchant / Payee
    merchant = "Unknown Merchant"
    merch_match = re.search(r'(?:to|at|for|from|vpa|info)\s+([A-Za-z0-9\s&\.\-\@]+?)(?=\s+(?:via|on|ref|avl|bal|a/c|date|link|\.|\,|$))', sms_text, re.IGNORECASE)
    if merch_match:
        m_str = merch_match.group(1).strip()
        if len(m_str) > 2 and not any(kw in m_str.lower() for kw in ["your a/c", "account", "bank account", "rs", "inr"]):
            merchant = m_str.title()
    
    if merchant == "Unknown Merchant":
        known_merchants = ["Amazon", "Swiggy", "Zomato", "Uber", "Ola", "Flipkart", "Starbucks", "Netflix", "Spotify", "Jio", "Airtel", "Chevron", "Costco", "Walmart", "Whole Foods"]
        for km in known_merchants:
            if km.lower() in text_lower:
                merchant = km
                break

    # 4. Bank Name Extraction
    bank = "Bank Account"
    banks = ["HDFC", "ICICI", "SBI", "Axis", "Kotak", "Citi", "PNB", "Bank of Baroda", "Canara", "Union Bank"]
    for b in banks:
        if b.lower() in text_lower:
            bank = f"{b} Bank"
            break

    # 5. Account / Card Last Digits
    card_last4 = None
    acct_match = re.search(r'(?:a/c|card|acct|ending)\s*(?:no\.?)?\s*x*(\d{3,4})', sms_text, re.IGNORECASE)
    if acct_match:
        card_last4 = acct_match.group(1)

    # 6. Reference ID / Txn ID Extraction
    reference_id = None
    ref_match = re.search(r'(?:ref|txn|rrn|upi ref|reference)\s*(?:no\.?|id)?\s*:?\s*([a-zA-Z0-9]{6,16})', sms_text, re.IGNORECASE)
    if ref_match:
        reference_id = ref_match.group(1)

    # 7. Calculate Confidence Score
    confidence = 0.0
    if amount > 0:
        confidence += 0.40
    if any(k in text_lower for k in ["debited", "credited", "spent", "paid", "withdrawn", "deposited", "received", "refunded"]):
        confidence += 0.30
    if merchant != "Unknown Merchant":
        confidence += 0.15
    if reference_id or card_last4 or payment_mode != "OTHER":
        confidence += 0.15

    confidence = round(confidence, 2)

    return {
        "amount": amount,
        "type": tx_type,
        "payment_mode": payment_mode,
        "merchant": merchant,
        "bank": bank,
        "card_last4": card_last4,
        "reference_id": reference_id,
        "confidence": confidence,
        "is_failed": is_failed
    }

# --- MAIN CLASSIFICATION & PROCESSING PIPELINE ---
def process_incoming_sms(sms_text: str, sender: str = "BANK-SMS", timestamp: str = None) -> SMSLogItem:
    """
    Full pipeline: Sanitize -> Fraud Check -> Transaction Extraction -> Categorization -> Classification.
    """
    sanitized_text = sanitize_sensitive_info(sms_text)
    fraud_score, suspicious_reasons = detect_fraud_and_scams(sms_text, sender)
    extracted = parse_and_extract_sms(sms_text)

    # Classification logic
    if fraud_score >= 0.35:
        status = "SUSPICIOUS"
    elif extracted["confidence"] >= 0.65 and not extracted["is_failed"]:
        status = "VERIFIED_TRANSACTION"
    elif extracted["amount"] > 0 and (extracted["confidence"] > 0.3 or "payment" in sms_text.lower()):
        status = "UNKNOWN"
    else:
        status = "NON_TRANSACTION"

    # Category determination using FinPilot categorizer
    cat = categorize_transaction(extracted["merchant"], extracted["amount"]) if extracted["amount"] > 0 else "Other"

    processed_date = timestamp if timestamp else datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    sms_item = SMSLogItem(
        id=f"sms_{uuid.uuid4().hex[:8]}",
        sender=sender,
        sms_text=sms_text,
        sanitized_text=sanitized_text,
        status=status,
        amount=extracted["amount"],
        type=extracted["type"],
        payment_mode=extracted["payment_mode"],
        merchant=extracted["merchant"],
        category=cat,
        bank=extracted["bank"],
        reference_id=extracted["reference_id"],
        card_last4=extracted["card_last4"],
        confidence=extracted["confidence"],
        fraud_score=fraud_score,
        suspicious_reasons=suspicious_reasons,
        is_confirmed_by_user=False,
        date_processed=processed_date
    )

    return sms_item
