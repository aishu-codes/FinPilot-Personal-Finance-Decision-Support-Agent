"""
Recurring & Subscription Detector Engine for FinPilot
Identifies recurring payments, billing cycles, price increases, and upcoming obligations.
"""

from typing import List, Dict, Any
from collections import defaultdict
from backend.models.schemas import Transaction, SubscriptionItem

def detect_subscriptions_and_recurring(transactions: List[Transaction]) -> List[SubscriptionItem]:
    """
    Groups transactions by merchant and analyzes amounts across months to detect recurring subscriptions/bills.
    """
    merchant_groups = defaultdict(list)
    for t in transactions:
        if t.type == "expense":
            merchant_clean = t.merchant.strip()
            merchant_groups[merchant_clean].append(t)

    subscriptions = []

    for merchant, txs in merchant_groups.items():
        # Sort by date
        txs_sorted = sorted(txs, key=lambda x: x.date)

        # Criteria for recurring:
        # 1. Marked is_recurring
        # 2. Or Category is 'Subscriptions' or 'Housing & Utilities' or 'Health & Fitness' or 'Software & Tools'
        # 3. Or appears in 2+ distinct months
        is_sub_cat = any(t.category in ["Subscriptions", "Housing & Utilities", "Health & Fitness", "Software & Tools"] for t in txs_sorted)
        explicit_rec = any(t.is_recurring for t in txs_sorted)
        
        months = set(t.date[:7] for t in txs_sorted) # YYYY-MM
        has_multi_month = len(months) >= 2

        if explicit_rec or is_sub_cat or (has_multi_month and len(txs_sorted) >= 2):
            latest_tx = txs_sorted[-1]
            prev_tx = txs_sorted[-2] if len(txs_sorted) >= 2 else None

            latest_amt = latest_tx.amount
            prev_amt = prev_tx.amount if prev_tx else latest_amt

            price_change_pct = 0.0
            status = "active"

            if prev_amt > 0 and latest_amt > prev_amt + 0.50: # Price hike detected!
                price_change_pct = round(((latest_amt - prev_amt) / prev_amt) * 100, 1)
                status = "price_hike"

            # Predict next due date (assume +30 days / next month same day)
            last_date_parts = latest_tx.date.split("-")
            if len(last_date_parts) == 3:
                year, month, day = int(last_date_parts[0]), int(last_date_parts[1]), int(last_date_parts[2])
                next_month = month + 1
                next_year = year
                if next_month > 12:
                    next_month = 1
                    next_year += 1
                next_due = f"{next_year:04d}-{next_month:02d}-{day:02d}"
            else:
                next_due = "2026-10-05"

            sub = SubscriptionItem(
                id=f"sub_{hash(merchant) % 100000:05d}",
                merchant=merchant,
                category=latest_tx.category,
                amount=latest_amt,
                frequency="monthly",
                last_billed=latest_tx.date,
                next_due=next_due,
                previous_amount=prev_amt if prev_amt != latest_amt else None,
                price_change_pct=price_change_pct,
                status=status
            )
            subscriptions.append(sub)

    # Sort subscriptions by amount descending
    subscriptions.sort(key=lambda x: x.amount, reverse=True)
    return subscriptions

def calculate_upcoming_obligations(subscriptions: List[SubscriptionItem], target_month: str = "2026-10") -> Dict[str, Any]:
    """
    Calculates total upcoming financial obligations for the specified target month.
    """
    total_committed = sum(s.amount for s in subscriptions)
    details = [
        {
            "merchant": s.merchant,
            "amount": s.amount,
            "next_due": s.next_due,
            "category": s.category,
            "status": s.status
        }
        for s in subscriptions
    ]
    return {
        "target_month": target_month,
        "total_committed": round(total_committed, 2),
        "count": len(subscriptions),
        "items": details
    }
