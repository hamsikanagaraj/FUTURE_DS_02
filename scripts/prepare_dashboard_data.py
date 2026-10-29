"""
Script: prepare_dashboard_data.py
Description: Compiles all analytical outputs (KPIs, cohort matrix, survival curve,
             churn reasons, segment metrics, and customer account table) into a single
             clean data bundle (dashboard/data.js) for the interactive dashboard.
"""

import pandas as pd
import json

def prepare_data():
    with open("data/processed/churn_summary_kpis.json", "r") as f:
        kpis = json.load(f)
        
    cohort_df = pd.read_csv("data/processed/cohort_retention_matrix.csv")
    survival_df = pd.read_csv("data/processed/survival_analysis.csv")
    fi_df = pd.read_csv("data/processed/churn_drivers_feature_importance.csv")
    df_clean = pd.read_csv("data/processed/saas_customer_churn_cleaned.csv")
    
    # Replace NaNs in cohort_df with null for clean JSON
    cohort_records = cohort_df.where(pd.notnull(cohort_df), None).to_dict(orient="records")
    survival_records = survival_df.to_dict(orient="records")
    fi_records = fi_df.to_dict(orient="records")
    
    # Sample 600 records for the client-side interactive table (balanced active, churned, high risk)
    high_risk_active = df_clean[(df_clean["churn_status"] == "Active") & (df_clean["churn_risk_tier"] == "High Risk")].head(200)
    churned_sample = df_clean[df_clean["churn_status"] == "Churned"].head(200)
    healthy_sample = df_clean[(df_clean["churn_status"] == "Active") & (df_clean["churn_risk_tier"] == "Low Risk")].head(200)
    
    combined_sample = pd.concat([high_risk_active, churned_sample, healthy_sample]).sample(frac=1.0, random_state=42)
    
    table_cols = [
        "customer_id", "subscription_plan", "customer_segment", "billing_cycle",
        "mrr", "tenure_months", "onboarding_completed", "usage_frequency_days_per_month",
        "support_satisfaction_score", "payment_failures_count", "churn_status",
        "churn_reason", "churn_risk_probability", "churn_risk_tier", "total_lifetime_revenue"
    ]
    customer_records = combined_sample[table_cols].where(pd.notnull(combined_sample[table_cols]), "").to_dict(orient="records")
    
    bundle = {
        "kpis": kpis,
        "cohortMatrix": cohort_records,
        "survivalCurve": survival_records,
        "featureImportance": fi_records,
        "customerAccounts": customer_records
    }
    
    # Save as JSON and JS
    json_path = "data/processed/dashboard_data.json"
    with open(json_path, "w") as f:
        json.dump(bundle, f, indent=2)
        
    js_path = "dashboard/data.js"
    with open(js_path, "w") as f:
        f.write("const RETENTION_DATA = " + json.dumps(bundle, indent=2) + ";\n")
        
    print(f"Dashboard data bundled to {json_path} and {js_path}")

if __name__ == "__main__":
    prepare_data()
