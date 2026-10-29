"""
Script: data_cleaning.py
Description: Performs end-to-end data auditing, cleaning, standardization,
             missing value imputation, and feature engineering on the raw SaaS churn dataset.
"""

import pandas as pd
import numpy as np
import os
import re

def clean_saas_churn_data(raw_csv_path, processed_csv_path):
    print("=" * 70)
    print("1. LOADING RAW SAAS CHURN DATASET")
    print("=" * 70)
    df = pd.read_csv(raw_csv_path)
    print(f"Raw dataset shape: {df.shape[0]} rows, {df.shape[1]} columns")
    print("\nInitial Missing Values:")
    print(df.isnull().sum()[df.isnull().sum() > 0])
    
    print("\n" + "=" * 70)
    print("2. STRING STANDARDIZATION & TRIMMING")
    print("=" * 70)
    string_cols = ["customer_id", "subscription_plan", "customer_segment", "billing_cycle", "region", "churn_status"]
    for col in string_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            
    print("Cleaned subscription plans:", df["subscription_plan"].unique())
    print("Cleaned customer segments:", df["customer_segment"].unique())
    print("Cleaned billing cycles:", df["billing_cycle"].unique())
    
    print("\n" + "=" * 70)
    print("3. DATE STANDARDIZATION")
    print("=" * 70)
    # Parse signup_date with flexible parsing (dayfirst where applicable)
    df["signup_date"] = pd.to_datetime(df["signup_date"], format="mixed", dayfirst=True)
    df["signup_date_clean"] = df["signup_date"].dt.strftime("%Y-%m-%d")
    df["cohort_month"] = df["signup_date"].dt.strftime("%Y-%m")
    
    # Parse churn_date
    df["churn_date_clean"] = pd.to_datetime(df["churn_date"], errors="coerce").dt.strftime("%Y-%m-%d")
    # For active customers, churn_date should be null
    df.loc[df["churn_status"] == "Active", "churn_date_clean"] = np.nan
    
    print("Signup date range:", df["signup_date_clean"].min(), "to", df["signup_date_clean"].max())
    print("Unique cohorts count:", df["cohort_month"].nunique())
    
    print("\n" + "=" * 70)
    print("4. NUMERICAL CLEANING & CURRENCY NORMALIZATION")
    print("=" * 70)
    # Clean total_lifetime_revenue (remove $, commas if present)
    def clean_currency(val):
        if pd.isna(val):
            return 0.0
        if isinstance(val, (int, float)):
            return float(val)
        val_str = str(val).replace("$", "").replace(",", "").strip()
        try:
            return float(val_str)
        except ValueError:
            return 0.0
            
    df["total_lifetime_revenue"] = df["total_lifetime_revenue"].apply(clean_currency)
    df["mrr"] = pd.to_numeric(df["mrr"], errors="coerce").fillna(0.0)
    df["tenure_months"] = pd.to_numeric(df["tenure_months"], errors="coerce").fillna(1).astype(int)
    
    # Check bounds
    df["usage_frequency_days_per_month"] = pd.to_numeric(df["usage_frequency_days_per_month"], errors="coerce").fillna(0).astype(int)
    df["active_users_seats"] = pd.to_numeric(df["active_users_seats"], errors="coerce").fillna(1).astype(int)
    df["support_tickets_opened"] = pd.to_numeric(df["support_tickets_opened"], errors="coerce").fillna(0).astype(int)
    df["payment_failures_count"] = pd.to_numeric(df["payment_failures_count"], errors="coerce").fillna(0).astype(int)
    df["nps_score"] = pd.to_numeric(df["nps_score"], errors="coerce").fillna(7).astype(int)
    
    print("\n" + "=" * 70)
    print("5. HANDLING MISSING VALUES & CHURN REASONS")
    print("=" * 70)
    # CSAT imputation using median per plan
    csat_medians = df.groupby("subscription_plan")["support_satisfaction_score"].transform("median")
    df["support_satisfaction_score"] = df["support_satisfaction_score"].fillna(csat_medians).round(1)
    
    # Clean churn_reason
    df["churn_reason"] = df["churn_reason"].fillna("None (Active)")
    df.loc[df["churn_status"] == "Active", "churn_reason"] = "None (Active)"
    
    print("\n" + "=" * 70)
    print("6. FEATURE ENGINEERING FOR RETENTION & CHURN INSIGHTS")
    print("=" * 70)
    # Binary churn indicator
    df["is_churned"] = (df["churn_status"] == "Churned").astype(int)
    
    # Tenure brackets
    def assign_tenure_bracket(m):
        if m <= 3:
            return "0-3 Months (Early Onboarding)"
        elif m <= 6:
            return "4-6 Months (Ramp-up)"
        elif m <= 12:
            return "7-12 Months (Established)"
        else:
            return "13-24+ Months (Mature/Loyal)"
            
    df["tenure_bracket"] = df["tenure_months"].apply(assign_tenure_bracket)
    
    # Engagement tier
    def assign_engagement(days):
        if days < 8:
            return "Low Engagement (<8 days/mo)"
        elif days <= 18:
            return "Moderate Engagement (8-18 days/mo)"
        else:
            return "High Engagement (>18 days/mo)"
            
    df["engagement_tier"] = df["usage_frequency_days_per_month"].apply(assign_engagement)
    
    # ARPU (Average Revenue per Seat)
    df["arpu_per_seat"] = (df["mrr"] / df["active_users_seats"]).round(2)
    
    # Involuntary churn indicator
    df["involuntary_churn"] = (df["churn_reason"].str.contains("Payment|Dunning", case=False, na=False)).astype(int)
    
    # Annualized Contract Value (ACV)
    df["annual_contract_value"] = (df["mrr"] * 12).round(2)
    
    # Deduplication check
    dup_count = df.duplicated(subset=["customer_id"]).sum()
    print(f"Duplicate customer records found: {dup_count}")
    if dup_count > 0:
        df = df.drop_duplicates(subset=["customer_id"])
        
    print("\nCleaned Dataset Overview:")
    print(f"Total Clean Customers: {len(df)}")
    print(f"Overall Churn Rate: {df['is_churned'].mean():.2%}")
    print(f"Total MRR Active Base: ${df[df['churn_status'] == 'Active']['mrr'].sum():,.2f}")
    print(f"Total Lost MRR (Churned): ${df[df['churn_status'] == 'Churned']['mrr'].sum():,.2f}")
    print(f"Total Lifetime Revenue Realized: ${df['total_lifetime_revenue'].sum():,.2f}")
    
    # Reorganize column order cleanly
    clean_cols = [
        "customer_id",
        "signup_date_clean",
        "cohort_month",
        "customer_segment",
        "subscription_plan",
        "billing_cycle",
        "region",
        "mrr",
        "annual_contract_value",
        "tenure_months",
        "tenure_bracket",
        "onboarding_completed",
        "usage_frequency_days_per_month",
        "engagement_tier",
        "active_users_seats",
        "arpu_per_seat",
        "support_tickets_opened",
        "support_satisfaction_score",
        "payment_failures_count",
        "nps_score",
        "churn_status",
        "is_churned",
        "churn_date_clean",
        "churn_reason",
        "involuntary_churn",
        "total_lifetime_revenue"
    ]
    df_clean = df[clean_cols].rename(columns={
        "signup_date_clean": "signup_date",
        "churn_date_clean": "churn_date"
    })
    
    # Export clean data
    os.makedirs(os.path.dirname(processed_csv_path), exist_ok=True)
    df_clean.to_csv(processed_csv_path, index=False)
    print(f"\nCleaned dataset successfully exported to: {processed_csv_path}")
    
    return df_clean

if __name__ == "__main__":
    raw_path = "data/raw/saas_customer_churn_raw.csv"
    processed_path = "data/processed/saas_customer_churn_cleaned.csv"
    clean_saas_churn_data(raw_path, processed_path)
