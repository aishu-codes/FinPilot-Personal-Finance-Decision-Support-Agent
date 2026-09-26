"""
Natural Language Q&A Engine for FinPilot
Answers natural-language financial queries using ingested data, recurring subscriptions, budgets, and anomalies.
"""

from typing import List, Dict, Any
from collections import defaultdict
from backend.models.schemas import Transaction, SubscriptionItem, BudgetItem, GoalItem, QueryResponse

def answer_financial_query(
    question: str,
    transactions: List[Transaction],
    subscriptions: List[SubscriptionItem],
    budgets: List[BudgetItem],
    goals: List[GoalItem],
    current_month: str = "2026-09"
) -> QueryResponse:
    q_lower = question.lower().strip()
    curr_txs = [t for t in transactions if t.date.startswith(current_month) and t.type == "expense"]
    prior_month = "2026-08"
    prior_txs = [t for t in transactions if t.date.startswith(prior_month) and t.type == "expense"]

    # Intent 1: "Where did I spend the most this month?" / "top spending" / "largest expense category"
    if any(k in q_lower for k in ["spend the most", "top category", "highest category", "biggest spending", "largest expense", "where did i spend"]):
        cat_totals = defaultdict(float)
        for t in curr_txs:
            cat_totals[t.category] += t.amount
        
        if not cat_totals:
            return QueryResponse(
                question=question,
                intent="top_spending_category",
                answer="No expenses recorded for this month.",
                data_points={},
                suggested_followups=["Which subscriptions am I paying for?", "How much of my budget is committed?"]
            )

        sorted_cats = sorted(cat_totals.items(), key=lambda x: x[1], reverse=True)
        top_cat, top_amt = sorted_cats[0]
        total_exp = sum(cat_totals.values())
        pct = (top_amt / total_exp * 100) if total_exp > 0 else 0

        # Also get top merchant
        merchant_totals = defaultdict(float)
        for t in curr_txs:
            merchant_totals[t.merchant] += t.amount
        top_merch, top_merch_amt = sorted(merchant_totals.items(), key=lambda x: x[1], reverse=True)[0]

        answer = (
            f"You spent the most in **{top_cat}** this month, totaling **${top_amt:,.2f}** "
            f"({pct:.1f}% of your total ${total_exp:,.2f} monthly expenses).\n\n"
            f"Your single largest merchant expense was **{top_merch}** at **${top_merch_amt:,.2f}**."
        )

        breakdown = {cat: round(amt, 2) for cat, amt in sorted_cats[:5]}

        return QueryResponse(
            question=question,
            intent="top_spending_category",
            answer=answer,
            data_points={"top_category": top_cat, "top_amount": top_amt, "breakdown": breakdown},
            suggested_followups=["What expenses increased compared with last month?", "Which subscriptions am I paying for?"]
        )

    # Intent 2: "Which subscriptions am I paying for?" / "active subscriptions" / "recurring payments"
    elif any(k in q_lower for k in ["subscriptions", "recurring", "recurring payments", "services i pay for", "monthly bills"]):
        if not subscriptions:
            return QueryResponse(
                question=question,
                intent="active_subscriptions",
                answer="No active recurring subscriptions detected.",
                data_points={},
                suggested_followups=["Where did I spend the most this month?", "How much of my budget is committed?"]
            )

        total_sub_monthly = sum(s.amount for s in subscriptions)
        sub_list_str = "\n".join([
            f"- **{s.merchant}**: ${s.amount:.2f}/mo ({s.category})" + (f" ⚠️ *Price increased +{s.price_change_pct}% from ${s.previous_amount:.2f}*" if s.status == "price_hike" else "")
            for s in subscriptions
        ])

        answer = (
            f"You are currently paying for **{len(subscriptions)} active recurring subscriptions** "
            f"costing a total of **${total_sub_monthly:,.2f} per month** (${total_sub_monthly * 12:,.2f}/year):\n\n"
            f"{sub_list_str}"
        )

        return QueryResponse(
            question=question,
            intent="active_subscriptions",
            answer=answer,
            data_points={"subscriptions_count": len(subscriptions), "monthly_total": total_sub_monthly},
            suggested_followups=["What expenses increased compared with last month?", "How much of my budget is already committed?"]
        )

    # Intent 3: "What expenses increased compared with last month?" / "spending increase" / "more than last month"
    elif any(k in q_lower for k in ["increased", "compared with last month", "compared to last month", "more than last month", "spending hike", "growth"]):
        curr_cat = defaultdict(float)
        for t in curr_txs:
            curr_cat[t.category] += t.amount

        prior_cat = defaultdict(float)
        for t in prior_txs:
            prior_cat[t.category] += t.amount

        increases = []
        for cat, curr_amt in curr_cat.items():
            prev_amt = prior_cat.get(cat, 0.0)
            if curr_amt > prev_amt:
                diff = curr_amt - prev_amt
                pct = ((diff / prev_amt) * 100) if prev_amt > 0 else 100.0
                increases.append({"category": cat, "current": curr_amt, "prior": prev_amt, "diff": diff, "pct": pct})

        increases.sort(key=lambda x: x["diff"], reverse=True)

        if not increases:
            answer = "Good news! None of your category expenses increased compared to last month."
        else:
            inc_strs = []
            for item in increases:
                prev_str = f"vs ${item['prior']:,.2f} last month" if item['prior'] > 0 else "new category this month"
                inc_strs.append(f"- **{item['category']}**: Spent **${item['current']:,.2f}** (+${item['diff']:,.2f}, {item['pct']:.0f}% higher {prev_str})")

            answer = (
                f"Here are the categories where your spending **increased** compared to last month:\n\n"
                + "\n".join(inc_strs)
            )

        return QueryResponse(
            question=question,
            intent="expense_increases",
            answer=answer,
            data_points={"increases": increases},
            suggested_followups=["Where did I spend the most this month?", "How much of my budget is already committed?"]
        )

    # Intent 4: "How much of my budget is already committed?" / "committed budget" / "fixed obligations"
    elif any(k in q_lower for k in ["committed", "committed budget", "fixed expenses", "obligations", "how much of my budget"]):
        total_allocated = sum(b.allocated_amount for b in budgets)
        total_committed = sum(b.committed_amount for b in budgets) if budgets else sum(s.amount for s in subscriptions)
        total_spent = sum(b.spent_amount for b in budgets)

        pct_committed = (total_committed / total_allocated * 100) if total_allocated > 0 else 0

        answer = (
            f"You have **${total_committed:,.2f}** in recurring fixed obligations already committed "
            f"out of your total **${total_allocated:,.2f}** budget (**{pct_committed:.1f}% committed**).\n\n"
            f"- **Already Spent This Month**: ${total_spent:,.2f}\n"
            f"- **Committed Future Bills**: ${total_committed:,.2f}\n"
            f"- **Remaining Discretionary Capacity**: ${max(0.0, total_allocated - total_spent):,.2f}"
        )

        return QueryResponse(
            question=question,
            intent="committed_budget",
            answer=answer,
            data_points={"total_allocated": total_allocated, "total_committed": total_committed, "pct_committed": pct_committed},
            suggested_followups=["Which subscriptions am I paying for?", "What expenses increased compared with last month?"]
        )

    # Fallback / General Financial Search
    else:
        # Check if user mentioned a specific merchant or word
        matched_txs = [t for t in transactions if any(w in t.merchant.lower() or w in t.category.lower() for w in q_lower.split())]
        if matched_txs:
            tot = sum(t.amount for t in matched_txs if t.type == "expense")
            items_str = "\n".join([f"- {t.date}: {t.merchant} (${t.amount:.2f})" for t in matched_txs[:5]])
            answer = f"Found **{len(matched_txs)} transactions** matching your search, totaling **${tot:,.2f}**:\n\n{items_str}"
        else:
            total_inc = sum(abs(t.amount) for t in transactions if t.date.startswith(current_month) and t.type == "income")
            total_exp = sum(t.amount for t in transactions if t.date.startswith(current_month) and t.type == "expense")
            answer = (
                f"FinPilot Financial Summary for {current_month}:\n"
                f"- **Total Income**: ${total_inc:,.2f}\n"
                f"- **Total Expenses**: ${total_exp:,.2f}\n"
                f"- **Net Savings**: ${total_inc - total_exp:,.2f}\n"
                f"- **Active Subscriptions**: {len(subscriptions)}\n\n"
                f"Try asking: *'Where did I spend the most this month?'* or *'Which subscriptions am I paying for?'*"
            )

        return QueryResponse(
            question=question,
            intent="general_finance_query",
            answer=answer,
            data_points={},
            suggested_followups=["Where did I spend the most this month?", "Which subscriptions am I paying for?", "How much of my budget is already committed?"]
        )
