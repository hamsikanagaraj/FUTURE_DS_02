# Data Science & Analytics – Task 2: Customer Retention & Churn Analysis (2026)
**By [Future Interns](https://futureinterns.com/)**  
**Project:** SaaSify Cloud Solutions – Customer Retention & Churn Intelligence  
**Role:** Data Science & Analytics Intern / Senior Retention Analyst  

---

## 📌 Executive Overview
This project delivers a real-world, enterprise-grade customer retention and churn analysis for a subscription-based SaaS platform (**SaaSify Cloud Solutions**). We analyze **8,500 customer records** across **24 monthly signup cohorts (Jan 2024 – Dec 2025)** to answer the core business questions that founders, product managers, and growth teams care about:
1. **Why are customers leaving the platform?** *(Root cause telemetry & exit reason financial modeling)*
2. **Which customer segments are most likely to churn?** *(Segment, plan, billing cycle, and engagement risk profiling)*
3. **How long do customers typically stay active?** *(24-month longitudinal cohort matrix & survival probability decay curves)*
4. **What actions can improve customer retention?** *(Machine learning feature importance & 4 actionable retention playbooks)*

---

## 🚀 Key Project Deliverables

| Deliverable | File Path | Description |
| :--- | :--- | :--- |
| **Interactive Intelligence Dashboard** | [`dashboard/index.html`](file:///c:/Users/DELL/OneDrive/Documents/task2/dashboard/index.html) | Modern dark-mode web application featuring real-time KPI cards, interactive 24-cohort heatmap, ML churn driver charts, what-if ROI simulator, and account risk explorer. |
| **Executive Excel Model** | [`data/excel/SaaS_Customer_Retention_and_Churn_Analysis.xlsx`](file:///c:/Users/DELL/OneDrive/Documents/task2/data/excel/SaaS_Customer_Retention_and_Churn_Analysis.xlsx) | Professional 5-tab workbook with Executive Summary, Color-coded Cohort Matrix, ML weights, Segment economics, and Customer data. |
| **Executive Markdown Report** | [`reports/Executive_Retention_Churn_Report.md`](file:///c:/Users/DELL/OneDrive/Documents/task2/reports/Executive_Retention_Churn_Report.md) | In-depth strategic report tailored for PMs, Founders, and Business Stakeholders. |
| **Styled Printable HTML Report** | [`reports/Executive_Retention_Churn_Report.html`](file:///c:/Users/DELL/OneDrive/Documents/task2/reports/Executive_Retention_Churn_Report.html) | Beautiful, print-ready executive report with KPI cards, tables, and strategy cards. |
| **Cleaned Customer Dataset** | [`data/processed/saas_customer_churn_cleaned.csv`](file:///c:/Users/DELL/OneDrive/Documents/task2/data/processed/saas_customer_churn_cleaned.csv) | 8,500 cleaned and feature-engineered customer records with predictive risk probabilities. |
| **Cohort Retention Matrix** | [`data/processed/cohort_retention_matrix.csv`](file:///c:/Users/DELL/OneDrive/Documents/task2/data/processed/cohort_retention_matrix.csv) | Month 0 to Month 12 retention rates across 24 signup cohorts. |
| **Machine Learning Churn Drivers** | [`data/processed/churn_drivers_feature_importance.csv`](file:///c:/Users/DELL/OneDrive/Documents/task2/data/processed/churn_drivers_feature_importance.csv) | Feature weights and odds ratios from Random Forest and Logistic Regression models. |

---

## 📊 Summary of Analytical Findings

### 1. High-Level Performance Metrics
* **Total Monitored Customers:** 8,500 accounts
* **Active Customer Base:** 4,903 accounts (57.7%) | **Active MRR:** $1,749,276 ($20.99M ARR)
* **Churned Customer Base:** 3,597 accounts (42.3%) | **Lost MRR:** $630,741 ($7.57M Lost ARR)
* **Gross Revenue Retention (GRR):** 73.5% *(Target: >85%)*
* **Net Revenue Retention (NRR):** 104.2% *(Positive net expansion in mature cohorts)*
* **Average Customer Lifetime Value (LTV):** $3,894 (Enterprise: $14,667 | Pro: $2,757 | Starter: $565)
* **ARR at Immediate Risk:** **$2,163,768 ARR** across 1,009 active accounts with >65% churn probability.

### 2. The Cohort "Onboarding Cliff"
* **Month 1 to Month 4 Drop-off:** Retention drops from 100% to 70.9%. **57.9% of all customer churn occurs within the first 90 days**.
* **The 6-Month Stabilization:** Accounts that survive past Month 6 exhibit an **89.2% probability** of remaining active through Year 1.

### 3. Top Churn Root Causes by Lost ARR
1. **Poor Product Fit / Low Usage:** $3,768,600 ARR (52.1% of churned accounts, avg lifespan 2.1 months)
2. **Competitor Switched:** $1,078,714 ARR (15.8% of churned accounts, avg lifespan 9.4 months)
3. **Customer Support Unresponsive:** $971,911 ARR (13.1% of churned accounts, avg CSAT 2.1/5.0)
4. **Missing Key Integrations:** $662,170 ARR (8.1% of churned accounts)
5. **High Price / Budget Cuts:** $574,114 ARR (6.9% of churned accounts)
6. **Payment / Involuntary Dunning Failure:** $513,384 ARR (4.0% of churned accounts)

### 4. Machine Learning Predictive Churn Drivers (ROC-AUC: 0.8073)
* **Monthly Billing Contract:** 20.8% weight (OR: 2.14, +114% churn likelihood vs Annual).
* **Incomplete Onboarding:** 20.7% weight (OR: 2.82, +182% churn likelihood vs Guided Onboarding).
* **Monthly Active Usage:** 16.9% weight (OR: 0.42, protective factor).
* **Customer Satisfaction (CSAT):** 6.7% weight (OR: 0.56, protective factor).
* **Payment Dunning Failures:** 4.1% weight (OR: 2.68, accounts with 2+ failed retries have 74% churn probability).

---

## 🎯 Strategic Retention Playbook

```
+-----------------------------------------------------------------------------------------------+
| Play 1: Fix Onboarding Cliff    ==> Interactive checklists + Day 14 CS alerts  ==> +$237.4K ARR |
| Play 2: Month 2 Annual Switch   ==> 15% discount for healthy accounts at Day 45 ==> +$101.8K ARR |
| Play 3: Smart Involuntary Retry ==> Stripe/Recurly dunning + card expiry alerts ==> +$154.0K ARR |
| Play 4: CS SLA for CSAT < 3.0   ==> 24-hour executive outreach for low scores   ==> +$98.0K ARR  |
+-----------------------------------------------------------------------------------------------+
| TOTAL PROTECTED REVENUE IMPACT: +$591,150 ARR Saved | GRR Lift: 73.5% -> 78.4% (+4.9%)        |
+-----------------------------------------------------------------------------------------------+
```

---

## 💻 How to Run & Reproduce the Analysis

### 1. Requirements
Ensure Python 3.10+ is installed with the required libraries:
```bash
pip install pandas numpy scikit-learn openpyxl matplotlib seaborn
```

### 2. Execute Data Pipeline
Run the scripts in sequence:
```bash
# Step 1: Generate realistic raw dataset
python scripts/generate_saas_dataset.py

# Step 2: Clean and validate data, engineer features
python scripts/data_cleaning.py

# Step 3: Run longitudinal cohort analysis and survival curves
python scripts/cohort_retention_analysis.py

# Step 4: Train Random Forest churn model and extract feature drivers
python scripts/churn_drivers_analysis.py

# Step 5: Export multi-tab formatted Excel model
python scripts/export_excel_workbook.py

# Step 6: Bundle processed data for the interactive dashboard
python scripts/prepare_dashboard_data.py
```

### 3. Launch Interactive Dashboard
To launch the interactive dashboard locally:
```bash
cd dashboard
python -m http.server 5173
```
Open your browser and navigate to: **`http://localhost:5173`**

---

## 📁 Repository Structure
```
task2/
├── README.md                                  <-- Project overview & documentation
├── data/
│   ├── raw/
│   │   └── saas_customer_churn_raw.csv        <-- 8,500 raw customer records
│   ├── processed/
│   │   ├── saas_customer_churn_cleaned.csv    <-- Cleaned & risk-scored dataset
│   │   ├── cohort_retention_matrix.csv        <-- 24-cohort M0-M12 retention rates
│   │   ├── churn_drivers_feature_importance.csv<-- ML feature importances & odds ratios
│   │   ├── segment_metrics.csv                <-- Economics by segment (SMB/Mid-Market/Ent)
│   │   ├── churn_reasons_breakdown.csv        <-- Lost ARR by departure reason
│   │   ├── survival_analysis.csv              <-- Lifespan survival curve
│   │   └── churn_summary_kpis.json            <-- Aggregated executive JSON
│   └── excel/
│       └── SaaS_Customer_Retention_and_Churn_Analysis.xlsx <-- Formatted multi-tab model
├── scripts/
│   ├── generate_saas_dataset.py               <-- Generates realistic raw telemetry
│   ├── data_cleaning.py                       <-- Cleans, audits, and engineers features
│   ├── cohort_retention_analysis.py           <-- Longitudinal cohort analysis
│   ├── churn_drivers_analysis.py              <-- Random Forest & LogReg modeling
│   ├── export_excel_workbook.py               <-- OpenPyXL Excel model builder
│   └── prepare_dashboard_data.py             <-- Bundles dashboard data
├── dashboard/
│   ├── index.html                             <-- Interactive retention dashboard
│   ├── style.css                              <-- Dark mode glassmorphic stylesheet
│   ├── app.js                                 <-- Chart.js logic & dynamic simulator
│   └── data.js                                <-- Packaged analytics data bundle
└── reports/
    ├── Executive_Retention_Churn_Report.md    <-- Executive report for leadership
    └── Executive_Retention_Churn_Report.html  <-- Styled printable executive presentation
```

---
*Created for Future Interns – Data Science & Analytics Internship Task 2 (2026).*
