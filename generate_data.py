"""
generate_data.py
----------------
Generates realistic but intentionally dirty CSV datasets for the
ecommerce data pipeline assignment.

Outputs:
    data/raw/customers.csv
    data/raw/orders.csv
    data/raw/products.csv
"""

import csv
import random
import pathlib
from datetime import datetime, timedelta

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
RAW_DIR = pathlib.Path(__file__).parent / "data" / "raw"
NUM_CUSTOMERS = 120
NUM_ORDERS = 500
SEED = 42

random.seed(SEED)

# ---------------------------------------------------------------------------
# Helper data
# ---------------------------------------------------------------------------
FIRST_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh",
    "Ayaan", "Krishna", "Ishaan", "Ananya", "Diya", "Myra", "Sara",
    "Aadhya", "Isha", "Kiara", "Riya", "Priya", "Neha", "Rahul", "Amit",
    "Deepak", "Suresh", "Mohan", "Lakshmi", "Gita", "Meera", "Pooja",
    "Kavya", "Rohan", "Karan", "Nikhil", "Sneha", "Tanvi",
]

LAST_NAMES = [
    "Sharma", "Verma", "Gupta", "Singh", "Kumar", "Patel", "Mehta",
    "Joshi", "Rao", "Nair", "Pillai", "Iyer", "Reddy", "Chopra",
    "Malhotra", "Bansal", "Agarwal", "Bhat", "Sinha", "Das",
]

REGIONS = ["North", "South", "East", "West", None]  # None → missing region

DOMAINS = ["gmail.com", "yahoo.com", "outlook.com", "company.co", "mail.in"]

PRODUCTS = [
    ("P001", "Wireless Mouse", "Electronics", 599.00),
    ("P002", "Mechanical Keyboard", "Electronics", 2499.00),
    ("P003", "USB-C Hub", "Electronics", 1299.00),
    ("P004", "Desk Lamp", "Home & Office", 899.00),
    ("P005", "Notebook Pack", "Stationery", 199.00),
    ("P006", "Ergonomic Chair", "Furniture", 12999.00),
    ("P007", "Monitor Stand", "Furniture", 2199.00),
    ("P008", "Webcam HD", "Electronics", 3499.00),
    ("P009", "Whiteboard Marker Set", "Stationery", 149.00),
    ("P010", "Standing Desk Mat", "Home & Office", 1599.00),
    ("P011", "Cable Organizer", "Home & Office", 349.00),
    ("P012", "Portable Charger", "Electronics", 1799.00),
    # Two products that will NOT appear in any order → tests "no match" path
    ("P013", "VR Headset", "Electronics", 34999.00),
    ("P014", "Smart Pen", "Stationery", 4999.00),
]

STATUS_VARIANTS = [
    "completed", "Completed", "COMPLETED", "done", "Done",
    "pending", "Pending", "PENDING",
    "cancelled", "Cancelled", "canceled", "Canceled", "CANCELLED",
    "refunded", "Refunded", "REFUNDED",
]

