from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "processed" / "order_business_summary.parquet"
CATEGORY_FILE = ROOT / "reports" / "category_performance.csv"
FORECAST_FILE = ROOT / "reports" / "sales_forecast.csv"
FORECAST_METRICS_FILE = ROOT / "reports" / "sales_forecast_metrics.csv"

st.set_page_config(
    page_title="ProfitOS | Business Decision Engine",
    page_icon="📊",
    layout="wide",
)

st.title("ProfitOS")
st.caption("AI Business Decision Engine | E-commerce Analytics")


# --------------------------------------------------
# DATA LOADING AND HELPERS
# --------------------------------------------------
@st.cache_data

def load_data():
    if not DATA_FILE.exists():
        return pd.DataFrame()

    data = pd.read_parquet(DATA_FILE)
    required = {
        "order_id", "purchase_timestamp", "order_status", "item_sales",
        "freight_charged",
    }
    missing = sorted(required - set(data.columns))
    if missing:
        raise ValueError(
            "The processed order summary is missing required columns: "
            + ", ".join(missing)
        )

    data["purchase_timestamp"] = pd.to_datetime(
        data["purchase_timestamp"], errors="coerce"
    )
    for column in ("item_sales", "freight_charged"):
        data[column] = pd.to_numeric(data[column], errors="coerce").fillna(0)
    data["order_status"] = data["order_status"].fillna("unknown").astype(str)
    return data.dropna(subset=["purchase_timestamp"]).copy()


@st.cache_data

def load_categories():
    if not CATEGORY_FILE.exists():
        return pd.DataFrame()
    category_data = pd.read_csv(CATEGORY_FILE)
    if "item_sales" in category_data.columns:
        category_data["item_sales"] = pd.to_numeric(
            category_data["item_sales"], errors="coerce"
        ).fillna(0)
    return category_data


def format_brl(value):
    """Format Brazilian real values compactly."""
    value = float(value or 0)
    if abs(value) >= 1_000_000:
        return f"R${value / 1_000_000:.2f}M"
    if abs(value) >= 1_000:
        return f"R${value / 1_000:.1f}K"
    return f"R${value:,.2f}"


def empty_message(message):
    st.info(message)


df = load_data()
categories = load_categories()

if df.empty:
    st.error(
        "No processed order data was found. Confirm that "
        "data/processed/order_business_summary.parquet exists and contains data."
    )
    st.stop()


# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------
st.sidebar.header("Dashboard Filters")
min_date = df["purchase_timestamp"].min().date()
max_date = df["purchase_timestamp"].max().date()

