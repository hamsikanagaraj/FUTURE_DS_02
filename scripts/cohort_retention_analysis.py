"""
Script: cohort_retention_analysis.py
Description: Computes monthly cohort retention matrices, survival curves,
             tenure distribution, and plan/contract retention benchmarks.
"""

import pandas as pd
import numpy as np
import os
import json
from datetime import datetime

def analyze_cohorts_and_retention(cleaned_csv_path):
    print("=" * 70)
    print("COHORT & RETENTION ANALYSIS")
    print("=" * 70)
    
    df = pd.read_csv(cleaned_csv_path)
    df["signup_date"] = pd.to_datetime(df["signup_date"])
    snapshot_date = pd.to_datetime("2026-03-31")
    
    # Calculate months since signup to snapshot
    df["months_since_signup"] = ((snapshot_date.year - df["signup_date"].dt.year) * 12 + 
                                 (snapshot_date.month - df["signup_date"].dt.month))
    
    # Generate Cohort Retention Matrix (Month 0 to Month 12)
    cohorts = sorted(df["cohort_month"].unique())
    max_periods = 13  # Month 0 to Month 12
    
    cohort_data = []
    
    for c in cohorts:
        cohort_df = df[df["cohort_month"] == c]
        cohort_size = len(cohort_df)
        months_elapsed = cohort_df["months_since_signup"].iloc[0]
        
        row = {
            "Cohort": c,
            "Cohort_Size": cohort_size
        }
        
        for m in range(max_periods):
            if m > months_elapsed:
                row[f"M{m}"] = np.nan
            else:
                # Active at month m if tenure_months >= m
                # (For active customers, tenure_months equals months_elapsed >= m)
                active_count = (cohort_df["tenure_months"] >= m).sum()
                retention_rate = round((active_count / cohort_size) * 100, 1)
                row[f"M{m}"] = retention_rate
                
        cohort_data.append(row)
        
    cohort_matrix_df = pd.DataFrame(cohort_data)
    cohort_matrix_path = "data/processed/cohort_retention_matrix.csv"
    cohort_matrix_df.to_csv(cohort_matrix_path, index=False)
    print(f"\nCohort Retention Matrix saved to: {cohort_matrix_path}")
    print(cohort_matrix_df.head(6))
    
    # Calculate Overall Benchmark Retention Curve across all mature cohorts (at least 12 months mature)
    mature_cohorts = cohort_matrix_df.dropna(subset=["M12"])
    m_cols = [f"M{i}" for i in range(max_periods)]
    benchmark_curve = mature_cohorts[m_cols].mean().round(2).to_dict()
    print("\nBenchmark SaaS Retention Curve (Average across mature cohorts):")
    for k, v in benchmark_curve.items():
        print(f"  {k}: {v}%")
        
    # Retention by Plan
    print("\n" + "=" * 70)
    print("RETENTION BY SUBSCRIPTION PLAN")
    print("=" * 70)
    plan_retention = df.groupby("subscription_plan").agg(
        Total_Customers=("customer_id", "count"),
        Active_Customers=("is_churned", lambda x: (x == 0).sum()),
        Churned_Customers=("is_churned", "sum"),
        Churn_Rate=("is_churned", lambda x: round(x.mean() * 100, 2)),
        Avg_Tenure_Months=("tenure_months", lambda x: round(x.mean(), 1)),
        Median_Tenure=("tenure_months", "median"),
        Total_MRR=("mrr", "sum"),
        Avg_LTV=("total_lifetime_revenue", lambda x: round(x.mean(), 2))
    ).reset_index()
    plan_retention["Retention_Rate"] = (100 - plan_retention["Churn_Rate"]).round(2)
    print(plan_retention)
    
    # Retention by Billing Cycle
    print("\n" + "=" * 70)
    print("RETENTION BY BILLING CYCLE")
    print("=" * 70)
    cycle_retention = df.groupby("billing_cycle").agg(
        Total_Customers=("customer_id", "count"),
        Churn_Rate=("is_churned", lambda x: round(x.mean() * 100, 2)),
        Avg_Tenure_Months=("tenure_months", lambda x: round(x.mean(), 1)),
        Avg_LTV=("total_lifetime_revenue", lambda x: round(x.mean(), 2))
    ).reset_index()
    cycle_retention["Retention_Rate"] = (100 - cycle_retention["Churn_Rate"]).round(2)
    print(cycle_retention)
    
    # Retention by Onboarding Completion
    print("\n" + "=" * 70)
    print("RETENTION BY ONBOARDING STATUS")
    print("=" * 70)
    onboard_retention = df.groupby("onboarding_completed").agg(
        Total_Customers=("customer_id", "count"),
        Churn_Rate=("is_churned", lambda x: round(x.mean() * 100, 2)),
        Avg_Tenure_Months=("tenure_months", lambda x: round(x.mean(), 1)),
        Avg_LTV=("total_lifetime_revenue", lambda x: round(x.mean(), 2))
    ).reset_index()
    onboard_retention["Retention_Rate"] = (100 - onboard_retention["Churn_Rate"]).round(2)
    print(onboard_retention)
    
    # Survival Distribution (Lifespan probability)
    tenure_counts = df["tenure_months"].value_counts().sort_index()
    total_cust = len(df)
    survival_curve = []
    active_pool = total_cust
    for m in range(1, int(df["tenure_months"].max()) + 1):
        churned_at_m = len(df[(df["tenure_months"] == m) & (df["is_churned"] == 1)])
        active_at_least_m = len(df[df["tenure_months"] >= m])
        pct_surviving = round((active_at_least_m / total_cust) * 100, 2)
        survival_curve.append({
            "month": m,
            "survival_pct": pct_surviving,
            "active_count": active_at_least_m,
            "churned_at_month": churned_at_m
        })
        
    survival_df = pd.DataFrame(survival_curve)
    survival_path = "data/processed/survival_analysis.csv"
    survival_df.to_csv(survival_path, index=False)
    print(f"\nSurvival analysis table exported to: {survival_path}")
    
    return cohort_matrix_df, plan_retention, cycle_retention, onboard_retention, benchmark_curve

if __name__ == "__main__":
    cleaned_path = "data/processed/saas_customer_churn_cleaned.csv"
    analyze_cohorts_and_retention(cleaned_path)
