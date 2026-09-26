"""
Monthly Financial Summary Report Generator for FinPilot
Synthesizes comprehensive monthly summaries, key observations, and action items.
"""

from typing import List, Dict, Any
from collections import defaultdict
from backend.models.schemas import Transaction, SubscriptionItem, BudgetItem, GoalItem, AnomalyAlert, MonthlyReport, CategorySummary

def generate_monthly_report(
    transactions: List[Transaction],
    subscriptions: List[SubscriptionItem],
    budgets: List[BudgetItem],
    goals: List[GoalItem],
    anomalies: List[AnomalyAlert],
    period: str = "September 2026"
) -> MonthlyReport:
    curr_month = "2026-09"
    curr_txs = [t for t in transactions if t.date.startswith(curr_month)]

    total_income = sum(abs(t.amount) for t in curr_txs if t.type == "income")
    total_expenses = sum(t.amount for t in curr_txs if t.type == "expense")
    net_savings = round(total_income - total_expenses, 2)
    savings_rate = round((net_savings / total_income * 100), 1) if total_income > 0 else 0.0

    # Category Summaries
    cat_map = defaultdict(float)
    cat_counts = defaultdict(int)
    for t in curr_txs:
        if t.type == "expense":
            cat_map[t.category] += t.amount
            cat_counts[t.category] += 1

    top_categories = []
    for cat, amt in sorted(cat_map.items(), key=lambda x: x[1], reverse=True):
        pct = round((amt / total_expenses * 100), 1) if total_expenses > 0 else 0.0
        top_categories.append(CategorySummary(
            category=cat,
            total_amount=round(amt, 2),
            percentage=pct,
            transaction_count=cat_counts[cat],
            change_vs_last_month=0.0
        ))

    total_recurring = round(sum(s.amount for s in subscriptions), 2)
    upcoming_obligations_total = total_recurring

    # Executive Commentary Synthesis
    executive_summary = (
        f"FinPilot Financial Report for {period}:\n"
        f"During this period, total income was ${total_income:,.2f} against total expenses of ${total_expenses:,.2f}, "
        f"resulting in a net savings of ${net_savings:,.2f} (Savings Rate: {savings_rate}%).\n\n"
        f"Your highest spending category was {top_categories[0].category if top_categories else 'N/A'} at ${top_categories[0].total_amount:,.2f}. "
        f"You have {len(subscriptions)} active recurring subscriptions totaling ${total_recurring:,.2f}/month. "
        f"There are {len(anomalies)} spending anomaly alerts requiring attention."
    )

    action_items = []
    # Generate concrete non-advisory action items
    for alt in anomalies:
        if alt.action_suggested:
            action_items.append(f"• [{alt.category}] {alt.title}: {alt.action_suggested}")

    for b in budgets:
        if b.status == "exceeded":
            action_items.append(f"• [Budget Alert] {b.category} exceeded budget by ${abs(b.remaining_amount):.2f} ({b.percentage_used}% used).")

    for g in goals:
        if g.status == "at_risk":
            action_items.append(f"• [Goal Alert] {g.name} contribution of ${g.monthly_contribution:.0f}/mo is behind target date of {g.target_date}.")

    if not action_items:
        action_items.append("• Maintain current savings velocity to stay on target for financial goals.")

    budget_health_summary = {
        "within_limit_count": sum(1 for b in budgets if b.status == "within_limit"),
        "warning_count": sum(1 for b in budgets if b.status == "warning"),
        "exceeded_count": sum(1 for b in budgets if b.status == "exceeded"),
        "total_budgeted": sum(b.allocated_amount for b in budgets),
        "total_spent": sum(b.spent_amount for b in budgets)
    }

    return MonthlyReport(
        period=period,
        total_income=round(total_income, 2),
        total_expenses=round(total_expenses, 2),
        net_savings=net_savings,
        savings_rate=savings_rate,
        top_categories=top_categories,
        active_subscriptions_count=len(subscriptions),
        total_recurring_monthly=total_recurring,
        upcoming_obligations_total=upcoming_obligations_total,
        budget_health=budget_health_summary,
        goals_status=goals,
        anomalies=anomalies,
        executive_summary=executive_summary,
        action_items=action_items
    )
