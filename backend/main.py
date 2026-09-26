import io
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
from datetime import datetime

from backend.models.schemas import (
    Transaction, SubscriptionItem, BudgetItem, GoalItem, AnomalyAlert,
    QueryRequest, QueryResponse, MonthlyReport, GoalImpactRequest,
    SMSProcessRequest, SMSLogItem, SMSConfirmRequest, SMSSummary
)
from backend.sample_data.sample_statements import DATASET_MAP, TECH_PROFESSIONAL_DATA
from backend.engine.parser import parse_csv_content, parse_json_content, parse_text_bill
from backend.engine.categorizer import categorize_transaction
from backend.engine.recurring_detector import detect_subscriptions_and_recurring, calculate_upcoming_obligations
from backend.engine.anomaly_detector import detect_anomalies
from backend.engine.budget_goal_engine import calculate_budget_health, analyze_goals_status, simulate_spending_impact_on_goal
from backend.engine.nl_qa_engine import answer_financial_query
from backend.engine.report_generator import generate_monthly_report
from backend.engine.sms_engine import process_incoming_sms

app = FastAPI(title="FinPilot Decision Support Agent API", version="1.1.0")

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory application state
state = {
    "profile_key": "tech_pro",
    "transactions": [],
    "budgets_cfg": [],
    "goals_cfg": [],
    "budgets": [],
    "goals": [],
    "subscriptions": [],
    "anomalies": [],
    "sms_logs": []
}

def reload_dataset(profile_key: str = "tech_pro"):
    data = DATASET_MAP.get(profile_key, TECH_PROFESSIONAL_DATA)
    state["profile_key"] = profile_key
    
    # Load transactions
    state["transactions"] = [Transaction(**t) for t in data["transactions"]]
    state["budgets_cfg"] = data["budgets"]
    state["goals_cfg"] = data["goals"]
    state["sms_logs"] = [] # Reset SMS logs on dataset switch
    
    # Run intelligence pipeline
    recalculate_pipeline()

def recalculate_pipeline():
    txs = state["transactions"]
    subs = detect_subscriptions_and_recurring(txs)
    state["subscriptions"] = subs
    
    anomalies = detect_anomalies(txs, subs)
    
    # Add suspicious SMS alerts to anomalies feed
    for sms in state["sms_logs"]:
        if sms.status == "SUSPICIOUS":
            anomalies.append(AnomalyAlert(
                id=f"alt_sms_{sms.id}",
                type="suspicious_sms",
                title=f"⚠️ Suspicious SMS Alert: {sms.sender}",
                description=f"Scam risk detected in message: '{sms.sanitized_text[:60]}...'. Reasons: {', '.join(sms.suspicious_reasons)}",
                amount=sms.amount,
                category="Security Warning",
                severity="high",
                date=sms.date_processed[:10],
                action_suggested="Do NOT click any link in this SMS or share OTP/PIN. Review in SMS tab."
            ))

    state["anomalies"] = anomalies
    
    b_health = calculate_budget_health(txs, subs, state["budgets_cfg"])
    state["budgets"] = b_health
    
    g_status = analyze_goals_status(state["goals_cfg"])
    state["goals"] = g_status

# Initialize default dataset on startup
@app.on_event("startup")
def startup_event():
    reload_dataset("tech_pro")

@app.get("/api/health")
def health_check():
    return {"status": "ok", "agent": "FinPilot Smart SMS Decision Support Agent", "active_profile": state["profile_key"]}

@app.get("/api/datasets")
def list_datasets():
    return [
        {"key": "tech_pro", "name": "Tech Professional", "description": TECH_PROFESSIONAL_DATA["description"]},
        {"key": "family", "name": "Family Household", "description": DATASET_MAP["family"]["description"]},
        {"key": "freelancer", "name": "Freelancer & Consultant", "description": DATASET_MAP["freelancer"]["description"]}
    ]

