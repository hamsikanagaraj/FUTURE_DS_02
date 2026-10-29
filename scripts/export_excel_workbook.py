"""
Script: export_excel_workbook.py
Description: Generates an executive-grade, beautifully formatted multi-tab Excel workbook
             (SaaS_Customer_Retention_and_Churn_Analysis.xlsx) with KPI summary, cohort retention matrix,
             churn driver models, segment economics, and customer data.
"""

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import pandas as pd
import json
import os

def create_executive_excel_workbook():
    print("=" * 70)
    print("GENERATING EXECUTIVE EXCEL WORKBOOK")
    print("=" * 70)
    
    wb = openpyxl.Workbook()
    # Remove default sheet
    wb.remove(wb.active)
    
    # Define Palette & Styles
    NAVY_HEADER = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid") # Dark Slate / Navy
    TEAL_HEADER = PatternFill(start_color="0F766E", end_color="0F766E", fill_type="solid") # Teal / Emerald
    CARD_FILL = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
    ACCENT_FILL = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")
    ALERT_FILL = PatternFill(start_color="FEF2F2", end_color="FEF2F2", fill_type="solid")
    
    FONT_TITLE = Font(name="Calibri", size=16, bold=True, color="1E293B")
    FONT_SUBTITLE = Font(name="Calibri", size=11, italic=True, color="64748B")
    FONT_SECTION = Font(name="Calibri", size=13, bold=True, color="0F766E")
    FONT_HEADER = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    FONT_BOLD = Font(name="Calibri", size=11, bold=True, color="1E293B")
    FONT_REGULAR = Font(name="Calibri", size=11, color="334155")
    FONT_KPI_VAL = Font(name="Calibri", size=18, bold=True, color="0F172A")
    FONT_KPI_LBL = Font(name="Calibri", size=9, bold=True, color="64748B")
    
    BORDER_THIN = Border(
        left=Side(style='thin', color='CBD5E1'),
        right=Side(style='thin', color='CBD5E1'),
        top=Side(style='thin', color='CBD5E1'),
        bottom=Side(style='thin', color='CBD5E1')
    )
    
    ALIGN_CENTER = Alignment(horizontal="center", vertical="center")
    ALIGN_LEFT = Alignment(horizontal="left", vertical="center")
    ALIGN_RIGHT = Alignment(horizontal="right", vertical="center")
    
    # Load processed data
    with open("data/processed/churn_summary_kpis.json", "r") as f:
        kpis = json.load(f)
        
    df_clean = pd.read_csv("data/processed/saas_customer_churn_cleaned.csv")
    cohort_df = pd.read_csv("data/processed/cohort_retention_matrix.csv")
    fi_df = pd.read_csv("data/processed/churn_drivers_feature_importance.csv")
    reasons_df = pd.read_csv("data/processed/churn_reasons_breakdown.csv")
    
    # -------------------------------------------------------------
    # TAB 1: EXECUTIVE KPI DASHBOARD
    # -------------------------------------------------------------
    ws_exec = wb.create_sheet(title="Executive Summary")
    ws_exec.views.sheetView[0].showGridLines = True
    
    # Title Block
    ws_exec["B2"] = "SaaSify Cloud Solutions – Customer Retention & Churn Executive Analysis"
    ws_exec["B2"].font = FONT_TITLE
    ws_exec["B3"] = "Cohort Retention Tracking, Churn Driver Modeling & Revenue Protection Strategy | FY2024–FY2026"
    ws_exec["B3"].font = FONT_SUBTITLE
    
    # KPI Cards Layout (Row 5 - Row 7)
    cards = [
        ("TOTAL CUSTOMERS", f"{kpis['executive_summary']['total_customers']:,}", "Active + Churned Base", "B"),
        ("OVERALL CHURN RATE", f"{kpis['executive_summary']['overall_churn_rate_pct']:.1f}%", "Customer Count Churn", "D"),
        ("ACTIVE MRR", f"${kpis['executive_summary']['total_active_mrr']:,.0f}", "Monthly Recurring Revenue", "F"),
        ("LOST MRR (CHURN)", f"${kpis['executive_summary']['total_churned_mrr']:,.0f}", "Monthly Lost Revenue", "H"),
        ("GROSS REV RETENTION", f"{kpis['executive_summary']['gross_revenue_retention_pct']:.1f}%", "GRR Baseline", "J"),
        ("AVG CUSTOMER LTV", f"${kpis['executive_summary']['avg_customer_ltv']:,.0f}", "Realized Lifetime Rev", "L"),
    ]
    
    for lbl, val, sub, col_start in cards:
        c_idx = openpyxl.utils.column_index_from_string(col_start)
        col_end = openpyxl.utils.get_column_letter(c_idx + 1)
        
        ws_exec.merge_cells(f"{col_start}5:{col_end}5")
        ws_exec.merge_cells(f"{col_start}6:{col_end}6")
        ws_exec.merge_cells(f"{col_start}7:{col_end}7")
        
        ws_exec[f"{col_start}5"] = lbl
        ws_exec[f"{col_start}5"].font = FONT_KPI_LBL
        ws_exec[f"{col_start}5"].alignment = ALIGN_CENTER
        ws_exec[f"{col_start}5"].fill = CARD_FILL
        
        ws_exec[f"{col_start}6"] = val
        ws_exec[f"{col_start}6"].font = FONT_KPI_VAL
        ws_exec[f"{col_start}6"].alignment = ALIGN_CENTER
        ws_exec[f"{col_start}6"].fill = CARD_FILL
        
        ws_exec[f"{col_start}7"] = sub
        ws_exec[f"{col_start}7"].font = Font(name="Calibri", size=9, italic=True, color="94A3B8")
        ws_exec[f"{col_start}7"].alignment = ALIGN_CENTER
        ws_exec[f"{col_start}7"].fill = CARD_FILL
        
        # Border
        for r in range(5, 8):
            for c in range(c_idx, c_idx + 2):
                ws_exec.cell(row=r, column=c).border = BORDER_THIN
                
    # Section: Primary Churn Reasons
    ws_exec["B9"] = "1. Churn Reasons & Revenue Impact Analysis"
    ws_exec["B9"].font = FONT_SECTION
    
    headers_reasons = ["Primary Churn Reason", "Lost Accounts", "% of Churned", "Lost MRR ($)", "Lost ARR ($)", "Avg CSAT"]
    for i, h in enumerate(headers_reasons, start=2):
        cell = ws_exec.cell(row=10, column=i, value=h)
        cell.font = FONT_HEADER
        cell.fill = NAVY_HEADER
        cell.alignment = ALIGN_CENTER
        cell.border = BORDER_THIN
        
    for r_idx, row_data in enumerate(reasons_df.itertuples(), start=11):
        ws_exec.cell(row=r_idx, column=2, value=row_data.churn_reason).font = FONT_BOLD
        ws_exec.cell(row=r_idx, column=3, value=row_data.Churned_Customers).number_format = "#,##0"
        ws_exec.cell(row=r_idx, column=4, value=row_data.Pct_Of_Churned_Customers / 100).number_format = "0.0%"
        ws_exec.cell(row=r_idx, column=5, value=row_data.Lost_MRR).number_format = "$#,##0.00"
        ws_exec.cell(row=r_idx, column=6, value=row_data.Lost_ARR).number_format = "$#,##0.00"
        ws_exec.cell(row=r_idx, column=7, value=row_data.Avg_CSAT).number_format = "0.0"
        for c in range(2, 8):
            ws_exec.cell(row=r_idx, column=c).border = BORDER_THIN
            if c in [3, 4, 7]:
                ws_exec.cell(row=r_idx, column=c).alignment = ALIGN_CENTER
            elif c in [5, 6]:
                ws_exec.cell(row=r_idx, column=c).alignment = ALIGN_RIGHT
            else:
                ws_exec.cell(row=r_idx, column=c).alignment = ALIGN_LEFT
                
    # Section: High Risk Accounts Intervention
    start_r = 11 + len(reasons_df) + 2
    ws_exec.cell(row=start_r, column=2, value="2. Customer Segment Performance Summary").font = FONT_SECTION
    
    seg_headers = ["Segment", "Total Accounts", "Active Accounts", "Churn Rate (%)", "Retention Rate (%)", "Active MRR ($)", "ARR at Risk ($)"]
    for i, h in enumerate(seg_headers, start=2):
        cell = ws_exec.cell(row=start_r + 1, column=i, value=h)
        cell.font = FONT_HEADER
        cell.fill = TEAL_HEADER
        cell.alignment = ALIGN_CENTER
        cell.border = BORDER_THIN
        
    seg_df = pd.read_csv("data/processed/segment_metrics.csv")
    for r_idx, row in enumerate(seg_df.itertuples(), start=start_r + 2):
        ws_exec.cell(row=r_idx, column=2, value=row.customer_segment).font = FONT_BOLD
        ws_exec.cell(row=r_idx, column=3, value=row.Total_Customers).number_format = "#,##0"
        ws_exec.cell(row=r_idx, column=4, value=row.Active_Customers).number_format = "#,##0"
        ws_exec.cell(row=r_idx, column=5, value=row.Churn_Rate / 100).number_format = "0.0%"
        ws_exec.cell(row=r_idx, column=6, value=row.Retention_Rate / 100).number_format = "0.0%"
        ws_exec.cell(row=r_idx, column=7, value=row.Total_MRR - row.Lost_MRR).number_format = "$#,##0.00"
        ws_exec.cell(row=r_idx, column=8, value=row.ARR_At_Risk).number_format = "$#,##0.00"
        for c in range(2, 9):
            ws_exec.cell(row=r_idx, column=c).border = BORDER_THIN
            if c in [3, 4, 5, 6]:
                ws_exec.cell(row=r_idx, column=c).alignment = ALIGN_CENTER
            elif c in [7, 8]:
                ws_exec.cell(row=r_idx, column=c).alignment = ALIGN_RIGHT
            else:
                ws_exec.cell(row=r_idx, column=c).alignment = ALIGN_LEFT

    # -------------------------------------------------------------
    # TAB 2: COHORT RETENTION MATRIX
    # -------------------------------------------------------------
    ws_cohort = wb.create_sheet(title="Cohort Retention Matrix")
    ws_cohort.views.sheetView[0].showGridLines = True
    
    ws_cohort["B2"] = "Monthly Customer Cohort Retention Tracking (Month 0 to Month 12)"
    ws_cohort["B2"].font = FONT_TITLE
    ws_cohort["B3"] = "% of Signups Active at Each Subsequent Monthly Milestone"
    ws_cohort["B3"].font = FONT_SUBTITLE
    
    # Headers
    cohort_cols = list(cohort_df.columns)
    for c_i, col_name in enumerate(cohort_cols, start=2):
        cell = ws_cohort.cell(row=5, column=c_i, value=col_name)
        cell.font = FONT_HEADER
        cell.fill = NAVY_HEADER
        cell.alignment = ALIGN_CENTER
        cell.border = BORDER_THIN
        
    for r_i, row in enumerate(cohort_df.itertuples(), start=6):
        ws_cohort.cell(row=r_i, column=2, value=row.Cohort).font = FONT_BOLD
        ws_cohort.cell(row=r_i, column=2).alignment = ALIGN_CENTER
        ws_cohort.cell(row=r_i, column=2).border = BORDER_THIN
        
        ws_cohort.cell(row=r_i, column=3, value=row.Cohort_Size).number_format = "#,##0"
        ws_cohort.cell(row=r_i, column=3).alignment = ALIGN_CENTER
        ws_cohort.cell(row=r_i, column=3).border = BORDER_THIN
        
        for m_idx in range(13):
            val = getattr(row, f"M{m_idx}")
            c_pos = 4 + m_idx
            cell = ws_cohort.cell(row=r_i, column=c_pos)
            cell.border = BORDER_THIN
            cell.alignment = ALIGN_CENTER
            if pd.notna(val):
                cell.value = val / 100.0
                cell.number_format = "0.0%"
                # Color code retention rate
                if val >= 85.0:
                    cell.fill = PatternFill(start_color="DCFCE7", end_color="DCFCE7", fill_type="solid") # Green
                elif val >= 70.0:
                    cell.fill = PatternFill(start_color="FEF9C3", end_color="FEF9C3", fill_type="solid") # Yellow
                elif val >= 55.0:
                    cell.fill = PatternFill(start_color="FFEDD5", end_color="FFEDD5", fill_type="solid") # Light Orange
                else:
                    cell.fill = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid") # Red/Pink
            else:
                cell.value = "-"
                cell.font = Font(color="CBD5E1")
                
    # -------------------------------------------------------------
    # TAB 3: CHURN DRIVERS & MACHINE LEARNING
    # -------------------------------------------------------------
    ws_ml = wb.create_sheet(title="Churn Drivers & ML")
    ws_ml.views.sheetView[0].showGridLines = True
    
    ws_ml["B2"] = "Machine Learning Churn Driver Weights & Risk Propensity"
    ws_ml["B2"].font = FONT_TITLE
    ws_ml["B3"] = "Random Forest Feature Importance & Logistic Regression Odds Ratios (Model AUC: 0.807)"
    ws_ml["B3"].font = FONT_SUBTITLE
    
    ml_headers = ["Rank", "Churn Driver / Feature", "Feature Code", "Impact Weight (%)", "Odds Ratio", "Risk Direction"]
    for c_i, h in enumerate(ml_headers, start=2):
        cell = ws_ml.cell(row=5, column=c_i, value=h)
        cell.font = FONT_HEADER
        cell.fill = NAVY_HEADER
        cell.alignment = ALIGN_CENTER
        cell.border = BORDER_THIN
        
    for r_i, row in enumerate(fi_df.itertuples(), start=6):
        ws_ml.cell(row=r_i, column=2, value=r_i - 5).alignment = ALIGN_CENTER
        ws_ml.cell(row=r_i, column=3, value=row.feature_name).font = FONT_BOLD
        ws_ml.cell(row=r_i, column=4, value=row.feature_code).font = Font(name="Courier New", size=10, color="64748B")
        
        ws_ml.cell(row=r_i, column=5, value=row.relative_impact_pct / 100.0).number_format = "0.0%"
        ws_ml.cell(row=r_i, column=5).alignment = ALIGN_RIGHT
        
        ws_ml.cell(row=r_i, column=6, value=round(row.odds_ratio, 2)).number_format = "0.00"
        ws_ml.cell(row=r_i, column=6).alignment = ALIGN_RIGHT
        
        ws_ml.cell(row=r_i, column=7, value=row.risk_direction).alignment = ALIGN_LEFT
        if "Increases" in row.risk_direction:
            ws_ml.cell(row=r_i, column=7).font = Font(color="B91C1C", bold=True)
        else:
            ws_ml.cell(row=r_i, column=7).font = Font(color="15803D", bold=True)
            
        for c in range(2, 8):
            ws_ml.cell(row=r_i, column=c).border = BORDER_THIN
            
    # -------------------------------------------------------------
    # TAB 4: PLAN & CONTRACT BENCHMARKS
    # -------------------------------------------------------------
    ws_bench = wb.create_sheet(title="Plan & Contract Benchmarks")
    ws_bench.views.sheetView[0].showGridLines = True
    
    ws_bench["B2"] = "Subscription Plan & Billing Cycle Retention Performance"
    ws_bench["B2"].font = FONT_TITLE
    
    # Plan Table
    ws_bench["B4"] = "A. Retention by Subscription Tier"
    ws_bench["B4"].font = FONT_SECTION
    plan_headers = ["Plan Tier", "Total Customers", "Active Customers", "Churned Customers", "Churn Rate (%)", "Retention Rate (%)", "Active MRR ($)", "Lost MRR ($)"]
    for i, h in enumerate(plan_headers, start=2):
        cell = ws_bench.cell(row=5, column=i, value=h)
        cell.font = FONT_HEADER
        cell.fill = TEAL_HEADER
        cell.alignment = ALIGN_CENTER
        cell.border = BORDER_THIN
        
    for r_i, p_data in enumerate(kpis["plan_performance"], start=6):
        ws_bench.cell(row=r_i, column=2, value=p_data["subscription_plan"]).font = FONT_BOLD
        ws_bench.cell(row=r_i, column=3, value=p_data["Total"]).number_format = "#,##0"
        ws_bench.cell(row=r_i, column=4, value=p_data["Active"]).number_format = "#,##0"
        ws_bench.cell(row=r_i, column=5, value=p_data["Churned"]).number_format = "#,##0"
        ws_bench.cell(row=r_i, column=6, value=p_data["Churn_Rate"] / 100).number_format = "0.0%"
        ws_bench.cell(row=r_i, column=7, value=(100 - p_data["Churn_Rate"]) / 100).number_format = "0.0%"
        ws_bench.cell(row=r_i, column=8, value=p_data["Active_MRR"]).number_format = "$#,##0.00"
        ws_bench.cell(row=r_i, column=9, value=p_data["Lost_MRR"]).number_format = "$#,##0.00"
        for c in range(2, 10):
            ws_bench.cell(row=r_i, column=c).border = BORDER_THIN
            if c in [3, 4, 5, 6, 7]:
                ws_bench.cell(row=r_i, column=c).alignment = ALIGN_CENTER
            elif c in [8, 9]:
                ws_bench.cell(row=r_i, column=c).alignment = ALIGN_RIGHT
                
    # Contract Table
    r_c_start = 6 + len(kpis["plan_performance"]) + 2
    ws_bench.cell(row=r_c_start, column=2, value="B. Retention by Billing Cycle (Monthly vs Annual)").font = FONT_SECTION
    contract_headers = ["Billing Cycle", "Total Customers", "Churn Rate (%)", "Retention Rate (%)", "Average LTV ($)"]
    for i, h in enumerate(contract_headers, start=2):
        cell = ws_bench.cell(row=r_c_start + 1, column=i, value=h)
        cell.font = FONT_HEADER
        cell.fill = NAVY_HEADER
        cell.alignment = ALIGN_CENTER
        cell.border = BORDER_THIN
        
    for r_i, c_data in enumerate(kpis["contract_performance"], start=r_c_start + 2):
        ws_bench.cell(row=r_i, column=2, value=c_data["billing_cycle"]).font = FONT_BOLD
        ws_bench.cell(row=r_i, column=3, value=c_data["Total"]).number_format = "#,##0"
        ws_bench.cell(row=r_i, column=4, value=c_data["Churn_Rate"] / 100).number_format = "0.0%"
        ws_bench.cell(row=r_i, column=5, value=c_data["Retention_Rate"] / 100).number_format = "0.0%"
        ws_bench.cell(row=r_i, column=6, value=c_data["Avg_LTV"]).number_format = "$#,##0.00"
        for c in range(2, 7):
            ws_bench.cell(row=r_i, column=c).border = BORDER_THIN
            if c in [3, 4, 5]:
                ws_bench.cell(row=r_i, column=c).alignment = ALIGN_CENTER
            elif c == 6:
                ws_bench.cell(row=r_i, column=c).alignment = ALIGN_RIGHT

    # -------------------------------------------------------------
    # TAB 5: CLEANED DATASET (SAMPLE 1,500 ROWS FOR COMPACT SPEED)
    # -------------------------------------------------------------
    ws_data = wb.create_sheet(title="Customer Dataset (Sample)")
    ws_data.views.sheetView[0].showGridLines = True
    
    sample_df = df_clean.head(1500)
    data_cols = [
        "customer_id", "signup_date", "cohort_month", "customer_segment",
        "subscription_plan", "billing_cycle", "region", "mrr",
        "tenure_months", "onboarding_completed", "usage_frequency_days_per_month",
        "active_users_seats", "support_satisfaction_score", "churn_status",
        "churn_reason", "churn_risk_probability", "churn_risk_tier", "total_lifetime_revenue"
    ]
    
    # Headers
    for c_i, c_name in enumerate(data_cols, start=1):
        cell = ws_data.cell(row=1, column=c_i, value=c_name)
        cell.font = FONT_HEADER
        cell.fill = NAVY_HEADER
        cell.alignment = ALIGN_CENTER
        cell.border = BORDER_THIN
        
    for r_i, row in enumerate(sample_df[data_cols].itertuples(index=False), start=2):
        for c_i, val in enumerate(row, start=1):
            cell = ws_data.cell(row=r_i, column=c_i, value=val)
            cell.font = FONT_REGULAR
            cell.border = BORDER_THIN
            
            # Format numbers
            if data_cols[c_i - 1] in ["mrr", "total_lifetime_revenue"]:
                cell.number_format = "$#,##0.00"
                cell.alignment = ALIGN_RIGHT
            elif data_cols[c_i - 1] in ["tenure_months", "usage_frequency_days_per_month", "active_users_seats"]:
                cell.number_format = "#,##0"
                cell.alignment = ALIGN_CENTER
            elif data_cols[c_i - 1] == "churn_risk_probability":
                cell.number_format = "0.0\"%\""
                cell.alignment = ALIGN_RIGHT
            elif data_cols[c_i - 1] in ["churn_status", "onboarding_completed", "cohort_month", "signup_date"]:
                cell.alignment = ALIGN_CENTER

    # Auto-adjust column widths for all sheets
    for sheet in wb.worksheets:
        for col in sheet.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                # ignore merged cells or very long titles
                if cell.row in [2, 3] and sheet.title in ["Executive Summary", "Cohort Retention Matrix", "Churn Drivers & ML", "Plan & Contract Benchmarks"]:
                    continue
                if cell.value:
                    val_str = str(cell.value)
                    if len(val_str) > max_len:
                        max_len = len(val_str)
            sheet.column_dimensions[col_letter].width = max(max_len + 3, 11)
            
    excel_output_path = "data/excel/SaaS_Customer_Retention_and_Churn_Analysis.xlsx"
    os.makedirs(os.path.dirname(excel_output_path), exist_ok=True)
    wb.save(excel_output_path)
    print(f"\nExcel Workbook saved successfully to: {excel_output_path}")

if __name__ == "__main__":
    create_executive_excel_workbook()
