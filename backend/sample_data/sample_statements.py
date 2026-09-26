"""
Sample Datasets for FinPilot Decision Support Agent
Contains realistic financial transaction data spanning 3 months.
"""

TECH_PROFESSIONAL_DATA = {
    "profile_name": "Tech Professional",
    "description": "Monthly salary, subscriptions, dining out, Amazon purchases, and recurring bills.",
    "budgets": [
        {"category": "Housing & Utilities", "allocated_amount": 1800.0},
        {"category": "Food & Dining", "allocated_amount": 600.0},
        {"category": "Groceries", "allocated_amount": 450.0},
        {"category": "Subscriptions", "allocated_amount": 120.0},
        {"category": "Shopping", "allocated_amount": 350.0},
        {"category": "Transportation", "allocated_amount": 250.0},
        {"category": "Entertainment", "allocated_amount": 200.0},
        {"category": "Health & Fitness", "allocated_amount": 100.0},
    ],
    "goals": [
        {
            "id": "g1",
            "name": "Emergency Fund",
            "target_amount": 10000.0,
            "current_savings": 6500.0,
            "monthly_contribution": 500.0,
            "target_date": "2027-04-01",
            "category": "Savings"
        },
        {
            "id": "g2",
            "name": "Japan Summer Trip",
            "target_amount": 3500.0,
            "current_savings": 1400.0,
            "monthly_contribution": 300.0,
            "target_date": "2027-07-01",
            "category": "Travel"
        }
    ],
    "transactions": [
        # --- SEPTEMBER 2026 ---
        {"id": "t101", "date": "2026-09-01", "merchant": "Acme Corp Salary", "amount": -4800.00, "category": "Income", "type": "income", "source": "direct_deposit"},
        {"id": "t102", "date": "2026-09-01", "merchant": "Apex Apartments Rent", "amount": 1650.00, "category": "Housing & Utilities", "type": "expense", "source": "ach", "is_recurring": True},
        {"id": "t103", "date": "2026-09-02", "merchant": "City Power & Light", "amount": 124.50, "category": "Housing & Utilities", "type": "expense", "source": "bill", "is_recurring": True},
        {"id": "t104", "date": "2026-09-03", "merchant": "Whole Foods Market", "amount": 142.80, "category": "Groceries", "type": "expense", "source": "card"},
        {"id": "t105", "date": "2026-09-04", "merchant": "Netflix Subscription", "amount": 19.99, "category": "Subscriptions", "type": "expense", "source": "card", "is_recurring": True}, # PRICE HIKE FROM $15.49
        {"id": "t106", "date": "2026-09-05", "merchant": "Spotify Premium", "amount": 10.99, "category": "Subscriptions", "type": "expense", "source": "card", "is_recurring": True},
        {"id": "t107", "date": "2026-09-06", "merchant": "Equinox Fitness Gym", "amount": 85.00, "category": "Health & Fitness", "type": "expense", "source": "card", "is_recurring": True},
        {"id": "t108", "date": "2026-09-07", "merchant": "Uber Rides", "amount": 34.20, "category": "Transportation", "type": "expense", "source": "card"},
        {"id": "t109", "date": "2026-09-08", "merchant": "Chipotle Mexican Grill", "amount": 18.45, "category": "Food & Dining", "type": "expense", "source": "card"},
        {"id": "t110", "date": "2026-09-10", "merchant": "Trader Joe's", "amount": 115.30, "category": "Groceries", "type": "expense", "source": "card"},
        {"id": "t111", "date": "2026-09-12", "merchant": "Amazon.com Tech Purchase", "amount": 429.00, "category": "Shopping", "type": "expense", "source": "card"}, # UNUSUAL SPIKE
        {"id": "t112", "date": "2026-09-14", "merchant": "Sushi Izakaya Dinner", "amount": 128.50, "category": "Food & Dining", "type": "expense", "source": "card"},
        {"id": "t113", "date": "2026-09-15", "merchant": "Acme Corp Salary", "amount": -4800.00, "category": "Income", "type": "income", "source": "direct_deposit"},
        {"id": "t114", "date": "2026-09-16", "merchant": "Verizon Wireless", "amount": 85.00, "category": "Housing & Utilities", "type": "expense", "source": "bill", "is_recurring": True},
        {"id": "t115", "date": "2026-09-17", "merchant": "ChatGPT Plus", "amount": 20.00, "category": "Subscriptions", "type": "expense", "source": "card", "is_recurring": True},
        {"id": "t116", "date": "2026-09-18", "merchant": "Blue Bottle Coffee", "amount": 28.40, "category": "Food & Dining", "type": "expense", "source": "card"},
        {"id": "t117", "date": "2026-09-20", "merchant": "Whole Foods Market", "amount": 168.90, "category": "Groceries", "type": "expense", "source": "card"},
        {"id": "t118", "date": "2026-09-22", "merchant": "Steam Games", "amount": 59.99, "category": "Entertainment", "type": "expense", "source": "card"},
        {"id": "t119", "date": "2026-09-24", "merchant": "Sweetgreen", "amount": 22.10, "category": "Food & Dining", "type": "expense", "source": "card"},
        {"id": "t120", "date": "2026-09-25", "merchant": "DoorDash Delivery", "amount": 64.80, "category": "Food & Dining", "type": "expense", "source": "card"},

        # --- AUGUST 2026 ---
        {"id": "t201", "date": "2026-08-01", "merchant": "Acme Corp Salary", "amount": -4800.00, "category": "Income", "type": "income", "source": "direct_deposit"},
        {"id": "t202", "date": "2026-08-01", "merchant": "Apex Apartments Rent", "amount": 1650.00, "category": "Housing & Utilities", "type": "expense", "source": "ach", "is_recurring": True},
        {"id": "t203", "date": "2026-08-02", "merchant": "City Power & Light", "amount": 118.20, "category": "Housing & Utilities", "type": "expense", "source": "bill", "is_recurring": True},
        {"id": "t204", "date": "2026-08-04", "merchant": "Netflix Subscription", "amount": 15.49, "category": "Subscriptions", "type": "expense", "source": "card", "is_recurring": True},
        {"id": "t205", "date": "2026-08-05", "merchant": "Spotify Premium", "amount": 10.99, "category": "Subscriptions", "type": "expense", "source": "card", "is_recurring": True},
        {"id": "t206", "date": "2026-08-06", "merchant": "Equinox Fitness Gym", "amount": 85.00, "category": "Health & Fitness", "type": "expense", "source": "card", "is_recurring": True},
        {"id": "t207", "date": "2026-08-07", "merchant": "Trader Joe's", "amount": 134.50, "category": "Groceries", "type": "expense", "source": "card"},
        {"id": "t208", "date": "2026-08-10", "merchant": "Chipotle Mexican Grill", "amount": 17.50, "category": "Food & Dining", "type": "expense", "source": "card"},
        {"id": "t209", "date": "2026-08-12", "merchant": "Amazon.com", "amount": 45.20, "category": "Shopping", "type": "expense", "source": "card"},
        {"id": "t210", "date": "2026-08-15", "merchant": "Acme Corp Salary", "amount": -4800.00, "category": "Income", "type": "income", "source": "direct_deposit"},
        {"id": "t211", "date": "2026-08-16", "merchant": "Verizon Wireless", "amount": 85.00, "category": "Housing & Utilities", "type": "expense", "source": "bill", "is_recurring": True},
        {"id": "t212", "date": "2026-08-17", "merchant": "ChatGPT Plus", "amount": 20.00, "category": "Subscriptions", "type": "expense", "source": "card", "is_recurring": True},
        {"id": "t213", "date": "2026-08-20", "merchant": "Whole Foods Market", "amount": 155.00, "category": "Groceries", "type": "expense", "source": "card"},
        {"id": "t214", "date": "2026-08-24", "merchant": "Ramen Noodle Bar", "amount": 38.50, "category": "Food & Dining", "type": "expense", "source": "card"},

        # --- JULY 2026 ---
        {"id": "t301", "date": "2026-07-01", "merchant": "Acme Corp Salary", "amount": -4800.00, "category": "Income", "type": "income", "source": "direct_deposit"},
        {"id": "t302", "date": "2026-07-01", "merchant": "Apex Apartments Rent", "amount": 1650.00, "category": "Housing & Utilities", "type": "expense", "source": "ach", "is_recurring": True},
        {"id": "t303", "date": "2026-07-02", "merchant": "City Power & Light", "amount": 110.00, "category": "Housing & Utilities", "type": "expense", "source": "bill", "is_recurring": True},
        {"id": "t304", "date": "2026-07-04", "merchant": "Netflix Subscription", "amount": 15.49, "category": "Subscriptions", "type": "expense", "source": "card", "is_recurring": True},
        {"id": "t305", "date": "2026-07-05", "merchant": "Spotify Premium", "amount": 10.99, "category": "Subscriptions", "type": "expense", "source": "card", "is_recurring": True},
        {"id": "t306", "date": "2026-07-06", "merchant": "Equinox Fitness Gym", "amount": 85.00, "category": "Health & Fitness", "type": "expense", "source": "card", "is_recurring": True},
        {"id": "t307", "date": "2026-07-15", "merchant": "Acme Corp Salary", "amount": -4800.00, "category": "Income", "type": "income", "source": "direct_deposit"},
        {"id": "t308", "date": "2026-07-16", "merchant": "Verizon Wireless", "amount": 85.00, "category": "Housing & Utilities", "type": "expense", "source": "bill", "is_recurring": True},
        {"id": "t309", "date": "2026-07-17", "merchant": "ChatGPT Plus", "amount": 20.00, "category": "Subscriptions", "type": "expense", "source": "card", "is_recurring": True},
        {"id": "t310", "date": "2026-07-20", "merchant": "Trader Joe's", "amount": 140.00, "category": "Groceries", "type": "expense", "source": "card"},
    ]
}

