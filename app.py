import streamlit as st
import pandas as pd

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Strategy Performance Dashboard",
    layout="wide"
)

st.title("📈 Strategy Performance Dashboard")
st.caption("Portfolio-level performance analysis | Created by Nitin Joshi")

st.divider()

# =========================
# FILE UPLOAD (MULTIPLE CSV)
# =========================
dashboard_files = st.file_uploader(
    "Upload one or more merged trade report CSVs",
    type=["csv"],
    accept_multiple_files=True
)

# =========================
# USER INPUTS
# =========================
total_capital = st.number_input(
    "Total Portfolio Capital (₹)",
    min_value=1,
    value=300000,
    step=50000
)

total_charges = st.number_input(
    "Total Portfolio Charges (₹)",
    min_value=0,
    value=0,
    step=1000
)

# =========================
# PROCESS DATA
# =========================
if dashboard_files:

    df_list = []

    for file in dashboard_files:
        temp_df = pd.read_csv(file)
        df_list.append(temp_df)

    df = pd.concat(df_list, ignore_index=True)

    # -------------------------
    # PREP DATA
    # -------------------------
    df["Entry Date"] = pd.to_datetime(df["Entry Date"])
    df = df.sort_values("Entry Date").reset_index(drop=True)

    total_trades = len(df)

    # -------------------------
    # APPLY CHARGES
    # -------------------------
    charge_per_trade = total_charges / total_trades if total_trades > 0 else 0
    df["Net P/L"] = df["P/L"] - charge_per_trade

    # -------------------------
    # EQUITY & DRAWDOWN
    # -------------------------
    df["Equity"] = total_capital + df["Net P/L"].cumsum()
    df["Peak Equity"] = df["Equity"].cummax()
    df["Drawdown"] = df["Equity"] - df["Peak Equity"]
    df["Drawdown %"] = (df["Drawdown"] / total_capital) * 100

    # -------------------------
    # METRICS
    # -------------------------
    total_profit = df["Net P/L"].sum()
    total_return_pct = (total_profit / total_capital) * 100

    monthly_pnl = df.groupby(df["Entry Date"].dt.to_period("M"))["Net P/L"].sum()
    avg_monthly_profit = monthly_pnl.mean()
    avg_monthly_profit_pct = (avg_monthly_profit / total_capital) * 100

    yearly_pnl = df.groupby(df["Entry Date"].dt.year)["Net P/L"].sum()

    max_dd = df["Drawdown"].min()
    max_dd_pct = df["Drawdown %"].min()

    # =========================
    # METRIC CARDS
    # =========================
    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric("Total Profit", f"₹{total_profit:,.0f}")
    c2.metric("Total Return", f"{total_return_pct:.2f}%")
    c3.metric("Total Capital", f"₹{total_capital:,.0f}")
    c4.metric("Avg Monthly Profit", f"₹{avg_monthly_profit:,.0f}")
    c5.metric("Avg Monthly Profit %", f"{avg_monthly_profit_pct:.2f}%")

    st.markdown("---")

    # =========================
    # CHARTS
    # =========================
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📈 Equity Curve")
        st.line_chart(df.set_index("Entry Date")["Equity"])

    with col2:
        st.subheader("📊 Yearly PnL")
        st.bar_chart(yearly_pnl)

    st.markdown("---")

    col3, col4 = st.columns([2, 1])

    with col3:
        st.subheader("📉 Drawdown Curve")
        st.line_chart(df.set_index("Entry Date")["Drawdown"])

    with col4:
        st.metric(
            "Max Drawdown",
            f"₹{abs(max_dd):,.0f}",
            f"{max_dd_pct:.2f}%"
        )

    # =========================
    # MONTHLY & YEARLY TABLE
    # =========================
    st.markdown("---")
    st.subheader("📊 Monthly & Yearly PnL Summary")

    show_percentage = st.checkbox("Show PnL in Percentage (%)", value=False)

    df["Year"] = df["Entry Date"].dt.year
    df["Month"] = df["]()
