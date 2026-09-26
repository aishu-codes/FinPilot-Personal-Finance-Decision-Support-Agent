"""
Budget & Financial Goal Engine for FinPilot
Calculates budget health, committed obligations, goal velocity, and goal impact modeling.
"""

from typing import List, Dict, Any
from datetime import datetime
from backend.models.schemas import Transaction, BudgetItem, GoalItem, SubscriptionItem

def calculate_budget_health(
    transactions: List[Transaction],
    subscriptions: List[SubscriptionItem],
    budget_configs: List[Dict[str, Any]],
    current_month: str = "2026-09"
) -> List[BudgetItem]:
    """
    Compares user-defined category budget limits with actual spent and committed obligations.
    """
    curr_txs = [t for t in transactions if t.date.startswith(current_month) and t.type == "expense"]

    # Calculate actual spent per category
    spent_map = {}
    for t in curr_txs:
        spent_map[t.category] = spent_map.get(t.category, 0.0) + t.amount

    # Calculate committed obligations per category
    committed_map = {}
    for sub in subscriptions:
        committed_map[sub.category] = committed_map.get(sub.category, 0.0) + sub.amount

    budget_items = []

    for cfg in budget_configs:
        cat = cfg["category"]
        allocated = float(cfg["allocated_amount"])
        spent = round(spent_map.get(cat, 0.0), 2)
        committed = round(committed_map.get(cat, 0.0), 2)
        remaining = round(allocated - spent, 2)
        pct_used = round((spent / allocated) * 100, 1) if allocated > 0 else 0.0

        if pct_used > 100.0:
            status = "exceeded"
        elif pct_used >= 80.0:
            status = "warning"
        else:
            status = "within_limit"

        budget_items.append(BudgetItem(
            category=cat,
            allocated_amount=allocated,
            spent_amount=spent,
            committed_amount=committed,
            remaining_amount=remaining,
            percentage_used=pct_used,
            status=status
        ))

    # Also add any category with spending that was not explicitly configured
    cfg_cats = {cfg["category"] for cfg in budget_configs}
    for cat, spent in spent_map.items():
        if cat not in cfg_cats and spent > 0:
            pct_used = 100.0
            budget_items.append(BudgetItem(
                category=cat,
                allocated_amount=spent,
                spent_amount=spent,
                committed_amount=committed_map.get(cat, 0.0),
                remaining_amount=0.0,
                percentage_used=pct_used,
                status="warning"
            ))

    return budget_items

def analyze_goals_status(
    goals_data: List[Dict[str, Any]],
    current_net_savings: float = 1200.0
) -> List[GoalItem]:
    """
    Calculates progress, projected completion dates, and shortfall for user financial goals.
    """
    goals = []

    for g in goals_data:
        target_amt = float(g["target_amount"])
        curr_sav = float(g["current_savings"])
        m_contrib = float(g["monthly_contribution"])
        target_date = g["target_date"]

        remaining_to_save = max(0.0, target_amt - curr_sav)
        pct = round((curr_sav / target_amt) * 100, 1) if target_amt > 0 else 100.0

        # Estimate months required
        months_needed = remaining_to_save / m_contrib if m_contrib > 0 else 999.0

        # Calculate projected date
        start_dt = datetime.now()
        proj_year = start_dt.year + int((start_dt.month - 1 + months_needed) // 12)
        proj_month = int(((start_dt.month - 1 + months_needed) % 12) + 1)
        projected_date = f"{proj_year:04d}-{proj_month:02d}-01"

        status = "on_track"
        notes = f"At ${m_contrib:.0f}/month, you will reach your ${target_amt:,.0f} goal by {projected_date}."

        if target_date and projected_date > target_date:
            status = "at_risk"
            notes = f"Target date is {target_date}, but at current contribution rate of ${m_contrib:.0f}/mo, completion is projected for {projected_date}."

        goals.append(GoalItem(
            id=g.get("id", "g_unk"),
            name=g["name"],
            target_amount=target_amt,
            current_savings=curr_sav,
            monthly_contribution=m_contrib,
            target_date=target_date,
            category=g.get("category", "Savings"),
            status=status,
            completion_percentage=pct,
            projected_date=projected_date,
            impact_notes=notes
        ))

    return goals

def simulate_spending_impact_on_goal(
    goal: GoalItem,
    additional_monthly_spend: float = 0.0,
    monthly_reduction: float = 0.0
) -> Dict[str, Any]:
    """
    Simulates how increasing or decreasing monthly spending impacts a specific goal's completion date.
    """
    new_monthly_contrib = max(10.0, goal.monthly_contribution - additional_monthly_spend + monthly_reduction)
    remaining_to_save = max(0.0, goal.target_amount - goal.current_savings)
    new_months_needed = remaining_to_save / new_monthly_contrib

    start_dt = datetime.now()
    proj_year = start_dt.year + int((start_dt.month - 1 + new_months_needed) // 12)
    proj_month = int(((start_dt.month - 1 + new_months_needed) % 12) + 1)
    new_projected_date = f"{proj_year:04d}-{proj_month:02d}-01"

    delay_months = round(new_months_needed - (remaining_to_save / goal.monthly_contribution if goal.monthly_contribution > 0 else 0), 1)

    return {
        "goal_name": goal.name,
        "original_target_date": goal.target_date,
        "original_projected_date": goal.projected_date,
        "new_projected_date": new_projected_date,
        "original_monthly_contribution": goal.monthly_contribution,
        "new_monthly_contribution": round(new_monthly_contrib, 2),
        "impact_months_diff": delay_months,
        "impact_summary": f"Spending an extra ${additional_monthly_spend:.0f}/month shifts your {goal.name} goal completion by {abs(delay_months)} months ({'delay' if delay_months > 0 else 'earlier'})."
    }
