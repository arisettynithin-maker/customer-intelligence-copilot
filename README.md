# Customer Intelligence Copilot

Customer Intelligence Copilot is a polished Streamlit analytics app for exploring customer transaction data through the lens of churn risk, customer lifetime value, segmentation, and experiment design. It is positioned as a premium internal business tool for analysts, stakeholders, and recruiters reviewing portfolio-quality analytics work.

## Business Problem

Business teams often have transaction exports but lack a fast, executive-friendly way to understand:

- which customers are drifting toward churn
- where future revenue is concentrated
- which customer groups deserve retention, upsell, or activation effort
- what experiments should be prioritized next

This project closes that gap with a lightweight analytics workflow that starts from a CSV and turns it into a coherent decision-support dashboard.

## Features

- Flexible CSV upload with automatic mapping for common field variants such as `CustomerID`, `Invoice`, `InvoiceDate`, `Sales`, and `Amount`
- One-click demo mode powered by `data/sample/online_retail_II.csv` so visitors can explore the app instantly
- Data validation, cleaning, and quality reporting
- Customer-level feature engineering including recency, frequency, value, tenure, and days between orders
- Configurable inactivity-based churn logic for 30, 60, and 90 day definitions
- Historical and estimated 90-day customer value / LTV calculations
- Rule-based customer segmentation with business-friendly labels
- Executive insight generation using deterministic rules instead of an external LLM API
- Experiment recommendation cards tied directly to the observed data
- Guided `Ask the Data` page for deployment-friendly chat-with-data style business questions
- Premium Streamlit styling with rounded cards, strong spacing, modern typography, and dashboard polish
- Downloadable processed customer summary CSV

## Tech Stack

- Python
- Streamlit
- Pandas
- NumPy
- Plotly

## App Workflow

1. Open the app and either use built-in demo data or upload a transaction CSV.
2. Validate and map fields into a canonical schema.
3. Clean the data and produce a quality report.
4. Apply global filters such as date range, country, category, and source segment.
5. Explore the dashboards:
   - Executive Overview
   - Churn Risk
   - LTV and Customer Value
   - Segmentation
   - Experiments and Recommendations
   - Data Quality and Assumptions
   - Ask the Data
6. Export the processed customer summary for downstream analysis.

## Project Structure

```text
customer-intelligence-copilot/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── src/
│   ├── data_prep.py
│   ├── feature_engineering.py
│   ├── churn.py
│   ├── ltv.py
│   ├── segmentation.py
│   ├── recommendations.py
│   ├── insights.py
│   ├── ask_data.py
│   └── utils.py
├── pages/
│   ├── 1_Executive_Overview.py
│   ├── 2_Churn_Risk.py
│   ├── 3_LTV_and_Value.py
│   ├── 4_Segmentation.py
│   ├── 5_Experiments.py
│   ├── 6_Data_Quality.py
│   └── 7_Ask_the_Data.py
├── assets/
└── data/
    └── sample/
        ├── online_retail_II.csv
        └── sample_transactions.csv
```

## Screenshots

- `docs/screenshots/overview.png` placeholder
- `docs/screenshots/churn.png` placeholder
- `docs/screenshots/value.png` placeholder

## How To Run Locally

```bash
cd customer-intelligence-copilot
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Sample Input Format

Minimum required columns:

```csv
customer_id,order_id,order_date,revenue
C001,O1001,2025-01-10,120.50
C001,O1049,2025-02-02,88.00
C002,O1002,2025-01-11,54.25
```

Optional enrichment columns:

- `quantity`
- `product`
- `category`
- `country`
- `segment`
- `unit_price`

The app also supports raw retail transaction files like Online Retail II with columns such as:

- `Invoice` or `InvoiceNo`
- `Customer ID` or `CustomerID`
- `InvoiceDate`
- `Quantity`
- `Price` or `UnitPrice`

If a direct revenue column is missing, the app derives `revenue = quantity * unit_price`.

## Key Analytics Methods

- Inactivity-based churn: customers are flagged as churned when `recency_days` exceeds the selected threshold
- Customer value estimation: combines historical revenue, average order value, and observed purchase frequency to estimate near-term 90-day value
- Rule-based segmentation: uses transparent business logic instead of opaque clustering so results are easy to explain in interviews and stakeholder reviews
- Executive insight generation: plain-English summaries are generated from computed metrics such as churn rate, repeat purchase share, and revenue concentration

## Why This Project Matters

This project demonstrates more than dashboard assembly. It shows how to move from raw operational data to business recommendations in a single product-style workflow. For business teams, that means faster answers. For recruiters, it shows analytical thinking, product judgment, and the ability to package technical work in a stakeholder-friendly interface.
