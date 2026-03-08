import re
import logging
import pathlib

import pandas as pd

BASE_DIR = pathlib.Path(__file__).parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

STATUS_MAP = {
    "completed": "completed",
    "done": "completed",
    "pending": "pending",
    "cancelled": "cancelled",
    "canceled": "cancelled",
    "refunded": "refunded",
}


def load_csv(filepath: pathlib.Path) -> pd.DataFrame:
    try:
        df = pd.read_csv(filepath)
        if df.empty:
            raise pd.errors.EmptyDataError(f"{filepath.name} is empty")
        logger.info("Loaded %s — %d rows", filepath.name, len(df))
        return df
    except FileNotFoundError:
        logger.error("File not found: %s", filepath)
        raise
    except pd.errors.EmptyDataError:
        logger.error("Empty file: %s", filepath)
        raise


def is_valid_email(email: str) -> bool:
    if not isinstance(email, str) or not email:
        return False
    return bool(re.match(r"^[^@]+@[^@]+\.[^@]+$", email))


def parse_date(val) -> pd.Timestamp:
    if pd.isna(val) or str(val).strip() == "":
        return pd.NaT
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m-%d-%Y"):
        try:
            return pd.to_datetime(str(val).strip(), format=fmt)
        except (ValueError, TypeError):
            continue
    logger.warning("Unparseable order_date: '%s'", val)
    return pd.NaT


def clean_customers(df: pd.DataFrame):
    report = {"rows_before": len(df)}

    df["signup_date"] = pd.to_datetime(df["signup_date"], errors="coerce", format="%Y-%m-%d")
    bad_dates = df["signup_date"].isna().sum()
    if bad_dates:
        logger.warning("%d unparseable signup_date values set to NaT", bad_dates)

    df = df.sort_values("signup_date", ascending=False, na_position="last")
    dupes = df.duplicated(subset=["customer_id"], keep="first").sum()
    df = df.drop_duplicates(subset=["customer_id"], keep="first").reset_index(drop=True)
    report["duplicates_removed"] = dupes

    df["name"] = df["name"].astype(str).str.strip()
    df["region"] = df["region"].astype(str).str.strip()
    df["region"] = df["region"].replace({"": "Unknown", "nan": "Unknown", "None": "Unknown"})

    df["email"] = df["email"].astype(str).str.strip().str.lower()
    df["email"] = df["email"].replace({"": pd.NA, "nan": pd.NA})
    df["is_valid_email"] = df["email"].apply(lambda x: is_valid_email(x) if pd.notna(x) else False)

    report["rows_after"] = len(df)
    report["nulls_after"] = df.isnull().sum().to_dict()
    return df, report


def clean_orders(df: pd.DataFrame):
    report = {
        "rows_before": len(df),
        "nulls_before": df.isnull().sum().to_dict(),
    }

    unrecoverable = (
        (df["customer_id"].astype(str).str.strip() == "") &
        (df["order_id"].astype(str).str.strip() == "")
    ) | (df["customer_id"].isna() & df["order_id"].isna())
    report["rows_dropped"] = int(unrecoverable.sum())
    df = df[~unrecoverable].reset_index(drop=True)

    df["order_date"] = df["order_date"].apply(parse_date)

    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df["amount"] = df["amount"].fillna(df.groupby("product")["amount"].transform("median"))

    df["status"] = (
        df["status"].astype(str).str.strip().str.lower()
        .map(STATUS_MAP)
        .fillna("pending")
    )

    df["order_year_month"] = df["order_date"].dt.to_period("M").astype(str)

    report["rows_after"] = len(df)
    report["nulls_after"] = df.isnull().sum().to_dict()
    return df, report


def print_report(name: str, report: dict) -> None:
    print(f"\nCleaning Report — {name}")
    print(f"  Rows before : {report.get('rows_before')}")
    print(f"  Rows after  : {report.get('rows_after')}")
    if "duplicates_removed" in report:
        print(f"  Duplicates removed : {report['duplicates_removed']}")
    if "rows_dropped" in report:
        print(f"  Unrecoverable rows dropped : {report['rows_dropped']}")
    if "nulls_before" in report:
        print("  Null counts before:")
        for col, cnt in report["nulls_before"].items():
            print(f"    {col}: {cnt}")
    if "nulls_after" in report:
        print("  Null counts after:")
        for col, cnt in report["nulls_after"].items():
            print(f"    {col}: {cnt}")


def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    customers_raw = load_csv(RAW_DIR / "customers.csv")
    customers_clean, cust_report = clean_customers(customers_raw)
    customers_clean.to_csv(PROCESSED_DIR / "customers_clean.csv", index=False)
    print_report("customers.csv", cust_report)
    logger.info("Saved customers_clean.csv (%d rows)", len(customers_clean))

    orders_raw = load_csv(RAW_DIR / "orders.csv")
    orders_clean, ord_report = clean_orders(orders_raw)
    orders_clean.to_csv(PROCESSED_DIR / "orders_clean.csv", index=False)
    print_report("orders.csv", ord_report)
    logger.info("Saved orders_clean.csv (%d rows)", len(orders_clean))


if __name__ == "__main__":
    main()