FAMILY_HOUSEHOLD_DATA = {
    "profile_name": "Family Household",
    "description": "Mortgage, daycare, family groceries, utilities, streaming services, and home maintenance.",
    "budgets": [
        {"category": "Housing & Utilities", "allocated_amount": 2800.0},
        {"category": "Childcare & Education", "allocated_amount": 1400.0},
        {"category": "Groceries", "allocated_amount": 900.0},
        {"category": "Subscriptions", "allocated_amount": 150.0},
        {"category": "Transportation", "allocated_amount": 400.0},
        {"category": "Shopping", "allocated_amount": 500.0},
    ],
    "goals": [
        {
            "id": "fg1",
            "name": "College Fund",
            "target_amount": 25000.0,
            "current_savings": 14000.0,
            "monthly_contribution": 600.0,
            "target_date": "2028-09-01",
            "category": "Education"
        }
    ],
    "transactions": [
        {"id": "ft101", "date": "2026-09-01", "merchant": "Enterprise Corp Payroll", "amount": -6500.00, "category": "Income", "type": "income"},
        {"id": "ft102", "date": "2026-09-01", "merchant": "Freedom Mortgage", "amount": 2400.00, "category": "Housing & Utilities", "type": "expense", "is_recurring": True},
        {"id": "ft103", "date": "2026-09-02", "merchant": "Sunshine Daycare Center", "amount": 1350.00, "category": "Childcare & Education", "type": "expense", "is_recurring": True},
        {"id": "ft104", "date": "2026-09-04", "merchant": "Costco Wholesale", "amount": 345.60, "category": "Groceries", "type": "expense"},
        {"id": "ft105", "date": "2026-09-05", "merchant": "Disney+ / Hulu Bundle", "amount": 24.99, "category": "Subscriptions", "type": "expense", "is_recurring": True},
        {"id": "ft106", "date": "2026-09-07", "merchant": "Home Depot Repairs", "amount": 620.00, "category": "Shopping", "type": "expense"}, # SPIKE
        {"id": "ft107", "date": "2026-09-15", "merchant": "Enterprise Corp Payroll", "amount": -6500.00, "category": "Income", "type": "income"},
        {"id": "ft108", "date": "2026-09-18", "merchant": "Kroger Supermarket", "amount": 289.40, "category": "Groceries", "type": "expense"},
        {"id": "ft109", "date": "2026-09-20", "merchant": "State Farm Insurance", "amount": 210.00, "category": "Housing & Utilities", "type": "expense", "is_recurring": True},
    ]
}

