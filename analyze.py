import logging
import pathlib

import pandas as pd

BASE_DIR = pathlib.Path(__file__).parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
RAW_DIR = BASE_DIR / "data" / "raw"

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


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


def merge_datasets(customers, orders, products):
    orders_with_customers = pd.merge(
        orders, customers, on="customer_id", how="left", suffixes=("", "_cust")
    )
    no_customer = orders_with_customers["name"].isna().sum()
    logger.info("Orders with no matching customer: %d", no_customer)

    full_data = pd.merge(
        orders_with_customers, products,
        left_on="product", right_on="product_name",
        how="left", suffixes=("", "_prod")
    )
    no_product = full_data["product_id"].isna().sum()
    logger.info("Orders with no matching product: %d", no_product)

    return full_data


def compute_monthly_revenue(df):
    completed = df[df["status"] == "completed"]
    return (
        completed
        .groupby("order_year_month", as_index=False)["amount"]
        .sum()
        .rename(columns={"amount": "total_revenue"})
        .sort_values("order_year_month")
    )


def compute_top_customers(df):
    completed = df[df["status"] == "completed"]
    return (
        completed
        .groupby(["customer_id", "name", "region"], as_index=False)["amount"]
        .sum()
        .rename(columns={"amount": "total_spend"})
        .sort_values("total_spend", ascending=False)
        .head(10)
    )


def add_churn_flag(top_customers, df):
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    latest_date = df["order_date"].max()
    cutoff = latest_date - pd.Timedelta(days=90)

    recent = df[(df["status"] == "completed") & (df["order_date"] >= cutoff)]
    active = set(recent["customer_id"].unique())

    top_customers["churned"] = ~top_customers["customer_id"].isin(active)
    logger.info("Churn cutoff: %s | Churned in top-10: %d",
                cutoff.strftime("%Y-%m-%d"), top_customers["churned"].sum())
    return top_customers


def compute_category_performance(df):
    completed = df[df["status"] == "completed"]
    result = (
        completed
        .groupby("category", as_index=False)
        .agg(
            total_revenue=("amount", "sum"),
            avg_order_value=("amount", "mean"),
            num_orders=("amount", "count"),
        )
        .sort_values("total_revenue", ascending=False)
    )
    result["avg_order_value"] = result["avg_order_value"].round(2)
    return result


def compute_regional_analysis(df, customers):
    completed = df[df["status"] == "completed"]

    cust_count = (
        customers
        .groupby("region", as_index=False)["customer_id"]
        .nunique()
        .rename(columns={"customer_id": "num_customers"})
    )

    region_orders = (
        completed
        .groupby("region", as_index=False)
        .agg(num_orders=("order_id", "count"), total_revenue=("amount", "sum"))
    )

    regional = pd.merge(cust_count, region_orders, on="region", how="left").fillna(0)
    regional["avg_revenue_per_customer"] = (regional["total_revenue"] / regional["num_customers"]).round(2)
    return regional.sort_values("total_revenue", ascending=False)


def main():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    customers = load_csv(PROCESSED_DIR / "customers_clean.csv")
    orders = load_csv(PROCESSED_DIR / "orders_clean.csv")
    products = load_csv(RAW_DIR / "products.csv")

    full_data = merge_datasets(customers, orders, products)

    monthly_rev = compute_monthly_revenue(full_data)
    monthly_rev.to_csv(PROCESSED_DIR / "monthly_revenue.csv", index=False)
    logger.info("Saved monthly_revenue.csv (%d rows)", len(monthly_rev))

    top_cust = compute_top_customers(full_data)
    top_cust = add_churn_flag(top_cust, full_data)
    top_cust.to_csv(PROCESSED_DIR / "top_customers.csv", index=False)
    logger.info("Saved top_customers.csv (%d rows)", len(top_cust))

    cat_perf = compute_category_performance(full_data)
    cat_perf.to_csv(PROCESSED_DIR / "category_performance.csv", index=False)
    logger.info("Saved category_performance.csv (%d rows)", len(cat_perf))

    regional = compute_regional_analysis(full_data, customers)
    regional.to_csv(PROCESSED_DIR / "regional_analysis.csv", index=False)
    logger.info("Saved regional_analysis.csv (%d rows)", len(regional))

    print("\nAll outputs saved to", PROCESSED_DIR)


if __name__ == "__main__":
    main()