@app.post("/api/dataset/load/{profile_key}")
def load_dataset(profile_key: str):
    if profile_key not in DATASET_MAP:
        raise HTTPException(status_code=404, detail="Dataset profile not found")
    reload_dataset(profile_key)
    return {"message": f"Successfully loaded dataset: {profile_key}", "transaction_count": len(state["transactions"])}

# --- STATEMENT & BILL UPLOADS ---
@app.post("/api/upload/statement")
async def upload_statement(
    file: Optional[UploadFile] = File(None),
    text_content: Optional[str] = Form(None),
    account_name: str = Form("Main Account")
):
    new_txs = []
    if file:
        content_bytes = await file.read()
        content_str = content_bytes.decode("utf-8", errors="ignore")
        filename = file.filename.lower()
        if filename.endswith(".json"):
            new_txs = parse_json_content(content_str, account_name)
        else: # Default CSV
            new_txs = parse_csv_content(content_str, account_name)
    elif text_content:
        single_tx = parse_text_bill(text_content)
        new_txs = [single_tx]
    else:
        raise HTTPException(status_code=400, detail="Must provide either a file upload or bill text content")

    state["transactions"].extend(new_txs)
    recalculate_pipeline()

    return {
        "message": f"Successfully ingested {len(new_txs)} transactions",
        "ingested_count": len(new_txs),
        "total_transactions": len(state["transactions"])
    }

# --- SMART SMS TRANSACTION AGENT ENDPOINTS ---

@app.post("/api/sms/analyze", response_model=SMSLogItem)
def analyze_sms_endpoint(req: SMSProcessRequest):
    """
    Analyzes raw SMS text without storing state. Useful for instant preview.
    """
    sms_item = process_incoming_sms(req.sms_text, req.sender or "BANK-SMS", req.timestamp)
    return sms_item

@app.post("/api/sms/process")
def process_sms_endpoint(req: SMSProcessRequest):
    """
    Receives incoming SMS payload (from Android listener or Paste SMS UI),
    runs sanitization, scam detection, transaction extraction, duplicate check,
    and records to financial ledger if verified.
    """
    sms_item = process_incoming_sms(req.sms_text, req.sender or "BANK-SMS", req.timestamp)
    
    # 1. Duplicate Protection Check
    is_duplicate = False
    for existing in state["sms_logs"]:
        if (existing.amount == sms_item.amount and 
            existing.merchant == sms_item.merchant and 
            existing.date_processed[:10] == sms_item.date_processed[:10] and 
            existing.reference_id == sms_item.reference_id):
            is_duplicate = True
            break

    if is_duplicate:
        return {
            "status": "DUPLICATE_IGNORED",
            "message": "Duplicate SMS transaction detected and ignored.",
            "sms_item": sms_item
        }

    state["sms_logs"].append(sms_item)

    # 2. If VERIFIED_TRANSACTION -> Auto-insert into FinPilot Financial Transactions
    if sms_item.status == "VERIFIED_TRANSACTION" and sms_item.amount > 0:
        tx_id = f"tx_sms_{sms_item.id}"
        tx_date = sms_item.date_processed[:10]
        tx_amount = -abs(sms_item.amount) if sms_item.type == "income" else abs(sms_item.amount)

        fin_tx = Transaction(
            id=tx_id,
            date=tx_date,
            merchant=sms_item.merchant,
            amount=tx_amount,
            category=sms_item.category,
            type=sms_item.type,
            payment_mode=sms_item.payment_mode,
            source="SMS",
            account=sms_item.bank,
            reference_id=sms_item.reference_id
        )

        state["transactions"].append(fin_tx)
        sms_item.associated_transaction_id = tx_id
        recalculate_pipeline()

    return {
        "status": sms_item.status,
        "message": f"Processed SMS. Status: {sms_item.status}",
        "sms_item": sms_item
    }

