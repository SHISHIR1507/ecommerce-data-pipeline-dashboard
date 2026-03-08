"""
clean_data.py
-------------
Part 1 — Data Cleaning Pipeline

Reads raw CSVs from data/raw/, applies cleaning rules, and writes
cleaned outputs to data/processed/.

Usage:
    python clean_data.py
"""

import re
import logging
import pathlib

import pandas as pd

# ---------------------------------------------------------------------------
# Configuration — no hardcoded absolute paths
# ---------------------------------------------------------------------------
BASE_DIR = pathlib.Path(__file__).parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data loading with error handling
# ---------------------------------------------------------------------------
def load_csv(filepath: pathlib.Path) -> pd.DataFrame:
    """Load a CSV with error handling for missing or empty files."""
    try:
        df = pd.read_csv(filepath)
        if df.empty:
            raise pd.errors.EmptyDataError(f"{filepath.name} is empty")
        logger.info("Loaded %s — %d rows, %d columns", filepath.name, len(df), len(df.columns))
        return df
    except FileNotFoundError:
        logger.error("File not found: %s", filepath)
        raise
    except pd.errors.EmptyDataError:
        logger.error("Empty data file: %s", filepath)
        raise


# ---------------------------------------------------------------------------
# Email validation helper
# ---------------------------------------------------------------------------
def is_valid_email(email: str) -> bool:
    """Return True if the email contains '@' and at least one '.' after '@'."""
    if not isinstance(email, str) or not email:
        return False
    return bool(re.match(r"^[^@]+@[^@]+\.[^@]+$", email))


# ---------------------------------------------------------------------------
# 1.1  Clean customers.csv
# ---------------------------------------------------------------------------
def clean_customers(df: pd.DataFrame) -> pd.DataFrame:
    """Apply all cleaning rules to the customers dataset."""
    report = {"rows_before": len(df)}

    # --- Deduplicate by customer_id, keep latest signup_date ---------------
    # First parse signup_date so we can sort properly
    df["signup_date"] = pd.to_datetime(df["signup_date"], errors="coerce", format="%Y-%m-%d")
    unparseable_dates = df["signup_date"].isna().sum()
    if unparseable_dates:
        logger.warning(
            "customers — %d unparseable signup_date values replaced with NaT",
            unparseable_dates,
        )

    df = df.sort_values("signup_date", ascending=False, na_position="last")
    duplicates_before = df.duplicated(subset=["customer_id"], keep="first").sum()
    df = df.drop_duplicates(subset=["customer_id"], keep="first").reset_index(drop=True)
    report["duplicates_removed"] = duplicates_before

    # --- Strip whitespace from name and region -----------------------------
    df["name"] = df["name"].astype(str).str.strip()
    df["region"] = df["region"].astype(str).str.strip()

    # --- Fill missing region with 'Unknown' --------------------------------
    df["region"] = df["region"].replace({"": "Unknown", "nan": "Unknown", "None": "Unknown"})

    # --- Standardize emails to lowercase; flag invalid ---------------------
    df["email"] = df["email"].astype(str).str.strip().str.lower()
    df["email"] = df["email"].replace({"": pd.NA, "nan": pd.NA})
    df["is_valid_email"] = df["email"].apply(
        lambda x: is_valid_email(x) if pd.notna(x) else False
    )

    # --- Format signup_date as YYYY-MM-DD string ---------------------------
    # (keep NaT for unparseable values)

    report["rows_after"] = len(df)
    report["nulls_after"] = df.isnull().sum().to_dict()

    return df, report


# ---------------------------------------------------------------------------
# 1.2  Multi-format date parser
# ---------------------------------------------------------------------------
def parse_date(val) -> pd.Timestamp:
    """Try multiple date formats; return NaT if none match."""
    if pd.isna(val) or str(val).strip() == "":
        return pd.NaT
    val_str = str(val).strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m-%d-%Y"):
        try:
            return pd.to_datetime(val_str, format=fmt)
        except (ValueError, TypeError):
            continue
    logger.warning("orders — unparseable order_date: '%s'", val_str)
    return pd.NaT


