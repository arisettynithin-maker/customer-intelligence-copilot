# Customer Intelligence Copilot

Customer Intelligence Copilot is a Streamlit analytics app that turns raw transaction data into executive-friendly customer insights. It helps teams quickly understand churn risk, customer value, segmentation opportunities, and next-best growth experiments from a single CSV upload.

## What This Project Shows

- End-to-end analytics product thinking, from messy data intake to business recommendations
- Clean customer feature engineering for recency, frequency, spend, tenure, and repeat behavior
- Practical retention and revenue analysis that is easy to explain in interviews and demos
- A polished multi-page Streamlit experience designed to feel like a premium internal business tool

## Core Features

- Upload your own transaction CSV or use the built-in demo dataset
- Automatically map common source column variations such as `CustomerID`, `Invoice`, `InvoiceDate`, `Amount`, and `Sales`
- Validate and clean raw data before analysis
- Explore churn risk with configurable inactivity thresholds
- Estimate historical and near-term customer value
- Segment customers into business-friendly groups
- Generate plain-English executive insights and recommended experiments
- Download processed customer-level summaries for further analysis

## Dashboards Included

- Executive Overview
- Churn Risk
- LTV and Customer Value
- Segmentation
- Experiments and Recommendations
- Data Quality and Assumptions
- Ask the Data

## Tech Stack

- Python
- Streamlit
- Pandas
- NumPy
- Plotly

## How It Works

1. Launch the app.
2. Use the demo data or upload a transaction CSV.
3. Let the app standardize, clean, and validate the dataset.
4. Review the dashboards for customer health, revenue concentration, and segment opportunities.
5. Export the processed customer summary if needed.

## Run Locally

```bash
git clone https://github.com/arisettynithin-maker/customer-intelligence-copilot.git
cd customer-intelligence-copilot
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Deploy Online

This project is ready for Streamlit Community Cloud:

1. Push this repository to GitHub.
2. Go to Streamlit Community Cloud.
3. Create a new app from this repository.
4. Set the main file path to `app.py`.

Once deployed, you can place that public app link on LinkedIn so people can open and use the application directly.

## Sample Input

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

The app also supports retail-style source files with columns like `Invoice`, `Customer ID`, `InvoiceDate`, `Quantity`, and `Price`.

## Repository Structure

```text
customer-intelligence-copilot/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── data/sample/
├── pages/
└── src/
```

## Why It Matters

This project is built to demonstrate more than dashboard creation. It shows how raw customer transaction data can be transformed into a usable decision-support product with clear business value, thoughtful UX, and strong portfolio presentation.
