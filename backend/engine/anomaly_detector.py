"""
Anomaly & Spike Detector Engine for FinPilot
Detects category spending surges, single high-value transactions, subscription price increases, and duplicate charges.
"""

from typing import List, Dict, Any
from collections import defaultdict
from backend.models.schemas import Transaction, AnomalyAlert, SubscriptionItem

def detect_anomalies(transactions: List[Transaction], subscriptions: List[SubscriptionItem], current_month: str = "2026-09") -> List[AnomalyAlert]:
    alerts = []

    # Filter transactions for current month vs prior months
    curr_txs = [t for t in transactions if t.date.startswith(current_month) and t.type == "expense"]
    prior_txs = [t for t in transactions if not t.date.startswith(current_month) and t.type == "expense"]

    # 1. Detect Subscription Price Hikes
    for sub in subscriptions:
        if sub.status == "price_hike" or (sub.price_change_pct and sub.price_change_pct > 5.0):
            alerts.append(AnomalyAlert(
                id=f"alt_sub_{sub.id}",
                type="price_hike",
                title=f"Price Hike Detected: {sub.merchant}",
                description=f"{sub.merchant} increased from ${sub.previous_amount:.2f} to ${sub.amount:.2f} (+{sub.price_change_pct}%).",
                amount=sub.amount,
                category=sub.category,
                severity="high" if sub.price_change_pct > 20 else "medium",
                date=sub.last_billed,
                action_suggested=f"Review if you still use {sub.merchant} or consider downgrading/canceling."
            ))

    # 2. Detect Category Spending Spikes (compare current month category total vs baseline)
    curr_cat_totals = defaultdict(float)
    for t in curr_txs:
        curr_cat_totals[t.category] += t.amount

    prior_cat_totals = defaultdict(list)
    for t in prior_txs:
        m = t.date[:7]
        prior_cat_totals[t.category].append((m, t.amount))

    # Aggregate prior month averages
    prior_cat_avg = {}
    for cat, items in prior_cat_totals.items():
        month_sums = defaultdict(float)
        for m, amt in items:
            month_sums[m] += amt
        if month_sums:
            prior_cat_avg[cat] = sum(month_sums.values()) / len(month_sums)

    for cat, curr_tot in curr_cat_totals.items():
        if cat in prior_cat_avg and prior_cat_avg[cat] > 0:
            avg = prior_cat_avg[cat]
            diff = curr_tot - avg
            pct_inc = (diff / avg) * 100
            if diff >= 100.0 and pct_inc >= 40.0:
                alerts.append(AnomalyAlert(
                    id=f"alt_spike_{cat.lower().replace(' ', '_')}",
                    type="spike",
                    title=f"Spending Spike in {cat}",
                    description=f"{cat} spending reached ${curr_tot:.2f} this month, up {pct_inc:.0f}% compared to your average of ${avg:.2f}.",
                    amount=curr_tot,
                    category=cat,
                    severity="high" if pct_inc > 80 else "medium",
                    date=f"{current_month}-15",
                    action_suggested=f"Check recent transactions in {cat} for non-essential purchases."
                ))

    # 3. High-Value Single Outlier Transactions (> $350 for non-housing/non-income)
    for t in curr_txs:
        if t.category not in ["Housing & Utilities", "Childcare & Education"] and t.amount >= 350.0:
            alerts.append(AnomalyAlert(
                id=f"alt_outlier_{t.id}",
                type="unusual_merchant",
                title=f"Large Expense: {t.merchant}",
                description=f"Single purchase of ${t.amount:.2f} at {t.merchant} on {t.date}.",
                amount=t.amount,
                category=t.category,
                severity="medium",
                date=t.date,
                action_suggested="Verify if this was a planned one-time major purchase."
            ))

    # 4. Duplicate Charges on Same Day & Same Amount
    tx_by_day_amt = defaultdict(list)
    for t in curr_txs:
        key = (t.date, t.merchant, t.amount)
        tx_by_day_amt[key].append(t)

    for (d, merch, amt), duplicates in tx_by_day_amt.items():
        if len(duplicates) > 1:
            alerts.append(AnomalyAlert(
                id=f"alt_dup_{duplicates[0].id}",
                type="duplicate",
                title=f"Potential Duplicate Charge: {merch}",
                description=f"Found {len(duplicates)} identical charges of ${amt:.2f} on {d} for {merch}.",
                amount=amt,
                category=duplicates[0].category,
                severity="high",
                date=d,
                action_suggested="Contact merchant or credit card provider to dispute duplicate billing."
            ))

    return alerts
