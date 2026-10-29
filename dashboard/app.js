/**
 * RetainPulse | SaaS Customer Retention & Churn Intelligence Application Logic
 * Multi-Theme Engine, Dynamic Cohort Filter, What-If Presets, Column Sorting,
 * Live Account Telemetry Modal, Dynamic Filter Reactivity & Table Pagination
 */

document.addEventListener("DOMContentLoaded", () => {
  // Check if data is loaded
  if (typeof RETENTION_DATA === "undefined") {
    console.error("RETENTION_DATA not found. Make sure data.js is loaded.");
    return;
  }

  const { kpis, cohortMatrix, survivalCurve, featureImportance, customerAccounts } = RETENTION_DATA;

  // State Management - Default to Frosted Pearl & Sapphire Light
  let currentTheme = localStorage.getItem("retainpulse_theme") || "pearl";
  if (!["pearl", "navy", "emerald", "sunset"].includes(currentTheme)) {
    currentTheme = "pearl";
    localStorage.setItem("retainpulse_theme", "pearl");
  }
  let currentFont = localStorage.getItem("retainpulse_font") || "sora-inter";
  let chartInstances = {};
  let currentFilteredAccounts = [...customerAccounts];
  let accountsPage = 1;
  let accountsPerPage = 15;
  let currentSort = { column: null, direction: 'asc' };

  // Toast Notification Helper
  function showToast(message, duration = 3000) {
    const toast = document.getElementById("toast-notification");
    if (!toast) return;
    toast.innerHTML = `
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
        <polyline points="22 4 12 14.01 9 11.01"/>
      </svg>
      <span>${message}</span>
    `;
    toast.classList.add("show");
    setTimeout(() => {
      toast.classList.remove("show");
    }, duration);
  }

  // Initialize UI & Theme & Font
  applyTheme(currentTheme);
  applyFont(currentFont);
  initKPIs(kpis.executive_summary);
  renderCohortHeatmap();
  initSurvivalChart(survivalCurve);
  initChurnDriversChart(featureImportance);
  initChurnReasonsChart(kpis.churn_reasons);
  initSegmentationCharts(kpis);
  initSimulator();
  applyAccountFilters(); // Sync table with initial dropdown selections
  setupEventListeners();
  initScrollSpy();

  // -------------------------------------------------------------
  // 1. THEME & FONT SWITCHER ENGINES
  // -------------------------------------------------------------
  function applyTheme(themeName) {
    document.body.dataset.theme = themeName;
    const themeSelect = document.getElementById("theme-selector");
    if (themeSelect) themeSelect.value = themeName;
    localStorage.setItem("retainpulse_theme", themeName);

    // Refresh charts if already initialized
    if (chartInstances.drivers) {
      updateChartsTheme();
    }
  }

  function applyFont(fontName) {
    document.body.dataset.font = fontName;
    const fontSelect = document.getElementById("font-selector");
    if (fontSelect) fontSelect.value = fontName;
    localStorage.setItem("retainpulse_font", fontName);
  }

  function getThemeColors() {
    const theme = document.body.dataset.theme || "pearl";
    if (theme === "navy") {
      return {
        isDark: true,
        primary: "#38BDF8",
        secondary: "#7DD3FC",
        accent: "#818CF8",
        rose: "#FF477E",
        amber: "#FBBF24",
        emerald: "#00F5A0",
        tickColor: "#94A3B8",
        gridColor: "rgba(255, 255, 255, 0.08)",
        textColor: "#F0F9FF",
        doughnutBorder: "#0B192C"
      };
    } else if (theme === "emerald") {
      return {
        isDark: false,
        primary: "#059669",
        secondary: "#10B981",
        accent: "#0D9488",
        rose: "#E11D48",
        amber: "#D97706",
        emerald: "#059669",
        tickColor: "#475569",
        gridColor: "rgba(6, 78, 59, 0.08)",
        textColor: "#064E3B",
        doughnutBorder: "#FFFFFF"
      };
    } else if (theme === "sunset") {
      return {
        isDark: false,
        primary: "#E11D48",
        secondary: "#F43F5E",
        accent: "#8B5CF6",
        rose: "#BE123C",
        amber: "#D97706",
        emerald: "#059669",
        tickColor: "#4B5563",
        gridColor: "rgba(76, 5, 25, 0.08)",
        textColor: "#4C0519",
        doughnutBorder: "#FFFFFF"
      };
    }
    // Default: "pearl" (Frosted Pearl & Sapphire Light)
    return {
      isDark: false,
      primary: "#4F46E5",
      secondary: "#6366F1",
      accent: "#0284C7",
      rose: "#E11D48",
      amber: "#D97706",
      emerald: "#059669",
      tickColor: "#475569",
      gridColor: "rgba(15, 23, 42, 0.07)",
      textColor: "#0F172A",
      doughnutBorder: "#FFFFFF"
    };
  }

  function updateChartsTheme() {
    const colors = getThemeColors();

    const updateAxes = (chart) => {
      if (!chart || !chart.options || !chart.options.scales) return;
      if (chart.options.scales.x) {
        if (chart.options.scales.x.ticks) chart.options.scales.x.ticks.color = colors.tickColor;
        if (chart.options.scales.x.grid && chart.options.scales.x.grid.display !== false) {
          chart.options.scales.x.grid.color = colors.gridColor;
        }
      }
      if (chart.options.scales.y) {
        if (chart.options.scales.y.ticks) chart.options.scales.y.ticks.color = colors.tickColor;
        if (chart.options.scales.y.grid && chart.options.scales.y.grid.display !== false) {
          chart.options.scales.y.grid.color = colors.gridColor;
        }
      }
    };

    if (chartInstances.survival) {
      chartInstances.survival.data.datasets[0].borderColor = colors.primary;
      chartInstances.survival.data.datasets[0].pointBackgroundColor = colors.primary;
      chartInstances.survival.data.datasets[0].backgroundColor = `${colors.primary}25`;
      updateAxes(chartInstances.survival);
      chartInstances.survival.update();
    }
    if (chartInstances.drivers) {
      const topFeatures = featureImportance.slice(0, 6);
      chartInstances.drivers.data.datasets[0].backgroundColor = topFeatures.map(f => f.odds_ratio > 1.0 ? colors.rose : colors.primary);
      updateAxes(chartInstances.drivers);
      chartInstances.drivers.update();
    }
    if (chartInstances.reasons) {
      chartInstances.reasons.data.datasets[0].borderColor = colors.doughnutBorder;
      if (chartInstances.reasons.options.plugins && chartInstances.reasons.options.plugins.legend) {
        chartInstances.reasons.options.plugins.legend.labels.color = colors.textColor;
      }
      chartInstances.reasons.update();
    }
    if (chartInstances.plan) {
      updateAxes(chartInstances.plan);
      chartInstances.plan.update();
    }
    if (chartInstances.contract) {
      chartInstances.contract.data.datasets[0].backgroundColor = [colors.primary, colors.rose];
      updateAxes(chartInstances.contract);
      chartInstances.contract.update();
    }
    if (chartInstances.onboard) {
      chartInstances.onboard.data.datasets[0].backgroundColor = [colors.rose, colors.primary];
      updateAxes(chartInstances.onboard);
      chartInstances.onboard.update();
    }
  }

  // -------------------------------------------------------------
  // 2. TOP KPI INITIALIZATION & DYNAMIC REACTIVITY
  // -------------------------------------------------------------
  function initKPIs(execSummary) {
    const churnEl = document.getElementById("kpi-churn-rate");
    const grrEl = document.getElementById("kpi-grr");
    const mrrEl = document.getElementById("kpi-active-mrr");
    const ltvEl = document.getElementById("kpi-avg-ltv");

    if (churnEl) churnEl.innerText = `${execSummary.overall_churn_rate_pct.toFixed(1)}%`;
    if (grrEl) grrEl.innerText = `${execSummary.gross_revenue_retention_pct.toFixed(1)}%`;
    if (mrrEl) mrrEl.innerText = `$${Math.round(execSummary.total_active_mrr).toLocaleString()}`;
    if (ltvEl) ltvEl.innerText = `$${Math.round(execSummary.avg_customer_ltv).toLocaleString()}`;
  }

  function updateDynamicKPIs() {
    const segFilter = document.getElementById("segment-filter");
    const planFilter = document.getElementById("plan-filter");
    const billingFilter = document.getElementById("billing-filter");
    const resetBtn = document.getElementById("reset-global-filters-btn");

    const segVal = segFilter ? segFilter.value : "ALL";
    const planVal = planFilter ? planFilter.value : "ALL";
    const billingVal = billingFilter ? billingFilter.value : "ALL";

    const isFiltered = (segVal !== "ALL") || (planVal !== "ALL") || (billingVal !== "ALL");

    if (resetBtn) {
      resetBtn.style.display = isFiltered ? "inline-flex" : "none";
    }

    if (!isFiltered) {
      initKPIs(kpis.executive_summary);
      const alertBanner = document.getElementById("risk-alert-banner");
      if (alertBanner) {
        const titleEl = alertBanner.querySelector("h4");
        const descEl = alertBanner.querySelector("p");
        if (titleEl) titleEl.innerText = "Acute Revenue Risk Alert: $2,163,768 ARR at Immediate Churn Risk";
        if (descEl) descEl.innerHTML = "Predictive machine learning models identify <strong>1,009 active accounts</strong> exhibiting acute churn probability (&gt;65%), representing <strong>$180,314 in monthly recurring revenue ($2.16M ARR)</strong> requiring proactive customer success intervention.";
      }
      return;
    }

    // Filter accounts matching global filters
    const matched = customerAccounts.filter(acc => {
      const matchSeg = (segVal === "ALL") || (acc.customer_segment === segVal);
      const matchPlan = (planVal === "ALL") || (acc.subscription_plan === planVal);
      const matchBilling = (billingVal === "ALL") || (acc.billing_cycle === billingVal);
      return matchSeg && matchPlan && matchBilling;
    });

    const total = matched.length;
    if (total === 0) return;

    const active = matched.filter(a => a.churn_status === "Active");
    const churned = matched.filter(a => a.churn_status === "Churned");
    const churnRate = (churned.length / total) * 100;
    const activeMRR = active.reduce((sum, a) => sum + a.mrr, 0);
    const avgLTV = matched.reduce((sum, a) => sum + (a.total_lifetime_revenue || a.mrr * a.tenure_months), 0) / total;

    const churnedMRR = churned.reduce((sum, a) => sum + a.mrr, 0);
    const totalMRR = activeMRR + churnedMRR;
    const dynamicGRR = totalMRR > 0 ? (activeMRR / totalMRR * 100) : 73.5;

    initKPIs({
      overall_churn_rate_pct: churnRate,
      gross_revenue_retention_pct: dynamicGRR,
      total_active_mrr: activeMRR,
      avg_customer_ltv: avgLTV
    });

    // Update risk banner for this filtered slice
    const highRiskActive = active.filter(a => a.churn_risk_tier === "High Risk");
    const highRiskMRR = highRiskActive.reduce((sum, a) => sum + a.mrr, 0);
    const highRiskARR = highRiskMRR * 12;

    const alertBanner = document.getElementById("risk-alert-banner");
    if (alertBanner) {
      const titleEl = alertBanner.querySelector("h4");
      const descEl = alertBanner.querySelector("p");
      if (titleEl) {
        titleEl.innerText = `Segment Revenue Risk Alert: $${Math.round(highRiskARR).toLocaleString()} ARR at Immediate Churn Risk`;
      }
      if (descEl) {
        descEl.innerHTML = `Filtered segment slice identifies <strong>${highRiskActive.length} active accounts</strong> exhibiting acute churn probability (&gt;65%), representing <strong>$${Math.round(highRiskMRR).toLocaleString()} in monthly recurring revenue ($${Math.round(highRiskARR).toLocaleString()} ARR)</strong>.`;
      }
    }
  }

  // -------------------------------------------------------------
  // 3. COHORT RETENTION HEATMAP (WITH FILTER & METRIC OPTIONS)
  // -------------------------------------------------------------
  function renderCohortHeatmap() {
    const tbody = document.getElementById("cohort-tbody");
    const periodFilter = document.getElementById("cohort-period-select") ? document.getElementById("cohort-period-select").value : "ALL";
    const metricFilter = document.getElementById("cohort-metric-select") ? document.getElementById("cohort-metric-select").value : "retention";

    tbody.innerHTML = "";

    let displayedCohorts = cohortMatrix;
    if (periodFilter === "2024") {
      displayedCohorts = cohortMatrix.filter(row => row.Cohort.startsWith("2024"));
    } else if (periodFilter === "2025") {
      displayedCohorts = cohortMatrix.filter(row => row.Cohort.startsWith("2025"));
    }

    displayedCohorts.forEach(row => {
      const tr = document.createElement("tr");

      let rowHtml = `<td class="sticky-col"><strong>${row.Cohort}</strong></td><td>${row.Cohort_Size.toLocaleString()}</td>`;

      for (let m = 0; m <= 12; m++) {
        const val = row[`M${m}`];
        if (val !== null && val !== undefined && !isNaN(val)) {
          let cellText = "";
          let colorClass = "c-low";

          if (val >= 85) colorClass = "c-high";
          else if (val >= 70) colorClass = "c-good";
          else if (val >= 55) colorClass = "c-med";

          if (metricFilter === "retention") {
            cellText = `${val}%`;
          } else if (metricFilter === "churn") {
            const churnRate = (100 - val).toFixed(1);
            cellText = `${churnRate}%`;
          } else if (metricFilter === "count") {
            const retainedCount = Math.round((val / 100) * row.Cohort_Size);
            cellText = retainedCount.toLocaleString();
          }

          rowHtml += `<td class="${colorClass}" title="${row.Cohort} @ Month ${m}: ${val}% Retained (${Math.round((val/100)*row.Cohort_Size)} accounts)">${cellText}</td>`;
        } else {
          rowHtml += `<td class="c-empty">-</td>`;
        }
      }

      tr.innerHTML = rowHtml;
      tbody.appendChild(tr);
    });
  }

  // -------------------------------------------------------------
  // 4. SURVIVAL DECAY CURVE CHART
  // -------------------------------------------------------------
  function initSurvivalChart(survivalData) {
    const ctx = document.getElementById("survivalChart").getContext("2d");
    const colors = getThemeColors();
    const labels = survivalData.map(d => `Month ${d.month}`);
    const values = survivalData.map(d => d.survival_pct);

    chartInstances.survival = new Chart(ctx, {
      type: "line",
      data: {
        labels: labels,
        datasets: [{
          label: "% Customer Survival Probability",
          data: values,
          borderColor: colors.primary,
          backgroundColor: `${colors.primary}25`,
          fill: true,
          tension: 0.35,
          borderWidth: 3,
          pointRadius: 4,
          pointBackgroundColor: colors.primary,
          pointHoverRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: "#0F172A",
            titleColor: "#FFFFFF",
            bodyColor: "#38BDF8",
            borderColor: "rgba(255,255,255,0.1)",
            borderWidth: 1,
            padding: 10,
            callbacks: {
              label: (ctx) => `Survival: ${ctx.parsed.y}% Active`
            }
          }
        },
        scales: {
          x: {
            grid: { color: colors.gridColor },
            ticks: { color: colors.tickColor }
          },
          y: {
            min: 50,
            max: 100,
            grid: { color: colors.gridColor },
            ticks: {
              color: colors.tickColor,
              callback: (v) => `${v}%`
            }
          }
        }
      }
    });
  }

  // -------------------------------------------------------------
  // 5. CHURN DRIVERS & FEATURE IMPORTANCE
  // -------------------------------------------------------------
  function initChurnDriversChart(features) {
    const topFeatures = features.slice(0, 6);
    const ctx = document.getElementById("churnDriversChart").getContext("2d");
    const colors = getThemeColors();

    const labels = topFeatures.map(f => f.feature_name);
    const weights = topFeatures.map(f => f.relative_impact_pct);
    const barColors = topFeatures.map(f => f.odds_ratio > 1.0 ? "#F43F5E" : colors.primary);

    chartInstances.drivers = new Chart(ctx, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [{
          label: "Relative Impact Weight (%)",
          data: weights,
          backgroundColor: barColors,
          borderRadius: 6
        }]
      },
      options: {
        indexAxis: "y",
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: "#0F172A",
            borderColor: "rgba(255,255,255,0.1)",
            borderWidth: 1,
            padding: 10,
            callbacks: {
              label: (ctx) => `Importance: ${ctx.parsed.x}% relative weight`
            }
          }
        },
        scales: {
          x: {
            grid: { color: colors.gridColor },
            ticks: {
              color: colors.tickColor,
              callback: (v) => `${v}%`
            }
          },
          y: {
            grid: { display: false },
            ticks: { color: colors.textColor, font: { weight: "600" } }
          }
        }
      }
    });

    // Populate driver pills
    const pillContainer = document.getElementById("driver-insights-list");
    pillContainer.innerHTML = "";
    topFeatures.forEach(f => {
      const isDanger = f.odds_ratio > 1.0;
      const div = document.createElement("div");
      div.className = "driver-pill";
      div.innerHTML = `
        <div>
          <span class="bold">${f.feature_name}</span>
          <span style="color: #64748B; font-size: 0.78rem; margin-left: 0.4rem;">(${f.relative_impact_pct}% weight)</span>
        </div>
        <span class="risk-tag ${isDanger ? 'danger' : 'safe'}">
          ${isDanger ? 'Increases Churn' : 'Protective Factor'} (OR: ${f.odds_ratio.toFixed(2)})
        </span>
      `;
      pillContainer.appendChild(div);
    });
  }

  // -------------------------------------------------------------
  // 6. CHURN REASONS & REVENUE IMPACT
  // -------------------------------------------------------------
  function initChurnReasonsChart(reasons) {
    const ctx = document.getElementById("churnReasonsChart").getContext("2d");
    const labels = reasons.map(r => r.churn_reason);
    const arrValues = reasons.map(r => r.Lost_ARR);
    const colors = getThemeColors();
    const palette = ["#F43F5E", "#F59E0B", "#6366F1", "#06B6D4", "#EC4899", "#8B5CF6"];

    chartInstances.reasons = new Chart(ctx, {
      type: "doughnut",
      data: {
        labels: labels,
        datasets: [{
          data: arrValues,
          backgroundColor: palette,
          borderColor: colors.doughnutBorder,
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: "right",
            labels: { color: colors.textColor, boxWidth: 12, font: { size: 11, weight: "500" } }
          },
          tooltip: {
            backgroundColor: "#0F172A",
            borderColor: "rgba(255,255,255,0.1)",
            borderWidth: 1,
            padding: 10,
            callbacks: {
              label: (ctx) => `Lost ARR: $${ctx.parsed.toLocaleString()}`
            }
          }
        },
        cutout: "68%"
      }
    });

    // Populate mini table
    const tbody = document.getElementById("reasons-tbody");
    tbody.innerHTML = "";
    const totalLostArr = arrValues.reduce((a, b) => a + b, 0);

    reasons.forEach(r => {
      const tr = document.createElement("tr");
      const pct = ((r.Lost_ARR / totalLostArr) * 100).toFixed(1);
      tr.innerHTML = `
        <td><strong>${r.churn_reason}</strong></td>
        <td>${r.Churned_Customers.toLocaleString()}</td>
        <td>$${Math.round(r.Lost_ARR).toLocaleString()}</td>
        <td>${pct}%</td>
      `;
      tbody.appendChild(tr);
    });
  }

  // -------------------------------------------------------------
  // 7. COMPARATIVE SEGMENTATION CHARTS (FIXED COLORS VARIABLE BUG)
  // -------------------------------------------------------------
  function initSegmentationCharts(kpis) {
    const colors = getThemeColors(); // Critical bug fix!

    // 1. Plan Retention
    const planCtx = document.getElementById("planRetentionChart").getContext("2d");
    const planData = kpis.plan_performance;
    chartInstances.plan = new Chart(planCtx, {
      type: "bar",
      data: {
        labels: planData.map(p => p.subscription_plan),
        datasets: [{
          label: "Retention Rate (%)",
          data: planData.map(p => (100 - p.Churn_Rate).toFixed(1)),
          backgroundColor: ["#10B981", "#6366F1", "#F59E0B"],
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (ctx) => `Retention: ${ctx.parsed.y}%`
            }
          }
        },
        scales: {
          x: { grid: { display: false }, ticks: { color: colors.tickColor } },
          y: {
            min: 30,
            max: 100,
            grid: { color: colors.gridColor },
            ticks: { color: colors.tickColor, callback: (v) => `${v}%` }
          }
        }
      }
    });

    // 2. Contract Retention
    const contractCtx = document.getElementById("contractRetentionChart").getContext("2d");
    const contractData = kpis.contract_performance;
    chartInstances.contract = new Chart(contractCtx, {
      type: "bar",
      data: {
        labels: contractData.map(c => c.billing_cycle),
        datasets: [{
          label: "Retention Rate (%)",
          data: contractData.map(c => c.Retention_Rate),
          backgroundColor: ["#06B6D4", "#F43F5E"],
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (ctx) => `Retention: ${ctx.parsed.y}%`
            }
          }
        },
        scales: {
          x: { grid: { display: false }, ticks: { color: colors.tickColor } },
          y: {
            min: 30,
            max: 100,
            grid: { color: colors.gridColor },
            ticks: { color: colors.tickColor, callback: (v) => `${v}%` }
          }
        }
      }
    });

    // 3. Onboarding Impact
    const onboardCtx = document.getElementById("onboardingImpactChart").getContext("2d");
    const onboardData = kpis.onboarding_impact;
    chartInstances.onboard = new Chart(onboardCtx, {
      type: "bar",
      data: {
        labels: ["Incomplete Onboarding", "Guided Onboarding Completed"],
        datasets: [{
          label: "Retention Rate (%)",
          data: onboardData.map(o => o.Retention_Rate),
          backgroundColor: ["#F43F5E", "#10B981"],
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (ctx) => `Retention: ${ctx.parsed.y}%`
            }
          }
        },
        scales: {
          x: { grid: { display: false }, ticks: { color: colors.tickColor } },
          y: {
            min: 20,
            max: 100,
            grid: { color: colors.gridColor },
            ticks: { color: colors.tickColor, callback: (v) => `${v}%` }
          }
        }
      }
    });
  }

  // -------------------------------------------------------------
  // 8. STRATEGIC CHURN ROI & WHAT-IF SIMULATOR (WITH PRESETS)
  // -------------------------------------------------------------
  function initSimulator() {
    const sOnboard = document.getElementById("slider-onboarding");
    const sAnnual = document.getElementById("slider-annual");
    const sDunning = document.getElementById("slider-dunning");

    const vOnboard = document.getElementById("val-onboarding");
    const vAnnual = document.getElementById("val-annual");
    const vDunning = document.getElementById("val-dunning");

    const simArr = document.getElementById("sim-arr-saved");
    const simMrr = document.getElementById("sim-mrr-saved");
    const simCust = document.getElementById("sim-cust-saved");
    const simGrr = document.getElementById("sim-grr-lift");

    function calculateImpact() {
      const onboardLift = parseInt(sOnboard.value);
      const annualLift = parseInt(sAnnual.value);
      const dunningLift = parseInt(sDunning.value);

      vOnboard.innerText = `+${onboardLift}%`;
      vAnnual.innerText = `+${annualLift}%`;
      vDunning.innerText = `+${dunningLift}%`;

      const arrFromOnboarding = 3768600 * (onboardLift / 100) * 0.42;
      const arrFromAnnual = 1850000 * (annualLift / 100) * 0.55;
      const arrFromDunning = 513384 * (dunningLift / 100) * 0.85;

      const totalArrSaved = arrFromOnboarding + arrFromAnnual + arrFromDunning;
      const totalMrrSaved = totalArrSaved / 12;
      const accountsSaved = Math.round(totalArrSaved / (185 * 12));

      const baselineGrr = 73.5;
      const startingMrr = 2380000;
      const newGrr = (baselineGrr + (totalMrrSaved / startingMrr * 100)).toFixed(1);
      const grrDiff = (newGrr - baselineGrr).toFixed(1);

      simArr.innerText = `+$${Math.round(totalArrSaved).toLocaleString()}`;
      simMrr.innerText = `+$${Math.round(totalMrrSaved).toLocaleString()} / mo`;
      simCust.innerText = `${accountsSaved.toLocaleString()} Accounts`;
      simGrr.innerHTML = `${baselineGrr}% &rarr; <strong>${newGrr}%</strong> (+${grrDiff}%)`;
    }

    sOnboard.addEventListener("input", calculateImpact);
    sAnnual.addEventListener("input", calculateImpact);
    sDunning.addEventListener("input", calculateImpact);

    // Preset Buttons
    const presetBtns = document.querySelectorAll(".preset-btn");
    presetBtns.forEach(btn => {
      btn.addEventListener("click", () => {
        presetBtns.forEach(b => b.classList.remove("active"));
        btn.classList.add("active");

        sOnboard.value = btn.dataset.onboard;
        sAnnual.value = btn.dataset.annual;
        sDunning.value = btn.dataset.dunning;

        calculateImpact();
      });
    });

    calculateImpact();
  }

  // -------------------------------------------------------------
  // 9. CUSTOMER ACCOUNTS TABLE & MODAL
  // -------------------------------------------------------------
  function applyAccountFilters() {
    const searchInput = document.getElementById("account-search-input");
    const riskFilter = document.getElementById("risk-tier-filter");
    const statusFilter = document.getElementById("account-status-filter");
    const segFilter = document.getElementById("segment-filter");
    const planFilter = document.getElementById("plan-filter");
    const billingFilter = document.getElementById("billing-filter");

    const query = searchInput ? searchInput.value.toLowerCase().trim() : "";
    const riskVal = riskFilter ? riskFilter.value : "ALL";
    const statusVal = statusFilter ? statusFilter.value : "ALL";
    const segVal = segFilter ? segFilter.value : "ALL";
    const planVal = planFilter ? planFilter.value : "ALL";
    const billingVal = billingFilter ? billingFilter.value : "ALL";

    currentFilteredAccounts = customerAccounts.filter(acc => {
      const matchesQuery = acc.customer_id.toLowerCase().includes(query) || acc.subscription_plan.toLowerCase().includes(query);
      const matchesRisk = (riskVal === "ALL") || (acc.churn_risk_tier === riskVal);
      const matchesStatus = (statusVal === "ALL") || (acc.churn_status === statusVal);
      const matchesSeg = (segVal === "ALL") || (acc.customer_segment === segVal);
      const matchesPlan = (planVal === "ALL") || (acc.subscription_plan === planVal);
      const matchesBilling = (billingVal === "ALL") || (acc.billing_cycle === billingVal);

      return matchesQuery && matchesRisk && matchesStatus && matchesSeg && matchesPlan && matchesBilling;
    });

    if (currentSort.column) {
      sortAccounts(currentSort.column, true);
    } else {
      accountsPage = 1;
      renderAccountsPage();
    }

    updateDynamicKPIs();
  }

  function sortAccounts(column, keepDirection = false) {
    if (!keepDirection) {
      if (currentSort.column === column) {
        currentSort.direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
      } else {
        currentSort.column = column;
        currentSort.direction = 'asc';
      }
    }

    // Update sort header icons
    document.querySelectorAll(".sortable-th").forEach(th => {
      th.classList.remove("sorted-asc", "sorted-desc");
      const icon = th.querySelector(".sort-icon");
      if (icon) icon.innerText = "↕";
    });

    const activeTh = document.querySelector(`.sortable-th[data-sort="${column}"]`);
    if (activeTh) {
      activeTh.classList.add(currentSort.direction === 'asc' ? "sorted-asc" : "sorted-desc");
      const icon = activeTh.querySelector(".sort-icon");
      if (icon) icon.innerText = currentSort.direction === 'asc' ? "▲" : "▼";
    }

    currentFilteredAccounts.sort((a, b) => {
      let valA = a[column];
      let valB = b[column];

      if (typeof valA === "string") {
        valA = valA.toLowerCase();
        valB = (valB || "").toLowerCase();
      }

      if (valA < valB) return currentSort.direction === 'asc' ? -1 : 1;
      if (valA > valB) return currentSort.direction === 'asc' ? 1 : -1;
      return 0;
    });

    accountsPage = 1;
    renderAccountsPage();
  }

  function renderAccountsPage() {
    const tbody = document.getElementById("accounts-tbody");
    const countSummary = document.getElementById("accounts-count-summary");
    const pageIndicator = document.getElementById("page-indicator");
    const prevBtn = document.getElementById("btn-prev-page");
    const nextBtn = document.getElementById("btn-next-page");

    const totalAccounts = currentFilteredAccounts.length;
    const totalPages = Math.max(1, Math.ceil(totalAccounts / accountsPerPage));

    if (accountsPage > totalPages) accountsPage = totalPages;

    const startIdx = (accountsPage - 1) * accountsPerPage;
    const endIdx = Math.min(startIdx + accountsPerPage, totalAccounts);
    const pageAccounts = currentFilteredAccounts.slice(startIdx, endIdx);

    countSummary.innerText = `Showing ${totalAccounts === 0 ? 0 : startIdx + 1}–${endIdx} of ${totalAccounts} accounts (${customerAccounts.length} total monitored)`;
    pageIndicator.innerText = `Page ${accountsPage} of ${totalPages}`;

    prevBtn.disabled = accountsPage <= 1;
    nextBtn.disabled = accountsPage >= totalPages;

    tbody.innerHTML = "";

    if (pageAccounts.length === 0) {
      tbody.innerHTML = `<tr><td colspan="12" style="text-align:center; padding: 2.5rem; color: #64748B;">No customer accounts match your selected filter criteria.</td></tr>`;
      return;
    }

    pageAccounts.forEach(acc => {
      const tr = document.createElement("tr");

      let riskClass = "low";
      if (acc.churn_risk_tier === "High Risk") riskClass = "high";
      else if (acc.churn_risk_tier === "Medium Risk") riskClass = "medium";

      let interventionPlay = "Routine Check-in";
      if (acc.churn_status === "Churned") {
        interventionPlay = "Win-back Campaign (30% Discount)";
      } else if (acc.payment_failures_count >= 2) {
        interventionPlay = "Automate Card Dunning Sequence";
      } else if (!acc.onboarding_completed) {
        interventionPlay = "Trigger CS Guided Onboarding";
      } else if (acc.billing_cycle === "Monthly" && acc.tenure_months >= 3) {
        interventionPlay = "Offer 15% Annual Upgrade Discount";
      } else if (acc.usage_frequency_days_per_month < 7) {
        interventionPlay = "Schedule Product Re-engagement Call";
      } else if (acc.support_satisfaction_score < 3.0) {
        interventionPlay = "Escalate to Senior Support Lead";
      }

      tr.innerHTML = `
        <td><strong style="color: var(--text-main);">${acc.customer_id}</strong></td>
        <td>${acc.customer_segment}</td>
        <td><span style="font-weight:600;">${acc.subscription_plan}</span></td>
        <td>${acc.billing_cycle}</td>
        <td style="font-family: var(--font-mono);">$${acc.mrr.toFixed(2)}</td>
        <td>${acc.tenure_months}m</td>
        <td>${acc.usage_frequency_days_per_month} d/m</td>
        <td>${acc.support_satisfaction_score.toFixed(1)}</td>
        <td><strong style="font-family: var(--font-mono);">${acc.churn_risk_probability}%</strong></td>
        <td>
          <span class="risk-pill ${riskClass}">
            <span class="risk-dot"></span>
            ${acc.churn_risk_tier}
          </span>
        </td>
        <td><span class="play-badge">${interventionPlay}</span></td>
        <td style="text-align: center;">
          <button class="btn-inspect" data-id="${acc.customer_id}">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
            Inspect
          </button>
        </td>
      `;

      tr.addEventListener("click", () => {
        openAccountModal(acc);
      });

      tbody.appendChild(tr);
    });
  }

  // -------------------------------------------------------------
  // 10. CUSTOMER DETAIL MODAL HANDLERS
  // -------------------------------------------------------------
  function openAccountModal(account) {
    const modal = document.getElementById("account-modal");
    if (!modal) return;

    document.getElementById("modal-cust-id").innerText = account.customer_id;

    // Risk pill
    const riskPill = document.getElementById("modal-risk-pill");
    const riskText = document.getElementById("modal-risk-text");
    riskPill.className = `risk-pill ${account.churn_risk_tier === "High Risk" ? "high" : account.churn_risk_tier === "Medium Risk" ? "medium" : "low"}`;
    riskText.innerText = account.churn_risk_tier;

    // Status chip
    const statusChip = document.getElementById("modal-status-chip");
    statusChip.className = `status-chip ${account.churn_status === "Churned" ? "churned" : ""}`;
    statusChip.innerText = account.churn_status;

    // Stats
    document.getElementById("modal-mrr").innerText = `$${account.mrr.toFixed(2)}/mo`;
    document.getElementById("modal-plan").innerText = `${account.subscription_plan} Plan (${account.billing_cycle})`;
    document.getElementById("modal-churn-prob").innerText = `${account.churn_risk_probability}%`;
    document.getElementById("modal-ltv").innerText = `$${Math.round(account.total_lifetime_revenue || account.mrr * account.tenure_months).toLocaleString()}`;
    document.getElementById("modal-tenure").innerText = `${account.tenure_months} Months Active`;
    document.getElementById("modal-csat").innerText = `${account.support_satisfaction_score.toFixed(1)} / 5.0`;
    document.getElementById("modal-usage").innerText = `${account.usage_frequency_days_per_month} Active Days / Mo`;

    // Signals
    const signalsContainer = document.getElementById("modal-signals");
    signalsContainer.innerHTML = `
      <div class="signal-chip">
        <span class="sig-lbl">Customer Segment</span>
        <span class="sig-val">${account.customer_segment}</span>
      </div>
      <div class="signal-chip">
        <span class="sig-lbl">Guided Onboarding</span>
        <span class="sig-val" style="color: ${account.onboarding_completed ? 'var(--accent-emerald)' : 'var(--accent-rose)'};">
          ${account.onboarding_completed ? 'Completed' : 'Incomplete'}
        </span>
      </div>
      <div class="signal-chip">
        <span class="sig-lbl">Payment Failures</span>
        <span class="sig-val" style="color: ${account.payment_failures_count > 0 ? 'var(--accent-rose)' : 'var(--text-main)'};">
          ${account.payment_failures_count} Failed Retries
        </span>
      </div>
      <div class="signal-chip">
        <span class="sig-lbl">Primary Churn Reason</span>
        <span class="sig-val">${account.churn_reason || 'None (Active Account)'}</span>
      </div>
    `;

    // Playbook recommendation
    let playDesc = "Schedule routine health check-in and review expansion seat opportunities.";
    if (account.churn_status === "Churned") {
      playDesc = "Trigger automated Win-Back sequence with a 30% re-activation incentive and executive exit interview.";
    } else if (account.payment_failures_count >= 2) {
      playDesc = "Automate Stripe/Recurly smart payment retry sequence and request secondary payment method.";
    } else if (!account.onboarding_completed) {
      playDesc = "Deploy in-app interactive setup tour and assign an Onboarding Specialist within 24 hours.";
    } else if (account.billing_cycle === "Monthly" && account.tenure_months >= 3) {
      playDesc = "Present Day 45 Annual Migration Offer: 15% discount (2 months free) to lock in annual retention.";
    } else if (account.usage_frequency_days_per_month < 8) {
      playDesc = "Trigger low-engagement alert; schedule executive consultation to audit feature adoption.";
    } else if (account.support_satisfaction_score < 3.0) {
      playDesc = "CS Escalation SLA: Senior Support Lead personal call within 24 hours to resolve open grievances.";
    }
    document.getElementById("modal-play-desc").innerText = playDesc;

    // Action button handlers
    const copyBtn = document.getElementById("modal-copy-btn");
    copyBtn.onclick = (e) => {
      e.stopPropagation();
      navigator.clipboard.writeText(account.customer_id).then(() => {
        showToast(`Copied ${account.customer_id} to clipboard!`);
      }).catch(() => {
        showToast(`Account ID: ${account.customer_id}`);
      });
    };

    const actionBtn = document.getElementById("modal-action-btn");
    actionBtn.onclick = (e) => {
      e.stopPropagation();
      showToast(`Outreach Playbook initiated for ${account.customer_id}!`);
      actionBtn.innerHTML = `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><polyline points="20 6 9 17 4 12"/></svg> Outreach Scheduled`;
      actionBtn.classList.remove("btn-primary");
      actionBtn.classList.add("btn-secondary");
    };

    modal.style.display = "flex";
    setTimeout(() => modal.classList.add("active"), 10);
  }

  function closeAccountModal() {
    const modal = document.getElementById("account-modal");
    if (!modal) return;
    modal.classList.remove("active");
    setTimeout(() => {
      modal.style.display = "none";
    }, 250);
  }

  // -------------------------------------------------------------
  // 11. CSV EXPORT
  // -------------------------------------------------------------
  function exportAccountsToCSV() {
    if (currentFilteredAccounts.length === 0) {
      showToast("No accounts available to export with current filters.");
      return;
    }

    showToast(`Exporting ${currentFilteredAccounts.length} customer records to CSV...`);

    const headers = [
      "Customer ID", "Segment", "Plan Tier", "Billing Cycle", "MRR",
      "Tenure Months", "Onboarding Completed", "Active Days/Mo",
      "CSAT Score", "Payment Failures", "Churn Status", "Churn Reason",
      "Churn Risk %", "Risk Tier"
    ];

    const rows = currentFilteredAccounts.map(a => [
      a.customer_id,
      a.customer_segment,
      a.subscription_plan,
      a.billing_cycle,
      a.mrr,
      a.tenure_months,
      a.onboarding_completed,
      a.usage_frequency_days_per_month,
      a.support_satisfaction_score,
      a.payment_failures_count,
      a.churn_status,
      `"${a.churn_reason || 'None'}"`,
      a.churn_risk_probability,
      a.churn_risk_tier
    ]);

    const csvContent = "data:text/csv;charset=utf-8," 
      + [headers.join(","), ...rows.map(e => e.join(","))].join("\n");

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `SaaS_Customer_Accounts_Export_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  // -------------------------------------------------------------
  // 12. SCROLL SPY & SIDEBAR SYNC
  // -------------------------------------------------------------
  function initScrollSpy() {
    const sections = document.querySelectorAll(".dashboard-section");
    const navItems = document.querySelectorAll(".nav-item");

    window.addEventListener("scroll", () => {
      let currentSectionId = "";
      const scrollPos = window.scrollY + 200;

      sections.forEach(sec => {
        if (sec.offsetTop <= scrollPos) {
          currentSectionId = sec.getAttribute("id");
        }
      });

      if (currentSectionId) {
        navItems.forEach(item => {
          if (item.getAttribute("href") === `#${currentSectionId}`) {
            item.classList.add("active");
          } else {
            item.classList.remove("active");
          }
        });
      }
    }, { passive: true });
  }

  // -------------------------------------------------------------
  // 13. EVENT LISTENERS
  // -------------------------------------------------------------
  function setupEventListeners() {
    // Theme Selector
    const themeSelect = document.getElementById("theme-selector");
    if (themeSelect) {
      themeSelect.addEventListener("change", (e) => {
        applyTheme(e.target.value);
      });
    }

    // Font Style Selector
    const fontSelect = document.getElementById("font-selector");
    if (fontSelect) {
      fontSelect.addEventListener("change", (e) => {
        applyFont(e.target.value);
      });
    }

    // Cohort Heatmap Filters
    const periodSelect = document.getElementById("cohort-period-select");
    const metricSelect = document.getElementById("cohort-metric-select");

    if (periodSelect) periodSelect.addEventListener("change", renderCohortHeatmap);
    if (metricSelect) metricSelect.addEventListener("change", renderCohortHeatmap);

    // Heatmap vs Survival Curve View Toggle
    const btnHeatmap = document.getElementById("toggle-heatmap");
    const btnSurvival = document.getElementById("toggle-survival");
    const heatmapContainer = document.getElementById("cohort-heatmap-container");
    const survivalContainer = document.getElementById("survival-chart-container");

    btnHeatmap.addEventListener("click", () => {
      btnHeatmap.classList.add("active");
      btnSurvival.classList.remove("active");
      heatmapContainer.style.display = "block";
      survivalContainer.style.display = "none";
    });

    btnSurvival.addEventListener("click", () => {
      btnSurvival.classList.add("active");
      btnHeatmap.classList.remove("active");
      heatmapContainer.style.display = "none";
      survivalContainer.style.display = "block";
    });

    // Accounts Search & Filters
    const searchInput = document.getElementById("account-search-input");
    const riskFilter = document.getElementById("risk-tier-filter");
    const statusFilter = document.getElementById("account-status-filter");
    const segFilter = document.getElementById("segment-filter");
    const planFilter = document.getElementById("plan-filter");
    const billingFilter = document.getElementById("billing-filter");
    const rowsSelect = document.getElementById("rows-per-page-select");
    const resetFiltersBtn = document.getElementById("reset-global-filters-btn");

    if (searchInput) searchInput.addEventListener("input", applyAccountFilters);
    if (riskFilter) riskFilter.addEventListener("change", applyAccountFilters);
    if (statusFilter) statusFilter.addEventListener("change", applyAccountFilters);
    if (segFilter) segFilter.addEventListener("change", applyAccountFilters);
    if (planFilter) planFilter.addEventListener("change", applyAccountFilters);
    if (billingFilter) billingFilter.addEventListener("change", applyAccountFilters);

    if (resetFiltersBtn) {
      resetFiltersBtn.addEventListener("click", () => {
        if (segFilter) segFilter.value = "ALL";
        if (planFilter) planFilter.value = "ALL";
        if (billingFilter) billingFilter.value = "ALL";
        if (riskFilter) riskFilter.value = "ALL";
        if (statusFilter) statusFilter.value = "ALL";
        if (searchInput) searchInput.value = "";
        applyAccountFilters();
        showToast("Global filters reset to default");
      });
    }

    // High Risk Banner Inspect Button
    const viewHighRiskBtn = document.getElementById("btn-view-high-risk");
    if (viewHighRiskBtn) {
      viewHighRiskBtn.addEventListener("click", (e) => {
        if (riskFilter) riskFilter.value = "High Risk";
        if (statusFilter) statusFilter.value = "Active";
        applyAccountFilters();
      });
    }

    // Table Column Sorting
    document.querySelectorAll(".sortable-th").forEach(th => {
      th.addEventListener("click", () => {
        const col = th.dataset.sort;
        if (col) sortAccounts(col);
      });
    });

    // Rows Per Page Select
    if (rowsSelect) {
      rowsSelect.addEventListener("change", (e) => {
        accountsPerPage = parseInt(e.target.value);
        accountsPage = 1;
        renderAccountsPage();
      });
    }

    // Pagination Buttons
    document.getElementById("btn-prev-page").addEventListener("click", () => {
      if (accountsPage > 1) {
        accountsPage--;
        renderAccountsPage();
      }
    });

    document.getElementById("btn-next-page").addEventListener("click", () => {
      accountsPage++;
      renderAccountsPage();
    });

    // CSV Export & Print
    const csvBtn = document.getElementById("export-csv-btn");
    if (csvBtn) csvBtn.addEventListener("click", exportAccountsToCSV);

    document.getElementById("export-report-btn").addEventListener("click", () => {
      window.print();
    });

    // Modal Close Listeners
    const modalCloseBtn = document.getElementById("modal-close-btn");
    const accountModal = document.getElementById("account-modal");
    if (modalCloseBtn) modalCloseBtn.addEventListener("click", closeAccountModal);

    if (accountModal) {
      accountModal.addEventListener("click", (e) => {
        if (e.target === accountModal) closeAccountModal();
      });
    }

    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") closeAccountModal();
    });

    // Mobile Menu Toggle
    const mobileToggle = document.getElementById("mobile-menu-toggle");
    const sidebar = document.getElementById("sidebar");
    if (mobileToggle && sidebar) {
      mobileToggle.addEventListener("click", () => {
        sidebar.classList.toggle("mobile-open");
      });
    }

    // Smooth Navigation Links
    const navItems = document.querySelectorAll(".nav-item");
    navItems.forEach(item => {
      item.addEventListener("click", () => {
        navItems.forEach(n => n.classList.remove("active"));
        item.classList.add("active");
        if (sidebar && sidebar.classList.contains("mobile-open")) {
          sidebar.classList.remove("mobile-open");
        }
      });
    });
  }
});