date_range = st.sidebar.date_input(
    "Purchase date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

statuses = sorted(df["order_status"].dropna().unique().tolist())
selected_statuses = st.sidebar.multiselect(
    "Order status", options=statuses, default=statuses
)


# --------------------------------------------------
# FILTER DATA
# --------------------------------------------------
filtered = df.copy()
if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range
    filtered = filtered[
        filtered["purchase_timestamp"].dt.date.between(start_date, end_date)
    ].copy()
elif isinstance(date_range, (tuple, list)) and len(date_range) == 1:
    selected_day = date_range[0]
    filtered = filtered[filtered["purchase_timestamp"].dt.date == selected_day].copy()

filtered = filtered[filtered["order_status"].isin(selected_statuses)].copy()
if filtered.empty:
    st.warning("No orders match the selected filters. Adjust the date range or order status.")
    st.stop()


# --------------------------------------------------
# KPI CALCULATIONS
# --------------------------------------------------
total_orders = int(filtered["order_id"].nunique())
delivered_orders = int(
    filtered.loc[filtered["order_status"].eq("delivered"), "order_id"].nunique()
)
sales = float(filtered["item_sales"].sum())
freight = float(filtered["freight_charged"].sum())
delivery_rate = delivered_orders / total_orders * 100 if total_orders else 0.0

k1, k2, k3, k4 = st.columns(4)
k1.metric("Orders", f"{total_orders:,}")
k2.metric("Item Sales", format_brl(sales))
k3.metric("Freight Charged", format_brl(freight))
k4.metric("Delivered Order Rate", f"{delivery_rate:.1f}%")
st.caption(
    "Item sales and freight are observed dataset measures; they do not represent profit. "
    "The delivered-order rate is the share of distinct filtered orders whose status is delivered."
)
st.divider()


# --------------------------------------------------
# MONTHLY AGGREGATION
# --------------------------------------------------
monthly = (
    filtered.assign(
        month=filtered["purchase_timestamp"].dt.to_period("M").dt.to_timestamp()
    )
    .groupby("month", as_index=False)
    .agg(
        orders=("order_id", "nunique"),
        item_sales=("item_sales", "sum"),
        freight=("freight_charged", "sum"),
    )
    .sort_values("month")
)

# This is a review threshold, not a claim that the source data is incomplete.
monthly["is_sparse"] = monthly["orders"] < 100


# --------------------------------------------------
# BUSINESS INSIGHTS
# --------------------------------------------------
st.subheader("Business Insights")
if not monthly.empty:
    best_sales_month = monthly.loc[monthly["item_sales"].idxmax()]
    best_order_month = monthly.loc[monthly["orders"].idxmax()]
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Highest Item-Sales Month**")
        st.write(
            f"{best_sales_month['month']:%B %Y}: "
            f"{format_brl(best_sales_month['item_sales'])} across "
            f"{int(best_sales_month['orders']):,} orders."
        )

    with col2:
        st.markdown("**Highest Order-Volume Month**")
        st.write(
            f"{best_order_month['month']:%B %Y}: "
            f"{int(best_order_month['orders']):,} orders."
        )

    low_volume = monthly.loc[monthly["is_sparse"]]
    if not low_volume.empty:
        flagged_months = ", ".join(low_volume["month"].dt.strftime("%B %Y"))
        st.warning(
            "Data-quality review recommended for unusually low-volume months: "
            f"{flagged_months}. Low volume is a review signal, not proof of incomplete data."
        )

    if not categories.empty and {"category", "item_sales"}.issubset(categories.columns):
        top_category = categories.loc[categories["item_sales"].idxmax()]
        st.markdown("**Leading Product Category**")
        st.write(
            f"{top_category['category']} has the highest recorded category item sales: "
            f"{format_brl(top_category['item_sales'])}."
        )
        st.caption("The category report uses the full dataset; other insights use the selected filters.")

    st.caption(
        "These findings describe recorded data. Sparse months are flagged for review, "
        "not automatically excluded. Item sales are not profit."
    )
else:
    empty_message("No monthly data is available for the current selection.")

st.divider()


# --------------------------------------------------
# MONTHLY CHARTS
# --------------------------------------------------
left, right = st.columns(2)

with left:
    st.subheader("Monthly Item Sales")
    # Keep sparse months visible as orange points, but don't connect them into the main trend.
    sales_trend = monthly.copy()
    sales_trend["regular_sales"] = sales_trend["item_sales"].where(~sales_trend["is_sparse"])
    fig = px.line(
        sales_trend,
        x="month",
        y="regular_sales",
        markers=True,
        labels={"month": "Month", "regular_sales": "Item Sales (R$)"},
        hover_data={"orders": True, "is_sparse": True},
    )
    sparse_sales = sales_trend[sales_trend["is_sparse"]]
    if not sparse_sales.empty:
        sparse_points = px.scatter(
            sparse_sales,
            x="month",
            y="item_sales",
            hover_data={"orders": True, "is_sparse": True},
            labels={"month": "Month", "item_sales": "Item Sales (R$)"},
        )
        for trace in sparse_points.data:
            trace.name = "Sparse month (review)"
            trace.marker.color = "#F4A261"
            trace.marker.size = 10
            fig.add_trace(trace)
    fig.update_layout(xaxis_title="Month", yaxis_title="Item Sales (R$)")
    st.plotly_chart(fig, width="stretch")
    if not sparse_sales.empty:
        st.caption(
            "Orange points mark months with fewer than 100 orders. They remain in the data; "
            "the threshold is a review aid and does not prove incompleteness."
        )

with right:
    st.subheader("Monthly Order Volume")
    orders_chart = monthly.copy()
    orders_chart["period_type"] = orders_chart["is_sparse"].map(
        {True: "Sparse month (review)", False: "Regular month"}
    )
    fig = px.bar(
        orders_chart,
        x="month",
        y="orders",
        color="period_type",
        color_discrete_map={
            "Regular month": "#7CC4FA",
            "Sparse month (review)": "#F4A261",
        },
        labels={"month": "Month", "orders": "Orders", "period_type": "Month type"},
        hover_data={"item_sales": ":,.2f"},
    )
    fig.update_layout(xaxis_title="Month", yaxis_title="Orders", legend_title_text="")
    st.plotly_chart(fig, width="stretch")

st.divider()


# --------------------------------------------------
# SALES FORECAST
# --------------------------------------------------
st.subheader("Historical Three-Month Item-Sales Forecast")
st.warning(
    "Historical forecast only: the available dataset ends in October 2018. "
    "The forecast below follows August 2018 and is not a prediction for 2026. "
    "September and October 2018 contain unusually few recorded orders and "
    "should be treated as sparse months requiring review."
)

# Show the model comparison produced by the rolling-origin backtest.
if FORECAST_METRICS_FILE.exists():
    metrics_df = pd.read_csv(FORECAST_METRICS_FILE)
    expected_metric_cols = {
        "model", "backtest_windows", "average_MAE",
        "average_RMSE", "average_WAPE_percent"
    }
    if expected_metric_cols.issubset(metrics_df.columns) and not metrics_df.empty:
        metrics_df["average_WAPE_percent"] = pd.to_numeric(
            metrics_df["average_WAPE_percent"], errors="coerce"
        )
        metrics_df = metrics_df.sort_values(
            "average_WAPE_percent", na_position="last"
        )
        best_metric = metrics_df.dropna(
            subset=["average_WAPE_percent"]
        ).head(1)

        if not best_metric.empty:
            best_row = best_metric.iloc[0]
            st.markdown("**Rolling Backtest Model Comparison**")
            m1, m2 = st.columns(2)
            m1.metric("Selected by lowest average WAPE", str(best_row["model"]))
            m2.metric(
                "Average validation WAPE",
                f"{best_row['average_WAPE_percent']:.2f}%"
            )
        st.dataframe(
            metrics_df.round({
                "average_MAE": 2,
                "average_RMSE": 2,
                "average_WAPE_percent": 2,
            }),
            width="stretch",
            hide_index=True,
        )
        st.caption(
            "Metrics summarize rolling validation windows in the current "
            "backtest report. They are historical diagnostics, not a guarantee "
            "of future accuracy."
        )
    else:
        st.info(
            "The metrics file does not contain the expected rolling-backtest "
            "columns. Run python src/profitos/sales_forecast.py to regenerate it."
        )
else:
    st.info(
        "Model metrics not found. Run python src/profitos/sales_forecast.py "
        "to generate the rolling-backtest report."
    )

if FORECAST_FILE.exists():
    forecast_df = pd.read_csv(FORECAST_FILE)
    expected_forecast_cols = {"forecast_month", "forecast_item_sales"}
    if not expected_forecast_cols.issubset(forecast_df.columns):
        st.warning(
            "The forecast file doesn't contain the expected columns: "
            "forecast_month and forecast_item_sales. Regenerate it using "
            "the project's forecast script."
        )
    else:
        forecast_df["forecast_month"] = pd.to_datetime(
            forecast_df["forecast_month"], errors="coerce"
        )
        forecast_df["forecast_item_sales"] = pd.to_numeric(
            forecast_df["forecast_item_sales"], errors="coerce"
        )
        forecast_df = forecast_df.dropna(
            subset=["forecast_month", "forecast_item_sales"]
        )

        selected_model = None
        if "selected_model" in forecast_df.columns and not forecast_df.empty:
            selected_model = str(forecast_df["selected_model"].iloc[0])

        if selected_model:
            st.caption(f"Forecast model selected by backtesting: **{selected_model}**")

        # Historical data is displayed only through the final training month.
        historical = (
            df.assign(
                month=df["purchase_timestamp"].dt.to_period("M").dt.to_timestamp()
            )
            .groupby("month", as_index=False)["item_sales"]
            .sum()
        )
        historical = historical[
            historical["month"] <= pd.Timestamp("2018-08-01")
        ].copy()
        historical = historical.rename(
            columns={"month": "forecast_month", "item_sales": "sales_value"}
        )
        historical["series"] = "Historical item sales"

        forecast_plot = forecast_df.rename(
            columns={"forecast_item_sales": "sales_value"}
        ).copy()
        forecast_plot["series"] = "Historical forecast (2018)"

        plot_data = pd.concat(
            [
                historical[["forecast_month", "sales_value", "series"]],
                forecast_plot[["forecast_month", "sales_value", "series"]],
            ],
            ignore_index=True,
        )

        if not plot_data.empty:
            fig = px.line(
                plot_data,
                x="forecast_month",
                y="sales_value",
                color="series",
                markers=True,
                labels={
                    "forecast_month": "Month",
                    "sales_value": "Item sales (R$)",
                    "series": "Series",
                },
                title="Historical Item Sales and 2018 Forecast",
            )
            fig.update_layout(yaxis_tickprefix="R$", yaxis_tickformat=",.0f")
            st.plotly_chart(fig, width="stretch")

            display_forecast = forecast_df.copy()
            display_forecast["forecast_month"] = (
                display_forecast["forecast_month"].dt.strftime("%B %Y")
            )
            display_forecast["forecast_item_sales"] = (
                display_forecast["forecast_item_sales"].map(
                    lambda value: f"R${value:,.2f}"
                )
            )
            st.dataframe(display_forecast, width="stretch", hide_index=True)

        st.caption(
            "Forecast values are item-sales estimates, not actual results or profit. "
            "The selected model is based on historical backtests and should be "
            "re-evaluated if the data or forecast horizon changes."
        )
else:
    st.info(
        "Forecast file not found. Run python src/profitos/sales_forecast.py first."
    )

st.divider()


# --------------------------------------------------
# ORDER STATUS AND CATEGORY ANALYSIS
# --------------------------------------------------
left, right = st.columns(2)
with left:
    st.subheader("Order Status Breakdown")
    status_data = (
        filtered.groupby("order_status", as_index=False)["order_id"]
        .nunique()
        .rename(columns={"order_id": "orders"})
        .sort_values("orders", ascending=False)
    )
    fig = px.bar(
        status_data,
        x="order_status",
        y="orders",
        color="order_status",
        labels={"order_status": "Order Status", "orders": "Number of Orders"},
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, width="stretch")

with right:
    st.subheader("Top Product Categories")
    if not categories.empty and {"category", "item_sales"}.issubset(categories.columns):
        top_categories = categories.nlargest(10, "item_sales").sort_values("item_sales")
        fig = px.bar(
            top_categories,
            x="item_sales",
            y="category",
            orientation="h",
            labels={"item_sales": "Item Sales (R$)", "category": "Category"},
        )
        fig.update_layout(xaxis_tickprefix="R$", xaxis_tickformat=",.0f")
        st.plotly_chart(fig, width="stretch")
    else:
        st.info("Category report is unavailable or missing category/item_sales columns.")

st.divider()


# --------------------------------------------------
# BUSINESS SCENARIO SIMULATOR
# --------------------------------------------------
st.subheader("Business Scenario Simulator")
st.write(
    "Explore how assumed changes in monthly order volume, average item value, and costs "
    "could affect a modeled operating contribution."
)
st.info(
    "Illustrative scenario only: item sales are a revenue proxy, and the source dataset does not "
    "contain a complete cost ledger. The contribution below is not actual accounting profit."
)

# Use typical non-sparse months as an editable reference baseline.
regular_months = monthly.loc[~monthly["is_sparse"]]
if regular_months.empty:
    regular_months = monthly
baseline_orders_default = max(1, int(round(regular_months["orders"].median())))
baseline_sales_default = max(0.0, float(regular_months["item_sales"].median()))

with st.expander("Adjust scenario assumptions", expanded=True):
    c1, c2 = st.columns(2)
    with c1:
        baseline_orders = st.number_input(
            "Baseline monthly orders", min_value=1, max_value=10_000_000,
            value=baseline_orders_default, step=100, key="sim_baseline_orders",
        )
        baseline_item_sales = st.number_input(
            "Baseline monthly item sales (R$)", min_value=0.0, max_value=1_000_000_000_000.0,
            value=baseline_sales_default, step=25_000.0, key="sim_baseline_sales",
        )
        order_growth_pct = st.slider(
            "Expected order growth (%)", min_value=-50, max_value=100,
            value=10, step=5, key="sim_order_growth",
        )
    with c2:
        item_value_change_pct = st.slider(
            "Average item value change (%)", min_value=-30, max_value=50,
            value=5, step=5, key="sim_item_value_change",
        )
        variable_cost_pct = st.slider(
            "Assumed variable cost rate (%)", min_value=0, max_value=100,
            value=60, step=5, key="sim_variable_cost",
        )
        fixed_monthly_costs = st.number_input(
            "Assumed fixed monthly costs (R$)", min_value=0.0,
            max_value=1_000_000_000_000.0, value=100_000.0,
            step=10_000.0, key="sim_fixed_costs",
        )

baseline_average_sales_per_order = baseline_item_sales / baseline_orders
scenario_orders = baseline_orders * (1 + order_growth_pct / 100)
scenario_average_sales_per_order = baseline_average_sales_per_order * (1 + item_value_change_pct / 100)
scenario_item_sales = scenario_orders * scenario_average_sales_per_order
baseline_variable_costs = baseline_item_sales * variable_cost_pct / 100
scenario_variable_costs = scenario_item_sales * variable_cost_pct / 100
baseline_contribution = baseline_item_sales - baseline_variable_costs - fixed_monthly_costs
scenario_contribution = scenario_item_sales - scenario_variable_costs - fixed_monthly_costs

m1, m2, m3 = st.columns(3)
m1.metric(
    "Scenario monthly item sales", format_brl(scenario_item_sales),
    delta=f"{scenario_item_sales - baseline_item_sales:+,.2f} R$ vs baseline",
)
m2.metric(
    "Scenario monthly orders", f"{scenario_orders:,.0f}",
    delta=f"{scenario_orders - baseline_orders:+,.0f} orders",
)
m3.metric(
    "Modeled operating contribution", format_brl(scenario_contribution),
    delta=f"{scenario_contribution - baseline_contribution:+,.2f} R$ vs baseline",
)

scenario_table = pd.DataFrame({
    "Metric": [
        "Monthly orders",
        "Average item sales per order (R$)",
        "Monthly item sales (R$)",
        "Assumed variable costs (R$)",
        "Assumed fixed costs (R$)",
        "Modeled operating contribution (R$)",
    ],
    "Baseline": [
        baseline_orders,
        baseline_average_sales_per_order,
        baseline_item_sales,
        baseline_variable_costs,
        fixed_monthly_costs,
        baseline_contribution,
    ],
    "Scenario": [
        scenario_orders,
        scenario_average_sales_per_order,
        scenario_item_sales,
        scenario_variable_costs,
        fixed_monthly_costs,
        scenario_contribution,
    ],
})
scenario_table["Change"] = scenario_table["Scenario"] - scenario_table["Baseline"]
st.dataframe(scenario_table.round(2), width="stretch", hide_index=True)
st.download_button(
    "Download Scenario Comparison (CSV)",
    data=scenario_table.to_csv(index=False).encode("utf-8"),
    file_name="profitos_scenario_comparison.csv",
    mime="text/csv",
)
st.caption(
    "Baseline defaults use the median of non-sparse months in the current filter selection when available. "
    "All cost rates and fixed costs are assumptions supplied by the user."
)


# --------------------------------------------------
# FILTERED ORDER TABLE AND EXPORT
# --------------------------------------------------
st.divider()
st.subheader("Filtered Order Data")
display_columns = [
    "order_id", "purchase_timestamp", "order_status", "item_count",
    "item_sales", "freight_charged", "total_payment_value",
]
available_columns = [column for column in display_columns if column in filtered.columns]
if available_columns:
    display_data = filtered[available_columns].sort_values(
        "purchase_timestamp", ascending=False
    )
    st.dataframe(display_data, width="stretch", hide_index=True)
else:
    st.info("No displayable order columns are available.")

csv_data = filtered.to_csv(index=False).encode("utf-8")
st.download_button(
    "Download Filtered Orders (CSV)",
    data=csv_data,
    file_name="profitos_filtered_orders.csv",
    mime="text/csv",
)
st.caption("ProfitOS | Portfolio Project | Data Source: Olist Brazilian E-commerce")