@app.get("/api/sms/transactions")
def get_sms_transactions():
    """
    Returns all processed SMS logs along with summary statistics.
    """
    logs = state["sms_logs"]
    verified = [s for s in logs if s.status == "VERIFIED_TRANSACTION"]
    suspicious = [s for s in logs if s.status == "SUSPICIOUS"]
    unknown = [s for s in logs if s.status == "UNKNOWN"]

    income_detected = sum(s.amount for s in verified if s.type == "income")
    expenses_detected = sum(s.amount for s in verified if s.type == "expense")
    
    online_spending = sum(s.amount for s in verified if s.payment_mode in ["UPI", "CARD", "BANK_TRANSFER"])
    cash_spending = sum(s.amount for s in verified if s.payment_mode in ["ATM", "CASH"])

    summary = SMSSummary(
        total_sms=len(logs),
        verified_count=len(verified),
        suspicious_count=len(suspicious),
        unknown_count=len(unknown),
        income_detected=round(income_detected, 2),
        expenses_detected=round(expenses_detected, 2),
        online_spending=round(online_spending, 2),
        cash_spending=round(cash_spending, 2)
    )

    return {
        "summary": summary,
        "sms_logs": sorted(logs, key=lambda x: x.date_processed, reverse=True)
    }

@app.get("/api/sms/suspicious")
def get_suspicious_sms():
    """
    Returns only suspicious SMS items requiring user review.
    """
    return [s for s in state["sms_logs"] if s.status == "SUSPICIOUS"]

@app.post("/api/sms/confirm")
def confirm_sms_endpoint(req: SMSConfirmRequest):
    """
    Allows user to manually approve a suspicious or unknown SMS into financial records, or reject it.
    """
    sms_item = next((s for s in state["sms_logs"] if s.id == req.sms_id), None)
    if not sms_item:
        raise HTTPException(status_code=404, detail="SMS log item not found")

    sms_item.is_confirmed_by_user = True

    if req.action == "approve":
        sms_item.status = "VERIFIED_TRANSACTION"
        if req.override_category:
            sms_item.category = req.override_category
        if req.override_merchant:
            sms_item.merchant = req.override_merchant

        # Convert to financial transaction if not already added
        if not sms_item.associated_transaction_id and sms_item.amount > 0:
            tx_id = f"tx_sms_cfm_{sms_item.id}"
            tx_amount = -abs(sms_item.amount) if sms_item.type == "income" else abs(sms_item.amount)
            fin_tx = Transaction(
                id=tx_id,
                date=sms_item.date_processed[:10],
                merchant=sms_item.merchant,
                amount=tx_amount,
                category=sms_item.category,
                type=sms_item.type,
                payment_mode=sms_item.payment_mode,
                source="SMS",
                account=sms_item.bank,
                reference_id=sms_item.reference_id
            )
            state["transactions"].append(fin_tx)
            sms_item.associated_transaction_id = tx_id
            recalculate_pipeline()

        return {"message": "SMS confirmed and recorded as transaction", "sms_item": sms_item}
    else:
        sms_item.status = "NON_TRANSACTION"
        return {"message": "SMS rejected", "sms_item": sms_item}

