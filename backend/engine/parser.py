import csv
import io
import json
import uuid
from typing import List, Dict, Any
from backend.models.schemas import Transaction
from backend.engine.categorizer import categorize_transaction

def parse_csv_content(content_str: str, account_name: str = "Uploaded Account") -> List[Transaction]:
    """
    Parses CSV string content into a list of Transaction objects.
    Handles flexible column naming.
    """
    lines = [line.strip() for line in content_str.splitlines() if line.strip()]
    if not lines:
        return []

    reader = csv.DictReader(lines)
    fieldnames = [f.lower().strip() for f in (reader.fieldnames or [])]
    
    # Map column headers flexibly
    date_col = next((f for f in reader.fieldnames if any(k in f.lower() for k in ["date", "time", "posted"])), None)
    merchant_col = next((f for f in reader.fieldnames if any(k in f.lower() for k in ["merchant", "description", "payee", "name", "narrative", "details"])), None)
    amount_col = next((f for f in reader.fieldnames if any(k in f.lower() for k in ["amount", "debit", "price", "val"])), None)
    category_col = next((f for f in reader.fieldnames if any(k in f.lower() for k in ["category", "type", "group"])), None)

    transactions = []
    for idx, row in enumerate(reader):
        date_val = row.get(date_col, "2026-09-01") if date_col else "2026-09-01"
        merchant_val = row.get(merchant_col, "Unknown Merchant") if merchant_col else "Unknown Merchant"
        
        # Parse amount
        raw_amt = row.get(amount_col, "0.0") if amount_col else "0.0"
        try:
            # Clean currency symbols
            clean_amt = str(raw_amt).replace("$", "").replace(",", "").strip()
            amount_val = float(clean_amt)
        except ValueError:
            amount_val = 0.0

        # Determine type & category
        is_income = amount_val < 0 or "salary" in merchant_val.lower() or "deposit" in merchant_val.lower() or "paycheck" in merchant_val.lower() or "payout" in merchant_val.lower()
        if is_income and amount_val > 0:
            amount_val = -amount_val # Standardize income as negative in calculation or handle explicitly

        given_cat = row.get(category_col, None) if category_col else None
        cat = categorize_transaction(merchant_val, amount_val, given_cat)

        tx_type = "income" if is_income or cat == "Income" else "expense"

        t = Transaction(
            id=f"tx_up_{uuid.uuid4().hex[:8]}",
            date=str(date_val).strip(),
            merchant=str(merchant_val).strip(),
            amount=abs(amount_val) if tx_type == "expense" else -abs(amount_val),
            category=cat,
            type=tx_type,
            source="csv_upload",
            account=account_name
        )
        transactions.append(t)

    return transactions

def parse_json_content(content_str: str, account_name: str = "Uploaded Account") -> List[Transaction]:
    """
    Parses JSON array into Transaction objects.
    """
    data = json.loads(content_str)
    if isinstance(data, dict) and "transactions" in data:
        data = data["transactions"]
    
    transactions = []
    for item in data:
        merchant = item.get("merchant") or item.get("description") or "Unknown Merchant"
        date_str = item.get("date", "2026-09-01")
        amount = float(item.get("amount", 0.0))
        cat = item.get("category") or categorize_transaction(merchant, amount)
        tx_type = item.get("type") or ("income" if cat == "Income" or amount < 0 else "expense")

        t = Transaction(
            id=item.get("id") or f"tx_up_{uuid.uuid4().hex[:8]}",
            date=date_str,
            merchant=merchant,
            amount=abs(amount) if tx_type == "expense" else -abs(amount),
            category=cat,
            type=tx_type,
            source="json_upload",
            account=account_name
        )
        transactions.append(t)
    return transactions

def parse_text_bill(text_str: str) -> Transaction:
    """
    Parses raw bill text or receipt text into a single Transaction object.
    """
    lines = [l.strip() for l in text_str.splitlines() if l.strip()]
    merchant = lines[0] if lines else "Vendor Bill"
    amount = 0.0
    date_str = "2026-09-20"

    for line in lines:
        if any(kw in line.lower() for kw in ["total", "due", "amount", "balance"]):
            # Extract numbers
            words = line.replace("$", " ").split()
            for w in words:
                try:
                    val = float(w.replace(",", ""))
                    if val > 0:
                        amount = val
                        break
                except ValueError:
                    continue

    cat = categorize_transaction(merchant, amount)
    return Transaction(
        id=f"tx_bill_{uuid.uuid4().hex[:8]}",
        date=date_str,
        merchant=merchant,
        amount=amount,
        category=cat,
        type="expense",
        source="bill_parse"
    )
