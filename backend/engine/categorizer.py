"""
Categorization Engine for FinPilot
Maps merchant names and descriptions to standard financial categories.
"""

CATEGORY_KEYWORDS = {
    "Income": [
        "salary", "payroll", "direct deposit", "stipend", "payout", "client payment",
        "dividend", "interest payment", "bonus", "freelance income", "stripe payout"
    ],
    "Subscriptions": [
        "netflix", "spotify", "hulu", "disney", "apple.com/bill", "chatgpt", "openai",
        "youtube premium", "hbo", "max subscription", "prime video", "nyt", "newspaper",
        "patreon", "substack", "gym", "equinox", "fitness club", "icloud"
    ],
    "Housing & Utilities": [
        "rent", "apartments", "mortgage", "power & light", "power", "utility", "utilities", "electric", "water bill",
        "gas utility", "verizon", "att", "t-mobile", "xfinity", "spectrum", "internet",
        "state farm", "geico", "allstate", "insurance", "hoa fee"
    ],
    "Groceries": [
        "whole foods", "trader joe", "kroger", "safeway", "costco", "walmart",
        "target grocery", "supermarket", "aldi", "h-mart", "groceries", "fresh market"
    ],
    "Food & Dining": [
        "chipotle", "sweetgreen", "doordash", "ubereats", "grubhub", "starbucks",
        "blue bottle", "coffee", "ramen", "izakaya", "restaurant", "cafe", "bistro",
        "burger", "sushi", "pizza", "diner", "bar & grill", "bakery", "tacos"
    ],
    "Transportation": [
        "uber", "lyft", "chevron", "shell", "exxon", "gas station", "transit",
        "metro", "subway", "amtrak", "parking", "toll", "auto repair"
    ],
    "Shopping": [
        "amazon", "best buy", "apple store", "nike", "zara", "nordstrom",
        "home depot", "lowes", "ikea", "ebay", "clothing", "electronics"
    ],
    "Health & Fitness": [
        "equinox", "planet fitness", "cvs", "walgreens", "pharmacy", "clinic",
        "doctor", "dental", "optometry", "hospital", "gnc", "health"
    ],
    "Entertainment": [
        "steam games", "playstation", "xbox", "cinema", "amc theater", "concert",
        "ticketmaster", "bowling", "museum", "eventbrite"
    ],
    "Childcare & Education": [
        "daycare", "tuition", "school", "college fund", "babysitter", "nanny",
        "kids activity", "preschool"
    ],
    "Software & Tools": [
        "adobe", "github", "zoom", "aws", "gcp", "digitalocean", "slack",
        "notion", "figma", "godaddy", "jira", "atlassian"
    ],
    "Travel": [
        "delta airlines", "united airlines", "american airlines", "airbnb",
        "hotel", "booking.com", "expedia", "flight", "resort"
    ]
}

def categorize_transaction(merchant: str, amount: float = 0.0, user_category: str = None) -> str:
    """
    Categorizes a transaction based on merchant name, amount, or explicit user override.
    """
    if user_category and user_category.strip() and user_category != "Uncategorized":
        return user_category.strip()

    merchant_clean = merchant.lower().strip()

    # If amount is explicitly negative (income deposit) or merchant implies salary/payroll
    if amount < 0 and any(kw in merchant_clean for kw in ["salary", "payroll", "deposit", "payout"]):
        return "Income"

    # Match merchant against rules
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in merchant_clean:
                return cat

    return "Shopping" if amount > 50 else "Food & Dining"