FREELANCER_DATA = {
    "profile_name": "Freelancer & Consultant",
    "description": "Variable client revenue, office space, software tools (Adobe, GitHub, Zoom), tax savings, and travel.",
    "budgets": [
        {"category": "Software & Tools", "allocated_amount": 250.0},
        {"category": "Housing & Office", "allocated_amount": 1500.0},
        {"category": "Travel", "allocated_amount": 500.0},
        {"category": "Food & Dining", "allocated_amount": 400.0},
    ],
    "goals": [
        {
            "id": "flg1",
            "name": "Tax Reserve Fund",
            "target_amount": 12000.0,
            "current_savings": 8500.0,
            "monthly_contribution": 1000.0,
            "target_date": "2026-12-15",
            "category": "Taxes"
        }
    ],
    "transactions": [
        {"id": "fl101", "date": "2026-09-02", "merchant": "Stripe Client Payout (Client A)", "amount": -3200.00, "category": "Income", "type": "income"},
        {"id": "fl102", "date": "2026-09-03", "merchant": "WeWork Desk Space", "amount": 450.00, "category": "Housing & Office", "type": "expense", "is_recurring": True},
        {"id": "fl103", "date": "2026-09-05", "merchant": "Adobe Creative Cloud", "amount": 59.99, "category": "Software & Tools", "type": "expense", "is_recurring": True},
        {"id": "fl104", "date": "2026-09-06", "merchant": "GitHub Pro", "amount": 10.00, "category": "Software & Tools", "type": "expense", "is_recurring": True},
        {"id": "fl105", "date": "2026-09-10", "merchant": "Stripe Client Payout (Client B)", "amount": -4500.00, "category": "Income", "type": "income"},
        {"id": "fl106", "date": "2026-09-12", "merchant": "Zoom Video Communications", "amount": 15.99, "category": "Software & Tools", "type": "expense", "is_recurring": True},
        {"id": "fl107", "date": "2026-09-15", "merchant": "Delta Airlines Flight", "amount": 485.00, "category": "Travel", "type": "expense"},
    ]
}

DATASET_MAP = {
    "tech_pro": TECH_PROFESSIONAL_DATA,
    "family": FAMILY_HOUSEHOLD_DATA,
    "freelancer": FREELANCER_DATA
}
