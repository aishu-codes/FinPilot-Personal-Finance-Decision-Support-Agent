import pytest
from backend.engine.parser import parse_csv_content, parse_json_content, parse_text_bill
from backend.engine.categorizer import categorize_transaction
from backend.engine.recurring_detector import detect_subscriptions_and_recurring
from backend.engine.anomaly_detector import detect_anomalies
from backend.engine.budget_goal_engine import calculate_budget_health, analyze_goals_status, simulate_spending_impact_on_goal
from backend.engine.nl_qa_engine import answer_financial_query
from backend.sample_data.sample_statements import TECH_PROFESSIONAL_DATA
from backend.models.schemas import Transaction, GoalItem

def test_parser_csv():
    csv_str = "Date,Merchant,Amount,Category\n2026-09-01,Starbucks Coffee,5.75,Food & Dining\n2026-09-02,Amazon.com,49.99,Shopping"
    txs = parse_csv_content(csv_str, "Test Account")
    assert len(txs) == 2
    assert txs[0].merchant == "Starbucks Coffee"
    assert txs[0].amount == 5.75
    assert txs[1].category == "Shopping"

def test_parser_json():
    json_str = '[{"date": "2026-09-01", "merchant": "Netflix", "amount": 19.99, "category": "Subscriptions"}]'
    txs = parse_json_content(json_str)
    assert len(txs) == 1
    assert txs[0].merchant == "Netflix"
    assert txs[0].amount == 19.99

def test_categorization():
    assert categorize_transaction("Chipotle Grill") == "Food & Dining"
    assert categorize_transaction("Netflix Subscription") == "Subscriptions"
    assert categorize_transaction("City Power Utility") == "Housing & Utilities"
    assert categorize_transaction("Acme Corp Salary", amount=-4800.0) == "Income"

def test_recurring_and_price_hike_detection():
    txs = [Transaction(**t) for t in TECH_PROFESSIONAL_DATA["transactions"]]
    subs = detect_subscriptions_and_recurring(txs)
    assert len(subs) > 0
    netflix_sub = next((s for s in subs if "Netflix" in s.merchant), None)
    assert netflix_sub is not None
    assert netflix_sub.status == "price_hike"
    assert netflix_sub.price_change_pct > 0

def test_anomaly_detection():
    txs = [Transaction(**t) for t in TECH_PROFESSIONAL_DATA["transactions"]]
    subs = detect_subscriptions_and_recurring(txs)
    anomalies = detect_anomalies(txs, subs, current_month="2026-09")
    assert len(anomalies) > 0
    price_hikes = [a for a in anomalies if a.type == "price_hike"]
    assert len(price_hikes) > 0

def test_budget_and_goals():
    txs = [Transaction(**t) for t in TECH_PROFESSIONAL_DATA["transactions"]]
    subs = detect_subscriptions_and_recurring(txs)
    budgets = calculate_budget_health(txs, subs, TECH_PROFESSIONAL_DATA["budgets"])
    assert len(budgets) > 0

    goals = analyze_goals_status(TECH_PROFESSIONAL_DATA["goals"])
    assert len(goals) == 2
    
    sim = simulate_spending_impact_on_goal(goals[0], additional_monthly_spend=100.0)
    assert sim["impact_months_diff"] > 0

def test_natural_language_qa_queries():
    txs = [Transaction(**t) for t in TECH_PROFESSIONAL_DATA["transactions"]]
    subs = detect_subscriptions_and_recurring(txs)
    budgets = calculate_budget_health(txs, subs, TECH_PROFESSIONAL_DATA["budgets"])
    goals = analyze_goals_status(TECH_PROFESSIONAL_DATA["goals"])

    # Question 1: "Where did I spend the most this month?"
    res1 = answer_financial_query("Where did I spend the most this month?", txs, subs, budgets, goals)
    assert "Housing & Utilities" in res1.answer or "Shopping" in res1.answer or "most" in res1.answer.lower()
    assert res1.intent == "top_spending_category"

    # Question 2: "Which subscriptions am I paying for?"
    res2 = answer_financial_query("Which subscriptions am I paying for?", txs, subs, budgets, goals)
    assert "Netflix" in res2.answer
    assert res2.intent == "active_subscriptions"

    # Question 3: "What expenses increased compared with last month?"
    res3 = answer_financial_query("What expenses increased compared with last month?", txs, subs, budgets, goals)
    assert "increased" in res3.answer.lower() or "Shopping" in res3.answer
    assert res3.intent == "expense_increases"

    # Question 4: "How much of my budget is already committed?"
    res4 = answer_financial_query("How much of my budget is already committed?", txs, subs, budgets, goals)
    assert "committed" in res4.answer.lower()
    assert res4.intent == "committed_budget"
