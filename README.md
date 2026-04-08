# Customer Intelligence Copilot

AI-powered customer analytics application built to turn transaction data into decision-ready insight across churn, lifetime value, segmentation, experimentation, and data quality review.

Live app: https://customer-intelligence-copilot.streamlit.app/

## Project Overview

Customer analytics often lives across static dashboards, spreadsheet analysis, and ad hoc interpretation. This project brings those workflows together in a single application that helps teams move from raw transactions to practical customer decisions faster.

The app combines analytical modelling, business-focused visualisation, and AI-assisted interpretation in a recruiter-friendly example of how analytics work can be packaged as a usable product.

## Business Problem

Teams often know they need to improve retention, customer value, and growth, but the path from raw transaction data to action is slow:

- churn risk is hard to detect early
- customer value is unevenly distributed
- segmentation work is repeated manually
- experiment recommendations are not consistently connected to the data

This creates delay between analysis and action.

## Solution / Approach

This project turns customer transaction data into a guided decision-support workflow:

- standardises and prepares transactional data
- evaluates churn risk and customer value
- segments customers into meaningful groups
- surfaces business insights and recommended actions
- adds an AI-powered "Ask the Data" layer for faster interpretation

The result is an analytics product that feels closer to a decision tool than a static dashboard.

## Tech Stack

- Python
- Streamlit
- Pandas
- Plotly
- LLM-powered analytics interactions

## Key Features

- Executive overview of customer performance
- Churn risk analysis
- LTV and value distribution analysis
- Customer segmentation
- Experiment recommendation layer
- Data quality checks
- AI-powered "Ask the Data" workflow

## Outputs / App Screenshots

### Home

![Home](./screenshots/Home%20Page.png)

### Executive Overview

![Executive Overview](./screenshots/Executive%20Overview.png)

### Churn Risk

![Churn Risk](./screenshots/Churn%20Risk.png)

### LTV and Value

![LTV and Value](./screenshots/LTV%20and%20Value.png)

### Segmentation

![Segmentation](./screenshots/Segmentation.png)

### Experiment Recommendations

![Experiments](./screenshots/Experiments.png)

### Data Quality

![Data Quality](./screenshots/Data%20Quality.png)

### Ask the Data

![Ask the Data](./screenshots/Ask%20the%20Data.png)

## Business Impact / Insights

Using the included retail dataset, the app demonstrates how analytics can move from description to decision support:

- highlights revenue concentration across top-value customers
- identifies customers at risk of churn
- surfaces dormant and recoverable segments
- supports retention and experimentation prioritisation
- reduces manual effort needed to convert transaction data into actionable insight

This is the kind of product thinking that can make analytics more useful to commercial, growth, and customer teams.

## Repository Structure

```text
.
├── README.md
├── app.py
├── requirements.txt
├── pages/
│   ├── 1_Executive_Overview.py
│   ├── 2_Churn_Risk.py
│   ├── 3_LTV_and_Value.py
│   ├── 4_Segmentation.py
│   ├── 5_Experiments.py
│   ├── 6_Data_Quality.py
│   └── 7_Ask_the_Data.py
├── src/
│   ├── ask_data.py
│   ├── churn.py
│   ├── data_prep.py
│   ├── feature_engineering.py
│   ├── insights.py
│   ├── ltv.py
│   ├── recommendations.py
│   ├── segmentation.py
│   └── utils.py
└── screenshots/
```

## How to Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Future Improvements

- add model performance reporting for churn scoring
- support direct CSV upload validation feedback
- extend experiment recommendations with prioritisation scoring
- add deployment-ready configuration for broader demo use
