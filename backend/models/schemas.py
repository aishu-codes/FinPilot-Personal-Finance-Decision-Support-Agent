from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class Transaction(BaseModel):
    id: str
    date: str  # YYYY-MM-DD
    merchant: str
    amount: float  # Positive for expense, negative for income
    category: str
    type: str = "expense"  # expense | income
    payment_mode: str = "OTHER"  # UPI | CARD | BANK_TRANSFER | ATM | CASH | OTHER
    source: str = "statement"  # statement | bill | manual | SMS
    is_recurring: bool = False
    notes: Optional[str] = None
    account: Optional[str] = "Main Account"
    reference_id: Optional[str] = None

class StatementIngestRequest(BaseModel):
    account_name: Optional[str] = "Main Account"
    transactions: List[Dict[str, Any]]

class CategorySummary(BaseModel):
    category: str
    total_amount: float
    percentage: float
    transaction_count: int
    change_vs_last_month: Optional[float] = 0.0

class SubscriptionItem(BaseModel):
    id: str
    merchant: str
    category: str
    amount: float
    frequency: str = "monthly"  # monthly | annual | weekly
    last_billed: str
    next_due: str
    previous_amount: Optional[float] = None
    price_change_pct: Optional[float] = 0.0
    status: str = "active"  # active | increased | price_hike | unused_risk

class BudgetItem(BaseModel):
    category: str
    allocated_amount: float
    spent_amount: float
    committed_amount: float = 0.0  # upcoming recurring obligations in this category
    remaining_amount: float
    percentage_used: float
    status: str = "within_limit"  # within_limit | warning | exceeded

class GoalItem(BaseModel):
    id: str
    name: str
    target_amount: float
    current_savings: float
    monthly_contribution: float
    target_date: str  # YYYY-MM-DD
    category: Optional[str] = "Savings"
    status: str = "on_track"  # on_track | at_risk | behind
    completion_percentage: float
    projected_date: str
    impact_notes: Optional[str] = None

class GoalImpactRequest(BaseModel):
    goal_id: str
    additional_monthly_spending: float = 0.0
    spending_category_reduction: Optional[Dict[str, float]] = None

class AnomalyAlert(BaseModel):
    id: str
    type: str  # spike | price_hike | unusual_merchant | duplicate | suspicious_sms
    title: str
    description: str
    amount: float
    category: str
    severity: str = "medium"  # low | medium | high
    date: str
    action_suggested: Optional[str] = None

class QueryRequest(BaseModel):
    question: str
    month: Optional[str] = None

class QueryResponse(BaseModel):
    question: str
    intent: str
    answer: str
    data_points: Dict[str, Any] = {}
    suggested_followups: List[str] = []

class MonthlyReport(BaseModel):
    period: str
    total_income: float
    total_expenses: float
    net_savings: float
    savings_rate: float
    top_categories: List[CategorySummary]
    active_subscriptions_count: int
    total_recurring_monthly: float
    upcoming_obligations_total: float
    budget_health: Dict[str, Any]
    goals_status: List[GoalItem]
    anomalies: List[AnomalyAlert]
    executive_summary: str
    action_items: List[str]

# --- Smart SMS Agent Schemas ---

class SMSProcessRequest(BaseModel):
    sms_text: str
    sender: Optional[str] = "BANK-SMS"
    timestamp: Optional[str] = None

class SMSLogItem(BaseModel):
    id: str
    sender: str = "BANK-SMS"
    sms_text: str
    sanitized_text: str
    status: str  # VERIFIED_TRANSACTION | SUSPICIOUS | NON_TRANSACTION | UNKNOWN
    amount: float = 0.0
    type: str = "expense"  # expense | income
    payment_mode: str = "OTHER"  # UPI | CARD | BANK_TRANSFER | ATM | CASH | OTHER
    merchant: str = "Unknown"
    category: str = "Other"
    bank: str = "Unknown Bank"
    reference_id: Optional[str] = None
    card_last4: Optional[str] = None
    confidence: float = 0.0
    fraud_score: float = 0.0
    suspicious_reasons: List[str] = []
    is_confirmed_by_user: bool = False
    date_processed: str
    associated_transaction_id: Optional[str] = None

class SMSConfirmRequest(BaseModel):
    sms_id: str
    action: str  # approve | reject
    override_category: Optional[str] = None
    override_merchant: Optional[str] = None

class SMSSummary(BaseModel):
    total_sms: int
    verified_count: int
    suspicious_count: int
    unknown_count: int
    income_detected: float
    expenses_detected: float
    online_spending: float
    cash_spending: float