# --- OVERVIEW & ANALYTICS ENDPOINTS ---
@app.get("/api/overview")
def get_overview():
    txs = state["transactions"]
    curr_txs = [t for t in txs if t.date.startswith("2026-09")]
    
    total_income = sum(abs(t.amount) for t in curr_txs if t.type == "income")
    total_expenses = sum(t.amount for t in curr_txs if t.type == "expense")
    net_savings = round(total_income - total_expenses, 2)
    savings_rate = round((net_savings / total_income * 100), 1) if total_income > 0 else 0.0

    committed_total = sum(s.amount for s in state["subscriptions"])

    # Online vs Cash Spending breakdown
    online_spending = sum(t.amount for t in curr_txs if t.type == "expense" and t.payment_mode in ["UPI", "CARD", "BANK_TRANSFER"])
    cash_spending = sum(t.amount for t in curr_txs if t.type == "expense" and t.payment_mode in ["ATM", "CASH"])

    # Monthly Cashflow chart data
    cashflow = []
    for m in ["2026-07", "2026-08", "2026-09"]:
        m_txs = [t for t in txs if t.date.startswith(m)]
        inc = sum(abs(t.amount) for t in m_txs if t.type == "income")
        exp = sum(t.amount for t in m_txs if t.type == "expense")
        cashflow.append({"month": m, "income": round(inc, 2), "expenses": round(exp, 2), "net": round(inc - exp, 2)})

    # Top spending categories
    cat_map = {}
    for t in curr_txs:
        if t.type == "expense":
            cat_map[t.category] = cat_map.get(t.category, 0.0) + t.amount
    
    top_categories = [
        {"category": cat, "amount": round(amt, 2)}
        for cat, amt in sorted(cat_map.items(), key=lambda x: x[1], reverse=True)
    ]

    suspicious_count = sum(1 for s in state["sms_logs"] if s.status == "SUSPICIOUS")

    return {
        "total_income": round(total_income, 2),
        "total_expenses": round(total_expenses, 2),
        "net_savings": net_savings,
        "savings_rate": savings_rate,
        "committed_obligations": round(committed_total, 2),
        "active_subscriptions_count": len(state["subscriptions"]),
        "anomalies_count": len(state["anomalies"]),
        "suspicious_sms_count": suspicious_count,
        "online_spending": round(online_spending, 2),
        "cash_spending": round(cash_spending, 2),
        "cashflow": cashflow,
        "top_categories": top_categories,
        "anomalies": state["anomalies"]
    }

@app.get("/api/transactions")
def get_transactions(category: Optional[str] = None, payment_mode: Optional[str] = None, search: Optional[str] = None):
    txs = state["transactions"]
    if category and category != "All":
        txs = [t for t in txs if t.category == category]
    if payment_mode and payment_mode != "All":
        txs = [t for t in txs if t.payment_mode == payment_mode]
    if search:
        s = search.lower()
        txs = [t for t in txs if s in t.merchant.lower() or s in t.category.lower() or s in t.date]
    return sorted(txs, key=lambda x: x.date, reverse=True)

@app.post("/api/transaction")
def add_transaction(tx: Transaction):
    state["transactions"].append(tx)
    recalculate_pipeline()
    return {"message": "Transaction added", "id": tx.id}

@app.get("/api/subscriptions")
def get_subscriptions():
    upcoming = calculate_upcoming_obligations(state["subscriptions"])
    return {
        "subscriptions": state["subscriptions"],
        "upcoming_summary": upcoming
    }

@app.get("/api/anomalies")
def get_anomalies():
    return state["anomalies"]

@app.get("/api/budgets")
def get_budgets():
    return state["budgets"]

@app.post("/api/budgets")
def update_budget(category: str = Form(...), allocated_amount: float = Form(...)):
    found = False
    for cfg in state["budgets_cfg"]:
        if cfg["category"] == category:
            cfg["allocated_amount"] = allocated_amount
            found = True
            break
    if not found:
        state["budgets_cfg"].append({"category": category, "allocated_amount": allocated_amount})
    
    recalculate_pipeline()
    return {"message": f"Updated budget for {category}"}

@app.get("/api/goals")
def get_goals():
    return state["goals"]

@app.post("/api/goals/simulate")
def simulate_goal_impact(req: GoalImpactRequest):
    goal = next((g for g in state["goals"] if g.id == req.goal_id), None)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    sim_res = simulate_spending_impact_on_goal(goal, req.additional_monthly_spending)
    return sim_res

@app.post("/api/qa/ask", response_model=QueryResponse)
def ask_question(req: QueryRequest):
    res = answer_financial_query(
        question=req.question,
        transactions=state["transactions"],
        subscriptions=state["subscriptions"],
        budgets=state["budgets"],
        goals=state["goals"],
        current_month="2026-09"
    )
    return res

@app.get("/api/report/monthly")
def get_monthly_report():
    report = generate_monthly_report(
        transactions=state["transactions"],
        subscriptions=state["subscriptions"],
        budgets=state["budgets"],
        goals=state["goals"],
        anomalies=state["anomalies"],
        period="September 2026"
    )
    return report
