# Ecommerce Data Pipeline & Dashboard

End-to-end data pipeline that ingests raw CSV datasets, cleans and transforms them with Python (pandas), performs business analysis, and surfaces results via a fullstack web application.

## Project Structure

```
├── generate_data.py          # Generates raw CSV datasets with realistic dirty data
├── clean_data.py             # Part 1 — Data cleaning pipeline
├── analyze.py                # Part 2 — Merging & business analysis
├── backend/                  # Part 3 — FastAPI REST API
├── frontend/                 # Part 3 — React dashboard
├── tests/                    # Pytest unit tests
├── data/
│   ├── raw/                  # Original CSVs (customers, orders, products)
│   └── processed/            # Cleaned and analysis output CSVs
└── README.md
```

## Quick Start

### 1. Generate Raw Data

```bash
python generate_data.py
```

This creates three intentionally dirty CSVs in `data/raw/`:
- `customers.csv` — 130 rows (includes duplicates, missing/malformed emails)
- `orders.csv` — 508 rows (mixed date formats, null amounts, status variants)
- `products.csv` — 14 products (some won't appear in orders)

### Prerequisites

- Python 3.9+
- pip