DATE_FORMATS = ["%Y-%m-%d", "%d/%m/%Y", "%m-%d-%Y"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _random_date(start: datetime, end: datetime) -> datetime:
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


def _make_email(first: str, last: str, malform: bool = False) -> str:
    """Return a valid email or, if malform=True, a broken one."""
    if malform:
        # Randomly return email without '@' or without '.'
        choice = random.choice(["no_at", "no_dot"])
        if choice == "no_at":
            return f"{first.lower()}{last.lower()}.com"
        return f"{first.lower()}@{last.lower()}"
    domain = random.choice(DOMAINS)
    return f"{first.lower()}.{last.lower()}@{domain}"


# ---------------------------------------------------------------------------
# Generate customers.csv
# ---------------------------------------------------------------------------
def generate_customers() -> list[dict]:
    rows: list[dict] = []
    start = datetime(2021, 1, 1)
    end = datetime(2025, 12, 31)

    for i in range(1, NUM_CUSTOMERS + 1):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        cid = f"C{i:04d}"

        # ~8 % chance of missing email, ~7 % chance of malformed email
        r = random.random()
        if r < 0.08:
            email = ""
        elif r < 0.15:
            email = _make_email(first, last, malform=True)
        else:
            email = _make_email(first, last)
            # Randomly uppercase some emails to test lowercasing
            if random.random() < 0.3:
                email = email.upper()

        # Add whitespace noise to name/region
        name = f"  {first} {last}  " if random.random() < 0.2 else f"{first} {last}"
        region = random.choice(REGIONS)
        if region and random.random() < 0.15:
            region = f"  {region} "

        # Signup date — occasionally unparseable
        if random.random() < 0.05:
            signup = "not-a-date"
        else:
            signup = _random_date(start, end).strftime("%Y-%m-%d")

        rows.append({
            "customer_id": cid,
            "name": name,
            "email": email,
            "region": region if region else "",
            "signup_date": signup,
        })

    # Inject ~10 duplicate rows (same customer_id, different signup_date)
    for _ in range(10):
        orig = random.choice(rows[:NUM_CUSTOMERS])
        dup = dict(orig)
        dup["signup_date"] = _random_date(start, end).strftime("%Y-%m-%d")
        rows.append(dup)

    random.shuffle(rows)
    return rows


# ---------------------------------------------------------------------------
# Generate orders.csv
# ---------------------------------------------------------------------------
def generate_orders() -> list[dict]:
    rows: list[dict] = []
    start = datetime(2023, 1, 1)
    end = datetime(2025, 11, 30)

    # Only use products P001–P012 in orders (P013, P014 stay unmatched)
    order_products = [p[1] for p in PRODUCTS[:12]]

    customer_ids = [f"C{i:04d}" for i in range(1, NUM_CUSTOMERS + 1)]

    for i in range(1, NUM_ORDERS + 1):
        oid = f"O{i:05d}"
        cid = random.choice(customer_ids)
        product = random.choice(order_products)
        amount = round(random.uniform(149, 35000), 2)
        status = random.choice(STATUS_VARIANTS)

        # Date in a random format
        fmt = random.choice(DATE_FORMATS)
        order_date = _random_date(start, end).strftime(fmt)

        # ~6 % chance amount is null
        if random.random() < 0.06:
            amount = ""

        rows.append({
            "order_id": oid,
            "customer_id": cid,
            "product": product,
            "amount": amount,
            "order_date": order_date,
            "status": status,
        })

    # Inject 3 rows where both customer_id and order_id are null
    for _ in range(3):
        rows.append({
            "order_id": "",
            "customer_id": "",
            "product": random.choice(order_products),
            "amount": round(random.uniform(149, 5000), 2),
            "order_date": _random_date(start, end).strftime("%Y-%m-%d"),
            "status": "pending",
        })

    # Inject 5 rows with customer_id pointing to non-existent customer
    for idx in range(5):
        rows.append({
            "order_id": f"O{NUM_ORDERS + 1 + idx:05d}",
            "customer_id": f"C{9900 + idx:04d}",
            "product": random.choice(order_products),
            "amount": round(random.uniform(149, 5000), 2),
            "order_date": _random_date(start, end).strftime("%Y-%m-%d"),
            "status": "completed",
        })

    random.shuffle(rows)
    return rows


# ---------------------------------------------------------------------------
# Generate products.csv
# ---------------------------------------------------------------------------
def generate_products() -> list[dict]:
    return [
        {
            "product_id": pid,
            "product_name": name,
            "category": cat,
            "unit_price": price,
        }
        for pid, name, cat, price in PRODUCTS
    ]


# ---------------------------------------------------------------------------
# Write helpers
# ---------------------------------------------------------------------------
def _write_csv(filepath: pathlib.Path, rows: list[dict]) -> None:
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"  ✓ Written {len(rows)} rows → {filepath}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    print("Generating raw datasets …")
    _write_csv(RAW_DIR / "customers.csv", generate_customers())
    _write_csv(RAW_DIR / "orders.csv", generate_orders())
    _write_csv(RAW_DIR / "products.csv", generate_products())
    print("Done. Files saved in", RAW_DIR)


if __name__ == "__main__":
    main()
