"""
Script: generate_charts.py
Description: Generates high-resolution PNG charts for executive presentations
             and report embedding (Cohort Heatmap, ML Drivers, Churn Reasons, Segment Economics).
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os

# Set styling
plt.style.use('dark_background')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#334155'
plt.rcParams['axes.linewidth'] = 0.8

os.makedirs("reports/assets", exist_ok=True)

# 1. COHORT RETENTION HEATMAP
print("Generating Cohort Retention Heatmap...")
cohort_df = pd.read_csv("data/processed/cohort_retention_matrix.csv")
cohort_matrix = cohort_df.set_index("Cohort")[[f"M{i}" for i in range(13)]]

plt.figure(figsize=(14, 10), facecolor='#060913')
ax = plt.gca()
ax.set_facecolor('#060913')

cmap = sns.color_palette("mako", as_cmap=True)
sns.heatmap(
    cohort_matrix,
    annot=True,
    fmt=".1f",
    cmap=cmap,
    vmin=40,
    vmax=100,
    linewidths=0.5,
    linecolor='#1E293B',
    cbar_kws={'label': 'Retention Rate (%)'},
    annot_kws={'size': 9, 'weight': 'bold'}
)

plt.title("SaaSify Customer Cohort Retention Heatmap (24-Month Tracking: Jan 2024 - Dec 2025)", fontsize=14, weight='bold', color='#FFFFFF', pad=15)
plt.xlabel("Tenure Milestone (Months Since Signup)", fontsize=11, color='#94A3B8', labelpad=10)
plt.ylabel("Signup Cohort", fontsize=11, color='#94A3B8', labelpad=10)
plt.tight_layout()
plt.savefig("reports/assets/cohort_retention_heatmap.png", dpi=300, facecolor='#060913')
plt.close()

# 2. CHURN DRIVERS FEATURE IMPORTANCE
print("Generating Churn Drivers Feature Importance Plot...")
fi_df = pd.read_csv("data/processed/churn_drivers_feature_importance.csv").sort_values(by="relative_impact_pct", ascending=True)

plt.figure(figsize=(10, 6), facecolor='#060913')
ax = plt.gca()
ax.set_facecolor('#060913')

colors = ['#F43F5E' if 'Increases' in r else '#6366F1' for r in fi_df['risk_direction']]
bars = plt.barh(fi_df['feature_name'], fi_df['relative_impact_pct'], color=colors, height=0.65, edgecolor='#334155')

for bar in bars:
    w = bar.get_width()
    plt.text(w + 0.4, bar.get_y() + bar.get_height()/2, f"{w:.1f}%", va='center', ha='left', color='#F8FAFC', fontsize=9, weight='bold')

plt.title("Machine Learning Churn Drivers (Random Forest Feature Importance | AUC: 0.807)", fontsize=13, weight='bold', color='#FFFFFF', pad=15)
plt.xlabel("Relative Importance Weight (%)", fontsize=10, color='#94A3B8', labelpad=10)
plt.xlim(0, max(fi_df['relative_impact_pct']) + 5)
plt.grid(axis='x', color='#FFFFFF', alpha=0.08, linestyle='--')
plt.tight_layout()
plt.savefig("reports/assets/churn_drivers_feature_importance.png", dpi=300, facecolor='#060913')
plt.close()

# 3. CHURN ROOT CAUSES & LOST ARR
print("Generating Churn Root Causes & Lost ARR Donut Chart...")
reasons_df = pd.read_csv("data/processed/churn_reasons_breakdown.csv")

plt.figure(figsize=(9, 6), facecolor='#060913')
colors = ['#F43F5E', '#F59E0B', '#6366F1', '#06B6D4', '#EC4899', '#8B5CF6']
wedges, texts, autotexts = plt.pie(
    reasons_df['Lost_ARR'],
    labels=[f"{r} (${val/1e6:.2f}M)" for r, val in zip(reasons_df['churn_reason'], reasons_df['Lost_ARR'])],
    autopct='%1.1f%%',
    startangle=140,
    colors=colors,
    pctdistance=0.75,
    textprops={'color': '#F8FAFC', 'fontsize': 9},
    wedgeprops={'width': 0.5, 'edgecolor': '#060913', 'linewidth': 2}
)

for autotext in autotexts:
    autotext.set_color('#FFFFFF')
    autotext.set_weight('bold')
    autotext.set_fontsize(9)

plt.title("Primary Churn Reasons by Lost Annual Recurring Revenue ($7.57M Total Lost ARR)", fontsize=12, weight='bold', color='#FFFFFF', pad=15)
plt.tight_layout()
plt.savefig("reports/assets/churn_reasons_revenue_loss.png", dpi=300, facecolor='#060913')
plt.close()

# 4. SEGMENTATION & RETENTION COMPARISON
print("Generating Comparative Segmentation Bar Plot...")
with open("data/processed/churn_summary_kpis.json", "r") as f:
    kpis = json.load(f)

fig, axes = plt.subplots(1, 3, figsize=(15, 5), facecolor='#060913')

# Plan Retention
plans = [p['subscription_plan'] for p in kpis['plan_performance']]
plan_ret = [100 - p['Churn_Rate'] for p in kpis['plan_performance']]
axes[0].set_facecolor('#060913')
axes[0].bar(plans, plan_ret, color=['#10B981', '#6366F1', '#F59E0B'], width=0.55, edgecolor='#334155')
axes[0].set_title("Retention by Plan Tier", fontsize=11, weight='bold', color='#FFFFFF')
axes[0].set_ylabel("Retention Rate (%)", fontsize=10, color='#94A3B8')
axes[0].set_ylim(0, 100)
for i, v in enumerate(plan_ret):
    axes[0].text(i, v + 2, f"{v:.1f}%", ha='center', color='#FFFFFF', weight='bold')

# Contract Retention
contracts = [c['billing_cycle'] for c in kpis['contract_performance']]
contract_ret = [c['Retention_Rate'] for c in kpis['contract_performance']]
axes[1].set_facecolor('#060913')
axes[1].bar(contracts, contract_ret, color=['#06B6D4', '#F43F5E'], width=0.45, edgecolor='#334155')
axes[1].set_title("Retention by Contract Type", fontsize=11, weight='bold', color='#FFFFFF')
axes[1].set_ylim(0, 100)
for i, v in enumerate(contract_ret):
    axes[1].text(i, v + 2, f"{v:.1f}%", ha='center', color='#FFFFFF', weight='bold')

# Onboarding Impact
onboarding_labels = ["Incomplete", "Completed"]
onboarding_ret = [o['Retention_Rate'] for o in kpis['onboarding_impact']]
axes[2].set_facecolor('#060913')
axes[2].bar(onboarding_labels, onboarding_ret, color=['#F43F5E', '#10B981'], width=0.45, edgecolor='#334155')
axes[2].set_title("Impact of Guided Onboarding", fontsize=11, weight='bold', color='#FFFFFF')
axes[2].set_ylim(0, 100)
for i, v in enumerate(onboarding_ret):
    axes[2].text(i, v + 2, f"{v:.1f}%", ha='center', color='#FFFFFF', weight='bold')

for ax in axes:
    ax.grid(axis='y', color='#FFFFFF', alpha=0.08, linestyle='--')
    ax.tick_params(colors='#CBD5E1')

plt.suptitle("Core Retention Differentials: Plan Tier, Billing Contract & Onboarding", fontsize=13, weight='bold', color='#FFFFFF', y=1.02)
plt.tight_layout()
plt.savefig("reports/assets/retention_by_segments_and_plans.png", dpi=300, facecolor='#060913')
plt.close()

print("All high-resolution charts successfully generated in reports/assets/")
