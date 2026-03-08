import csv
import random
import pathlib
from datetime import datetime, timedelta

RAW_DIR = pathlib.Path(__file__).parent / "data" / "raw"
NUM_CUSTOMERS = 120
NUM_ORDERS = 500
SEED = 42

random.seed(SEED)

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

REGIONS = ["North", "South", "East", "West", None]

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


def random_date(start, end):
    return start + timedelta(days=random.randint(0, (end - start).days))


def make_email(first, last, malform=False):
    if malform:
        return f"{first.lower()}{last.lower()}.com" if random.random() < 0.5 else f"{first.lower()}@{last.lower()}"
    email = f"{first.lower()}.{last.lower()}@{random.choice(DOMAINS)}"
    return email.upper() if random.random() < 0.3 else email


def generate_customers():
    rows = []
    start, end = datetime(2021, 1, 1), datetime(2025, 12, 31)

    for i in range(1, NUM_CUSTOMERS + 1):
        first, last = random.choice(FIRST_NAMES), random.choice(LAST_NAMES)
        cid = f"C{i:04d}"

        r = random.random()
        if r < 0.08:
            email = ""
        elif r < 0.15:
            email = make_email(first, last, malform=True)
        else:
            email = make_email(first, last)

        name = f"  {first} {last}  " if random.random() < 0.2 else f"{first} {last}"
        region = random.choice(REGIONS)
        if region and random.random() < 0.15:
            region = f"  {region} "

        signup = "not-a-date" if random.random() < 0.05 else random_date(start, end).strftime("%Y-%m-%d")

        rows.append({"customer_id": cid, "name": name, "email": email or "",
                     "region": region or "", "signup_date": signup})

    for _ in range(10):
        dup = dict(random.choice(rows[:NUM_CUSTOMERS]))
        dup["signup_date"] = random_date(start, end).strftime("%Y-%m-%d")
        rows.append(dup)

    random.shuffle(rows)
    return rows


def generate_orders():
    rows = []
    start, end = datetime(2023, 1, 1), datetime(2025, 11, 30)
    order_products = [p[1] for p in PRODUCTS[:12]]
    customer_ids = [f"C{i:04d}" for i in range(1, NUM_CUSTOMERS + 1)]

    for i in range(1, NUM_ORDERS + 1):
        rows.append({
            "order_id": f"O{i:05d}",
            "customer_id": random.choice(customer_ids),
            "product": random.choice(order_products),
            "amount": "" if random.random() < 0.06 else round(random.uniform(149, 35000), 2),
            "order_date": random_date(start, end).strftime(random.choice(DATE_FORMATS)),
            "status": random.choice(STATUS_VARIANTS),
        })

    for _ in range(3):
        rows.append({
            "order_id": "", "customer_id": "",
            "product": random.choice(order_products),
            "amount": round(random.uniform(149, 5000), 2),
            "order_date": random_date(start, end).strftime("%Y-%m-%d"),
            "status": "pending",
        })

    for idx in range(5):
        rows.append({
            "order_id": f"O{NUM_ORDERS + 1 + idx:05d}",
            "customer_id": f"C{9900 + idx:04d}",
            "product": random.choice(order_products),
            "amount": round(random.uniform(149, 5000), 2),
            "order_date": random_date(start, end).strftime("%Y-%m-%d"),
            "status": "completed",
        })

    random.shuffle(rows)
    return rows


def generate_products():
    return [
        {"product_id": pid, "product_name": name, "category": cat, "unit_price": price}
        for pid, name, cat, price in PRODUCTS
    ]


def write_csv(filepath, rows):
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"Written {len(rows)} rows → {filepath}")


def main():
    print("Generating raw datasets...")
    write_csv(RAW_DIR / "customers.csv", generate_customers())
    write_csv(RAW_DIR / "orders.csv", generate_orders())
    write_csv(RAW_DIR / "products.csv", generate_products())


if __name__ == "__main__":
    main()
