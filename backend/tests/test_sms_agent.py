import pytest
from backend.engine.sms_engine import process_incoming_sms, sanitize_sensitive_info, detect_fraud_and_scams, parse_and_extract_sms
from backend.models.schemas import SMSProcessRequest
from backend.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_genuine_debit_sms():
    sms = "Rs.850 debited from A/c XX1234 for AMAZON via UPI. Ref 987654321."
    res = process_incoming_sms(sms)
    assert res.status == "VERIFIED_TRANSACTION"
    assert res.amount == 850.0
    assert res.type == "expense"
    assert res.payment_mode == "UPI"
    assert "Amazon" in res.merchant
    assert res.category == "Shopping"
    assert res.confidence >= 0.75

def test_genuine_credit_sms():
    sms = "Rs. 5000.00 credited to A/c XX4321 from CLIENT PAYOUT on 2026-09-20. Ref TXN112233."
    res = process_incoming_sms(sms)
    assert res.status == "VERIFIED_TRANSACTION"
    assert res.amount == 5000.0
    assert res.type == "income"
    assert res.confidence >= 0.70

def test_upi_received_money():
    sms = "INR 1,200.00 received in your HDFC Bank account via UPI from Swiggy Refund."
    res = process_incoming_sms(sms)
    assert res.status == "VERIFIED_TRANSACTION"
    assert res.amount == 1200.0
    assert res.type == "income"
    assert res.payment_mode == "UPI"

def test_atm_cash_withdrawal():
    sms = "Rs.2000 cash withdrawn at HDFC ATM using Debit Card XX5678 on 2026-09-21."
    res = process_incoming_sms(sms)
    assert res.status == "VERIFIED_TRANSACTION"
    assert res.amount == 2000.0
    assert res.payment_mode == "ATM"
    assert res.type == "expense"

def test_cash_deposit():
    sms = "Rs. 3000 cash deposited into A/c XX1234 via CDM on 2026-09-22."
    res = process_incoming_sms(sms)
    assert res.status == "VERIFIED_TRANSACTION"
    assert res.amount == 3000.0
    assert res.payment_mode == "CASH"
    assert res.type == "income"

def test_refund_sms():
    sms = "Rs.450 refunded to your ICICI credit card for Zomato order."
    res = process_incoming_sms(sms)
    assert res.status == "VERIFIED_TRANSACTION"
    assert res.amount == 450.0
    assert res.type == "income"

def test_fake_kyc_scam_sms():
    sms = "Your HDFC account will be blocked today! Click http://bit.ly/fake-kyc to verify PAN immediately."
    res = process_incoming_sms(sms, sender="+919876543210")
    assert res.status == "SUSPICIOUS"
    assert res.fraud_score >= 0.40
    assert len(res.suspicious_reasons) > 0

def test_suspicious_url_sms():
    sms = "Rs. 10,000 cash reward approved! Click http://verify-bank-rewards.xyz to claim."
    res = process_incoming_sms(sms)
    assert res.status == "SUSPICIOUS"
    assert res.fraud_score >= 0.40

def test_otp_sms_sanitization_and_classification():
    sms = "Your OTP for login is 987654. Do not share your OTP with anyone."
    sanitized = sanitize_sensitive_info(sms)
    assert "******" in sanitized
    assert "987654" not in sanitized
    
    res = process_incoming_sms(sms)
    assert res.status == "NON_TRANSACTION"

def test_non_financial_sms():
    sms = "Hey! Let's grab coffee at 5 PM today."
    res = process_incoming_sms(sms)
    assert res.status == "NON_TRANSACTION"
    assert res.amount == 0.0

def test_unknown_low_confidence_sms():
    sms = "Payment update regarding reference 1234."
    res = process_incoming_sms(sms)
    assert res.status in ["UNKNOWN", "NON_TRANSACTION"]

def test_duplicate_sms_api():
    # Process first SMS
    payload = {"sms_text": "Rs.750 debited for STARBUCKS via UPI. Ref 998877.", "sender": "BANK-SMS"}
    resp1 = client.post("/api/sms/process", json=payload)
    assert resp1.status_code == 200
    data1 = resp1.json()
    assert data1["status"] == "VERIFIED_TRANSACTION"

    # Send identical duplicate SMS
    resp2 = client.post("/api/sms/process", json=payload)
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert data2["status"] == "DUPLICATE_IGNORED"
