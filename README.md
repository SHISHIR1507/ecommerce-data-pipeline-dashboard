# Ecommerce Data Pipeline & Dashboard

This project is a full-stack data engineering and visualization solution. It demonstrates an end-to-end pipeline: generating raw data, cleaning it with Pandas, merging datasets for business intelligence, serving the results via a FastAPI backend, and visualizing them in a responsive React (Vite + Tailwind) dashboard.

## Overview of Components

1. **Data Generation** (`generate_data.py`): Creates intentionally messy raw CSVs (`customers.csv`, `orders.csv`, `products.csv`) to simulate real-world data issues.
2. **Data Cleaning** (`clean_data.py`): A Pandas pipeline that handles schema validation, deduplication, missing value imputation (e.g. median substitution), date parsing, and regex email validation. Outputs clean CSVs and cleaning reports.
3. **Data Analysis** (`analyze.py`): Merges the cleaned datasets using left joins to produce aggregated business metrics (monthly revenue, top customers, category performance, regional analysis) saved as CSVs.
4. **Backend API** (`backend/main.py`): A FastAPI application that serves the processed data via RESTful JSON endpoints.
5. **Frontend Dashboard** (`frontend/`): A modern React application built with Vite, Tailwind CSS v4, and Recharts. It features interactive KPI cards, sortable/searchable tables, and charts with date filtering.

## Setup Instructions

### Prerequisites
- Python 3.9+
- Node.js 18+
- Docker & Docker Compose (optional, for containerized backend)

### 1. Data Pipeline Execution

First, generate the raw data:
```bash
python generate_data.py
```

Clean the data:
```bash
python clean_data.py
```

Run the analysis to generate summary datasets:
```bash
python analyze.py
```
*Note: Make sure the `data/processed/` folder contains exactly 6 CSV files before starting the backend.*

### 2. Running Locally

**Backend (Terminal 1):**
```bash
pip install -r backend/requirements.txt
python -m uvicorn backend.main:app --port 8000
```
*The API will be available at http://localhost:8000. Check the health endpoint at `/health`.*

**Frontend (Terminal 2):**
```bash
cd frontend
npm install
npm run dev
```
*Visit the dashboard at the URL provided by Vite (usually http://localhost:5173).*

### 3. Running Backend with Docker (Optional)

You can run the FastAPI backend via Docker instead of running it locally.

```bash
# From the project root directory
docker-compose up --build
```
*This mounts the `data/processed` folder into the container so the API can read the CSVs you generated locally.*

## Testing

Unit tests cover the core Pandas data cleaning logic (testing deduplication, imputation, and status normalization).

```bash
pip install pytest
pytest tests/test_clean_data.py -v
```

## Assumptions & Design Decisions
- **Data Persistence**: CSVs were chosen over a database like SQLite or PostgreSQL to keep the assignment portable and self-contained, strictly adhering to the requirements.
- **Data Cleaning Strategy**: 
    - Missing order amounts are imputed using the *median* of that product's category to avoid skew from outliers.
    - Invalid emails are flagged (`is_valid_email`) rather than dropped, as dropping them could result in losing critical transaction data.
    - Duplicate customers are resolved by keeping the row with the most recent `signup_date`.
- **Backend Architecture**: FastAPI naturally handles async requests and provides built-in Swagger UI (`/docs`). Data is loaded dynamically per request to ensure fresh reads, though caching could be added for scale.
- **Frontend State**: Filtering (Search, Date ranges) is done client-side inside `App.jsx` for speed, given the aggregated BI datasets are small enough. In a production app with raw data, this would be pushed down to the API.