# ---------------------------------------------------------------------------
# Status normalization mapping
# ---------------------------------------------------------------------------
STATUS_MAP = {
    "completed": "completed",
    "done": "completed",
    "pending": "pending",
    "cancelled": "cancelled",
    "canceled": "cancelled",
    "refunded": "refunded",
}


# ---------------------------------------------------------------------------
# 1.2  Clean orders.csv
# ---------------------------------------------------------------------------
def clean_orders(df: pd.DataFrame) -> pd.DataFrame:
    """Apply all cleaning rules to the orders dataset."""
    report = {
        "rows_before": len(df),
        "nulls_before": df.isnull().sum().to_dict(),
    }

    # --- Drop rows where BOTH customer_id and order_id are null ------------
    mask_unrecoverable = df["customer_id"].isna() & df["order_id"].isna()
    # Also catch empty strings
    mask_unrecoverable |= (
        (df["customer_id"].astype(str).str.strip() == "") &
        (df["order_id"].astype(str).str.strip() == "")
    )
    rows_dropped = mask_unrecoverable.sum()
    df = df[~mask_unrecoverable].reset_index(drop=True)
    report["rows_dropped"] = int(rows_dropped)

    # --- Parse order_date with custom multi-format parser ------------------
    df["order_date"] = df["order_date"].apply(parse_date)

    # --- Fill missing amount with median grouped by product ----------------
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    product_medians = df.groupby("product")["amount"].transform("median")
    df["amount"] = df["amount"].fillna(product_medians)

    # --- Normalize status to controlled vocabulary -------------------------
    df["status"] = (
        df["status"]
        .astype(str)
        .str.strip()
        .str.lower()
        .map(STATUS_MAP)
        .fillna("pending")  # fallback for any unmapped value
    )

    # --- Derive order_year_month -------------------------------------------
    df["order_year_month"] = df["order_date"].dt.to_period("M").astype(str)

    report["rows_after"] = len(df)
    report["nulls_after"] = df.isnull().sum().to_dict()

    return df, report


# ---------------------------------------------------------------------------
# Cleaning report printer
# ---------------------------------------------------------------------------
def print_report(name: str, report: dict) -> None:
    """Print a human-readable cleaning summary."""
    print(f"\n{'='*60}")
    print(f"  Cleaning Report — {name}")
    print(f"{'='*60}")
    print(f"  Rows before cleaning : {report.get('rows_before', 'N/A')}")
    print(f"  Rows after cleaning  : {report.get('rows_after', 'N/A')}")
    if "duplicates_removed" in report:
        print(f"  Duplicate rows removed: {report['duplicates_removed']}")
    if "rows_dropped" in report:
        print(f"  Unrecoverable rows dropped: {report['rows_dropped']}")
    if "nulls_before" in report:
        print("  Null counts BEFORE:")
        for col, cnt in report["nulls_before"].items():
            print(f"    {col:25s}: {cnt}")
    if "nulls_after" in report:
        print("  Null counts AFTER:")
        for col, cnt in report["nulls_after"].items():
            print(f"    {col:25s}: {cnt}")
    print(f"{'='*60}\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # --- Customers ---------------------------------------------------------
    customers_raw = load_csv(RAW_DIR / "customers.csv")
    customers_clean, cust_report = clean_customers(customers_raw)
    customers_clean.to_csv(PROCESSED_DIR / "customers_clean.csv", index=False)
    print_report("customers.csv", cust_report)
    logger.info("Saved customers_clean.csv (%d rows)", len(customers_clean))

    # --- Orders ------------------------------------------------------------
    orders_raw = load_csv(RAW_DIR / "orders.csv")
    orders_clean, ord_report = clean_orders(orders_raw)
    orders_clean.to_csv(PROCESSED_DIR / "orders_clean.csv", index=False)
    print_report("orders.csv", ord_report)
    logger.info("Saved orders_clean.csv (%d rows)", len(orders_clean))


if __name__ == "__main__":
    main()
