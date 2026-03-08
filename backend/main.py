import pathlib

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Ecommerce Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = pathlib.Path(__file__).parent.parent / "data" / "processed"


def read_csv(filename: str) -> list[dict]:
    path = DATA_DIR / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"{filename} not found")
    df = pd.read_csv(path)
    return df.to_dict(orient="records")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/revenue")
def get_revenue():
    return read_csv("monthly_revenue.csv")


@app.get("/api/top-customers")
def get_top_customers():
    return read_csv("top_customers.csv")


@app.get("/api/categories")
def get_categories():
    return read_csv("category_performance.csv")


@app.get("/api/regions")
def get_regions():
    return read_csv("regional_analysis.csv")
