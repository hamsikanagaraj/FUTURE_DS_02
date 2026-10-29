"""
Script: generate_saas_dataset.py
Description: Generates a realistic, enterprise-grade SaaS subscription & customer churn dataset
             spanning 24 signup cohorts (2024-01 to 2025-12) with realistic churn mechanics,
             behavioral engagement signals, financial metrics, and real-world raw data anomalies.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

def generate_saas_churn_data(n_customers=8500):
    customer_ids = [f"CUST-{10000 + i}" for i in range(n_customers)]
    
    # Cohort signup dates over 24 months: 2024-01-01 to 2025-12-31
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2025, 12, 31)
    date_range_days = (end_date - start_date).days
    
    # Snapshot / Analysis date is 2026-03-31
    snapshot_date = datetime(2026, 3, 31)
    
    plans = ["Starter", "Professional", "Enterprise"]
    plan_probs = [0.45, 0.40, 0.15]
    
    base_mrr_map = {
        "Starter": 49.0,
        "Professional": 149.0,
        "Enterprise": 499.0
    }
    
    segments = ["SMB", "Mid-Market", "Enterprise"]
    regions = ["North America", "Europe", "Asia-Pacific", "Latin America"]
    region_probs = [0.48, 0.28, 0.16, 0.08]
    
    billing_cycles = ["Monthly", "Annual"]
    
    churn_reasons_pool = [
        "Competitor Switched",
        "High Price / Budget Cuts",
        "Poor Product Fit / Low Usage",
        "Customer Support Unresponsive",
        "Missing Key Integrations",
        "Payment / Involuntary Dunning Failure"
    ]
    
    records = []
    
    for i, cust_id in enumerate(customer_ids):
        # Signup Date
        random_days = random.randint(0, date_range_days)
        signup_dt = start_date + timedelta(days=random_days)
        cohort_month = signup_dt.strftime("%Y-%m")
        
        # Segment & Plan selection (correlated)
        seg_roll = random.random()
        if seg_roll < 0.55:
            segment = "SMB"
            plan = np.random.choice(["Starter", "Professional"], p=[0.75, 0.25])
        elif seg_roll < 0.85:
            segment = "Mid-Market"
            plan = np.random.choice(["Starter", "Professional", "Enterprise"], p=[0.15, 0.65, 0.20])
        else:
            segment = "Enterprise"
            plan = np.random.choice(["Professional", "Enterprise"], p=[0.20, 0.80])
            
        # Billing cycle: Enterprise prefers annual, SMB prefers monthly
        if plan == "Enterprise":
            billing_cycle = np.random.choice(billing_cycles, p=[0.20, 0.80])
        elif plan == "Professional":
            billing_cycle = np.random.choice(billing_cycles, p=[0.55, 0.45])
        else:
            billing_cycle = np.random.choice(billing_cycles, p=[0.82, 0.18])
            
        region = np.random.choice(regions, p=region_probs)
        
        # Base MRR + add-ons (seats, modules)
        base_mrr = base_mrr_map[plan]
        extra_seats = random.randint(0, 5) if plan == "Starter" else (random.randint(1, 20) if plan == "Professional" else random.randint(10, 80))
        seat_price = 12.0 if plan == "Starter" else (18.0 if plan == "Professional" else 25.0)
        mrr = round(base_mrr + (extra_seats * seat_price * 0.4), 2)
        
        # Max possible tenure in months from signup to snapshot
        max_possible_tenure = max(1, int((snapshot_date - signup_dt).days / 30.44))
        
        # Onboarding completion status (SMBs have lower completion rate)
        onboarding_prob = 0.88 if segment == "Enterprise" else (0.75 if segment == "Mid-Market" else 0.58)
        onboarding_completed = random.random() < onboarding_prob
        
        # Usage metrics (Days active per month, 0 to 30)
        base_active_days = random.gauss(18, 6) if onboarding_completed else random.gauss(8, 4)
        active_days = int(np.clip(base_active_days, 1, 30))
        
        # Support tickets
        support_tickets = np.random.poisson(lam=2.8)
        
        # CSAT score (1 to 5)
        if support_tickets == 0:
            csat = 4.5
        elif support_tickets > 5:
            csat = round(float(np.clip(random.gauss(2.4, 0.9), 1.0, 5.0)), 1)
        else:
            csat = round(float(np.clip(random.gauss(3.8, 0.8), 1.0, 5.0)), 1)
            
        # Payment failure count (0, 1, 2, 3+)
        payment_failures = np.random.choice([0, 1, 2, 3], p=[0.82, 0.11, 0.05, 0.02])
        
        # Net Promoter Score (NPS: 0-10)
        if csat >= 4.0 and active_days >= 15:
            nps_rating = int(np.clip(random.gauss(8.8, 1.2), 0, 10))
        elif csat < 3.0 or active_days < 7:
            nps_rating = int(np.clip(random.gauss(4.2, 2.0), 0, 10))
        else:
            nps_rating = int(np.clip(random.gauss(6.8, 1.8), 0, 10))
            
        # Calculate Churn Propensity based on realistic SaaS drivers:
        churn_risk = 0.22 # baseline risk
        
        # Monthly vs Annual
        if billing_cycle == "Monthly":
            churn_risk += 0.16
        else:
            churn_risk -= 0.12
            
        # Plan tier
        if plan == "Starter":
            churn_risk += 0.10
        elif plan == "Enterprise":
            churn_risk -= 0.12
            
        # Onboarding
        if not onboarding_completed:
            churn_risk += 0.24
            
        # Inactivity
        if active_days < 6:
            churn_risk += 0.25
        elif active_days > 20:
            churn_risk -= 0.12
            
        # Support friction
        if csat < 2.5:
            churn_risk += 0.18
        if support_tickets >= 6:
            churn_risk += 0.14
            
        # Involuntary payment failures
        if payment_failures >= 2:
            churn_risk += 0.26
            
        churn_risk = float(np.clip(churn_risk, 0.05, 0.92))
        
        # Simulate Churn Outcome
        is_churned = random.random() < churn_risk
        
        if is_churned:
            churn_status = "Churned"
            # How long did they survive?
            # High churn in early months (months 1-3) especially if no onboarding
            if not onboarding_completed:
                tenure_months = random.randint(1, min(3, max_possible_tenure))
            else:
                # Weibull/exponential shaped lifespan
                lifespan_roll = int(np.random.exponential(scale=7)) + 1
                tenure_months = min(lifespan_roll, max_possible_tenure)
                
            churn_dt = signup_dt + timedelta(days=int(tenure_months * 30.44))
            churn_date_str = churn_dt.strftime("%Y-%m-%d")
            
            # Select realistic churn reason based on profiles
            if payment_failures >= 2 and random.random() < 0.65:
                churn_reason = "Payment / Involuntary Dunning Failure"
            elif not onboarding_completed or active_days < 6:
                churn_reason = "Poor Product Fit / Low Usage"
            elif csat < 2.8 or support_tickets >= 5:
                churn_reason = "Customer Support Unresponsive"
            elif plan == "Enterprise" or plan == "Professional":
                churn_reason = np.random.choice(
                    ["Competitor Switched", "Missing Key Integrations", "High Price / Budget Cuts"],
                    p=[0.45, 0.35, 0.20]
                )
            else:
                churn_reason = np.random.choice(
                    ["High Price / Budget Cuts", "Competitor Switched", "Poor Product Fit / Low Usage"],
                    p=[0.40, 0.35, 0.25]
                )
        else:
            churn_status = "Active"
            tenure_months = max_possible_tenure
            churn_date_str = ""
            churn_reason = "None (Active)"
            
        # Total revenue to date
        if billing_cycle == "Annual":
            years_billed = max(1, int(np.ceil(tenure_months / 12)))
            total_revenue = round(years_billed * mrr * 12 * 0.85, 2) # 15% annual discount
        else:
            total_revenue = round(tenure_months * mrr, 2)
            
        # Record creation
        records.append({
            "customer_id": cust_id,
            "signup_date": signup_dt.strftime("%Y-%m-%d"),
            "cohort_month": cohort_month,
            "customer_segment": segment,
            "subscription_plan": plan,
            "billing_cycle": billing_cycle,
            "region": region,
            "mrr": mrr,
            "tenure_months": tenure_months,
            "onboarding_completed": onboarding_completed,
            "usage_frequency_days_per_month": active_days,
            "active_users_seats": extra_seats + 1,
            "support_tickets_opened": support_tickets,
            "support_satisfaction_score": csat,
            "payment_failures_count": payment_failures,
            "nps_score": nps_rating,
            "churn_status": churn_status,
            "churn_date": churn_date_str,
            "churn_reason": churn_reason,
            "total_lifetime_revenue": total_revenue
        })
        
    df = pd.DataFrame(records)
    
    # Introduce intentional raw anomalies to simulate dirty raw enterprise data:
    # 1. Whitespace in categories
    df_raw = df.copy()
    noisy_indices = df_raw.sample(frac=0.06, random_state=42).index
    df_raw.loc[noisy_indices, "subscription_plan"] = df_raw.loc[noisy_indices, "subscription_plan"].apply(lambda x: f" {x}  ")
    
    # 2. Some dates formatted as DD/MM/YYYY or MM-DD-YYYY
    date_noisy = df_raw.sample(frac=0.04, random_state=123).index
    df_raw.loc[date_noisy, "signup_date"] = pd.to_datetime(df_raw.loc[date_noisy, "signup_date"]).dt.strftime("%d/%m/%Y")
    
    # 3. Missing values in CSAT (users who didn't submit review)
    missing_csat = df_raw.sample(frac=0.05, random_state=77).index
    df_raw.loc[missing_csat, "support_satisfaction_score"] = np.nan
    
    # 4. In churn_date, active users should have empty strings or nulls
    df_raw.loc[df_raw["churn_status"] == "Active", "churn_date"] = np.nan
    df_raw.loc[df_raw["churn_status"] == "Active", "churn_reason"] = np.nan
    
    # 5. Some string numbers in total_lifetime_revenue
    str_rev = df_raw.sample(frac=0.03, random_state=88).index
    df_raw.loc[str_rev, "total_lifetime_revenue"] = df_raw.loc[str_rev, "total_lifetime_revenue"].apply(lambda x: f"${x:,.2f}")
    
    return df_raw

if __name__ == "__main__":
    df_raw = generate_saas_churn_data(n_customers=8500)
    raw_path = "data/raw/saas_customer_churn_raw.csv"
    df_raw.to_csv(raw_path, index=False)
    print(f"Generated {len(df_raw)} raw customer records saved to {raw_path}")
    print(df_raw.head())
    print("\nData distribution by Churn Status:")
    print(df_raw["churn_status"].value_counts(normalize=True))
