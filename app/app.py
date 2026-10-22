from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "processed" / "order_business_summary.parquet"
CATEGORY_FILE = ROOT / "reports" / "category_performance.csv"
FORECAST_FILE = ROOT / "reports" / "sales_forecast.csv"
FORECAST_METRICS_FILE = ROOT / "reports" / "sales_forecast_metrics.csv"

st.set_page_config(page_title="ProfitOS | Business Intelligence", page_icon="📊", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
:root{--bg:#080d1a;--panel:#111a2e;--line:#293b5d;--text:#f4f7ff;--muted:#9caecc;--cyan:#38d9ff;--violet:#a78bfa;--green:#46e6a5;--amber:#ffb86b}
.stApp{background:radial-gradient(ellipse at 7% 0%,rgba(56,217,255,.12),transparent 30%),radial-gradient(ellipse at 94% 4%,rgba(167,139,250,.13),transparent 28%),linear-gradient(145deg,#080d1a 0%,#0b1222 50%,#080d1a 100%);color:var(--text);font-family:'DM Sans',sans-serif}
[data-testid="stHeader"]{background:rgba(8,13,26,.72)}.block-container{padding-top:1.5rem;padding-bottom:3rem;max-width:1600px}
h1,h2,h3{font-family:'Manrope',sans-serif!important;color:#f4f7ff!important;letter-spacing:-.5px}
p,label,[data-testid="stMarkdownContainer"]{color:#d5dff2}[data-testid="stCaptionContainer"],.stCaption{color:var(--muted)!important}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#10192d 0%,#0a1120 100%);border-right:1px solid #263653}[data-testid="stSidebar"] *{color:#e4ecfc}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2{color:var(--cyan)!important}
.brand{display:flex;align-items:center;gap:12px;padding:8px 0 22px;border-bottom:1px solid #2b3a51;margin-bottom:22px}
.brand-icon{background:linear-gradient(135deg,#38d9ff,#7c6cf4 58%,#46e6a5);border-radius:13px;padding:10px 14px;color:#07111f;font-size:20px;font-weight:900;box-shadow:0 8px 24px #38d9ff24}
.brand-name{font-family:Manrope,sans-serif;font-size:23px;font-weight:800;color:#fff;line-height:1.1}.brand-sub{font-size:10px;color:#9eacc2;letter-spacing:1.4px;margin-top:5px}
.eyebrow{color:var(--green);font-size:11px;letter-spacing:1.7px;font-weight:800}.page-title{font-family:Manrope,sans-serif;font-size:clamp(28px,3vw,38px);font-weight:800;letter-spacing:-1.2px;color:#f4f7ff;line-height:1.2}.page-sub{color:#aab9d2;font-size:14px;margin:6px 0 20px}
.section-title{font-family:Manrope,sans-serif;font-size:18px;font-weight:800;color:#f4f7ff}.section-sub{font-size:12px;color:#9caecc;margin-bottom:12px}
.metric-card{background:linear-gradient(145deg,rgba(23,35,59,.98),rgba(14,23,41,.98));border:1px solid #2a3b5d;border-radius:18px;padding:18px 19px;min-height:126px;box-shadow:0 12px 28px #0003;position:relative;overflow:hidden;transition:transform .18s ease,border-color .18s ease,box-shadow .18s ease}
.metric-card:hover{transform:translateY(-3px);border-color:var(--cyan);box-shadow:0 14px 35px #38d9ff1c}.metric-card:before{content:"";position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,var(--cyan),var(--violet),var(--green))}
.metric-label{font-size:11px;font-weight:700;letter-spacing:.8px;color:#a9b9d5}.metric-value{font-family:Manrope,sans-serif;font-size:clamp(23px,2.2vw,30px);font-weight:800;color:#f7faff;margin-top:12px;line-height:1.2}.metric-note{font-size:11px;color:#a2b2ce;margin-top:8px}
.insight{background:linear-gradient(145deg,#14213a,#101a2e);border:1px solid #293b5d;border-left:4px solid var(--cyan);border-radius:13px;padding:14px;margin-bottom:8px;min-height:88px}.insight.teal{border-left-color:var(--green)}.insight.amber{border-left-color:var(--amber)}
.insight-title{font-weight:800;font-size:13px;color:#f2f6ff;margin-bottom:5px}.insight-text{font-size:12px;line-height:1.5;color:#aebed7}
.note{background:linear-gradient(110deg,#112c42,#1b1c3a);border:1px solid #31516c;border-radius:12px;padding:12px 14px;color:#d8eaff;font-size:12px;line-height:1.5}
div[data-testid="stPlotlyChart"]{background:rgba(17,26,46,.78);border:1px solid #293b5d;border-radius:16px;padding:8px;box-shadow:0 10px 26px #0002}div[data-testid="stDataFrame"],div[data-testid="stTable"]{border:1px solid #293b5d;border-radius:12px;overflow:hidden}
div[data-testid="stMetric"]{background:#111a2e;border:1px solid #293b5d;border-radius:14px;padding:14px}div[data-testid="stMetricLabel"]{color:#a9b9d5!important}div[data-testid="stMetricValue"]{color:#f7faff!important}
div[data-baseweb="select"]>div,div[data-baseweb="input"]>div,[data-testid="stDateInput"] input{background:#111a2e!important;color:#f4f7ff!important;border-color:#304362!important;border-radius:10px!important}
.stButton>button,.stDownloadButton>button{background:linear-gradient(100deg,#38d9ff,#8b7cf6);color:#07111f!important;border:0;border-radius:10px;font-weight:800;transition:.18s ease}.stButton>button:hover,.stDownloadButton>button:hover{transform:translateY(-2px);box-shadow:0 8px 24px #38d9ff2e}
hr{border-color:#293b5d!important}a{color:var(--cyan)!important}[data-testid="stTabs"] button{color:#aebfda!important}[data-testid="stTabs"] button[aria-selected="true"]{color:var(--cyan)!important;border-bottom-color:var(--cyan)!important}
@media(max-width:700px){.block-container{padding-left:1rem;padding-right:1rem}.page-title{font-size:28px}}
</style>
""", unsafe_allow_html=True)

PLOT_COLORS = ["#38D9FF", "#A78BFA", "#46E6A5", "#FFB86B", "#FF6B9A", "#6EA8FE"]
px.defaults.template = "plotly_dark"
px.defaults.color_discrete_sequence = PLOT_COLORS


@st.cache_data(show_spinner="Loading order data…")
def load_data():
    if not DATA_FILE.exists():
        return pd.DataFrame()
    data = pd.read_parquet(DATA_FILE)
    required = {"order_id","purchase_timestamp","order_status","item_sales","freight_charged"}
    missing = sorted(required - set(data.columns))
    if missing:
        raise ValueError("Processed order summary missing columns: " + ", ".join(missing))
    data["purchase_timestamp"] = pd.to_datetime(data["purchase_timestamp"], errors="coerce")
    for col in ("item_sales","freight_charged"):
        data[col] = pd.to_numeric(data[col], errors="coerce").fillna(0)
    data["order_status"] = data["order_status"].fillna("unknown").astype(str)
    return data.dropna(subset=["purchase_timestamp"]).copy()

@st.cache_data
def load_csv(path_string):
    path = Path(path_string)
    return pd.read_csv(path) if path.exists() else pd.DataFrame()

def brl(value):
    value = float(value or 0)
    if abs(value) >= 1_000_000: return f"R${value/1_000_000:.2f}M"
    if abs(value) >= 1_000: return f"R${value/1_000:.1f}K"
    return f"R${value:,.2f}"

def heading(title, subtitle=None):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="section-sub">{subtitle}</div>', unsafe_allow_html=True)

def metric(label, value, note):
    st.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-note">{note}</div></div>', unsafe_allow_html=True)

def style(fig, height=340):
    fig.update_layout(height=height,paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, sans-serif",color="#D5DFF2",size=11),
        margin=dict(l=12,r=12,t=38,b=12),
        legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="left",x=0,title_text=""),
        hoverlabel=dict(bgcolor="#152238",font_color="#fff"))
    fig.update_xaxes(showgrid=False,linecolor="#344765",zeroline=False)
    fig.update_yaxes(gridcolor="#263653",zeroline=False)
    return fig

df = load_data()
categories = load_csv(str(CATEGORY_FILE))
if df.empty:
    st.error("No processed order data found. Confirm data/processed/order_business_summary.parquet exists.")
    st.stop()

with st.sidebar:
    st.markdown('<div class="brand"><div class="brand-icon">P</div><div><div class="brand-name">ProfitOS</div><div class="brand-sub">BUSINESS INTELLIGENCE</div></div></div>', unsafe_allow_html=True)
    st.markdown("### Workspace")
    page = st.radio("Navigate",["Executive overview","Sales analysis","Drill-down analytics","Sales target tracker","Forecasting","Scenario planner","Order explorer","Executive report","Data quality & methodology"],label_visibility="collapsed")
    st.markdown("---")
    st.markdown("### Data filters")
    min_date, max_date = df["purchase_timestamp"].min().date(), df["purchase_timestamp"].max().date()
    date_range = st.date_input("Purchase date range",value=(min_date,max_date),min_value=min_date,max_value=max_date,key="filter_dates")
    statuses = sorted(df["order_status"].dropna().unique().tolist())
    selected_statuses = st.multiselect("Order status",statuses,default=statuses,key="filter_status")
    def reset_filters():
        st.session_state["filter_dates"] = (min_date, max_date)
        st.session_state["filter_status"] = statuses

    st.button("Reset filters", use_container_width=True, on_click=reset_filters)
    st.markdown("---")
    st.caption("Source: Olist Brazilian e-commerce")
    st.caption(f"Available data: {min_date:%d %b %Y} – {max_date:%d %b %Y}")

filtered = df.copy()
if isinstance(date_range,(tuple,list)) and len(date_range)==2:
    start_date,end_date=date_range
    filtered=filtered[filtered["purchase_timestamp"].dt.date.between(start_date,end_date)].copy()
elif isinstance(date_range,(tuple,list)) and len(date_range)==1:
    start_date=end_date=date_range[0]
    filtered=filtered[filtered["purchase_timestamp"].dt.date==start_date].copy()
else:
    start_date,end_date=min_date,max_date
filtered=filtered[filtered["order_status"].isin(selected_statuses)].copy()
if filtered.empty:
    st.markdown('<div class="page-title">No matching orders</div>',unsafe_allow_html=True)
    st.info("Change the date range or selected statuses.")
    st.stop()

orders=int(filtered["order_id"].nunique())
delivered=int(filtered.loc[filtered["order_status"].eq("delivered"),"order_id"].nunique())
sales=float(filtered["item_sales"].sum())
freight=float(filtered["freight_charged"].sum())
delivery_rate=delivered/orders*100 if orders else 0
aov=sales/orders if orders else 0
monthly=(filtered.assign(month=filtered["purchase_timestamp"].dt.to_period("M").dt.to_timestamp())
    .groupby("month",as_index=False).agg(orders=("order_id","nunique"),item_sales=("item_sales","sum"),freight=("freight_charged","sum")).sort_values("month"))

monthly["is_sparse"]=monthly["orders"]<100

# Comparable previous-period window, matched to the selected date-range length.
period_days = max(1, (end_date - start_date).days + 1)
previous_end = pd.Timestamp(start_date) - pd.Timedelta(days=1)
previous_start = previous_end - pd.Timedelta(days=period_days - 1)
previous = df[
    df["purchase_timestamp"].dt.date.between(previous_start.date(), previous_end.date())
    & df["order_status"].isin(selected_statuses)
].copy()
prev_orders = int(previous["order_id"].nunique())
prev_sales = float(previous["item_sales"].sum())
prev_freight = float(previous["freight_charged"].sum())

def pct_change(current, prior):
    if prior == 0:
        return None
    return (current - prior) / abs(prior) * 100

sales_change_pct = pct_change(sales, prev_sales)
orders_change_pct = pct_change(orders, prev_orders)

titles={
"Executive overview":("Executive overview","A clear view of sales performance, order health and business signals."),
"Sales analysis":("Sales analytics","Explore revenue patterns, order activity and category performance."),
"Drill-down analytics":("Interactive drill-down","Move from summary trends to month, status, and category-level detail."),
"Sales target tracker":("Sales target tracker","Compare selected-period performance against an editable target."),
"Forecasting":("Forecast center","Review historical forecast output, model diagnostics and data limitations."),
"Scenario planner":("Scenario planner","Model possible changes in order volume, average order value and assumed costs."),
"Order explorer":("Order explorer","Inspect and export the orders included by your current filters."),
"Executive report":("Executive report generator","Create a shareable executive summary from the current dashboard filters."),
"Data quality & methodology":("Data quality & methodology","Check source coverage, data quality signals, metric definitions, and project limitations.")}
title,subtitle=titles[page]
st.markdown('<div class="eyebrow">BUSINESS INTELLIGENCE WORKSPACE</div>',unsafe_allow_html=True)
st.markdown(f'<div class="page-title">{title}</div>',unsafe_allow_html=True)
st.markdown(f'<div class="page-sub">{subtitle}</div>',unsafe_allow_html=True)
st.markdown(f'<div class="note">Showing <b>{orders:,} distinct orders</b> from <b>{start_date:%d %b %Y}</b> to <b>{end_date:%d %b %Y}</b>. Values reflect recorded item sales, not profit.</div>',unsafe_allow_html=True)
st.write("")

if page=="Executive overview":
    cols=st.columns(4,gap="medium")
    for col,args in zip(cols,[("ITEM SALES",brl(sales),"Recorded product sales"),("TOTAL ORDERS",f"{orders:,}","Distinct orders in selection"),("AVERAGE ORDER VALUE",brl(aov),"Item sales ÷ orders"),("DELIVERED ORDER RATE",f"{delivery_rate:.1f}%","Delivered / selected orders")]):
        with col: metric(*args)
    st.write("")
    heading("Period comparison", "Current selection versus the immediately preceding window of equal length")
    pc1,pc2,pc3=st.columns(3,gap="medium")
    pc1.metric("Sales vs previous period", "N/A" if sales_change_pct is None else f"{sales_change_pct:+.1f}%", help=f"Previous window: {previous_start:%d %b %Y} – {previous_end:%d %b %Y}. A comparison is unavailable when the prior period has zero sales.")
    pc2.metric("Orders vs previous period", "N/A" if orders_change_pct is None else f"{orders_change_pct:+.1f}%", help=f"Previous window: {previous_start:%d %b %Y} – {previous_end:%d %b %Y}.")
    pc3.metric("Previous-window sales", brl(prev_sales), help=f"{prev_orders:,} distinct orders in the previous window.")
    st.write("")
    left,right=st.columns([1.6,1],gap="large")
    with left:
        heading("Sales performance","Monthly item sales across the selected period")
        fig=px.area(monthly,x="month",y="item_sales",markers=True,labels={"month":"Month","item_sales":"Item sales (R$)"})
        fig.update_traces(line=dict(color="#38D9FF",width=3),fillcolor="rgba(56,217,255,.12)",marker=dict(size=6,color="#38D9FF"))
        fig.update_layout(yaxis_tickprefix="R$",yaxis_tickformat=",.0f")
        st.plotly_chart(style(fig,355),use_container_width=True)
    with right:
        heading("Order health","Selected orders by status")
        status=(filtered.groupby("order_status",as_index=False)["order_id"].nunique().rename(columns={"order_id":"orders"}).sort_values("orders",ascending=False))
        fig=px.pie(status,names="order_status",values="orders",hole=.68,color_discrete_sequence=["#38D9FF","#46E6A5","#FFB86B","#A78BFA","#6EA8FE"])
        fig.update_traces(textposition="inside",textinfo="percent")
        st.plotly_chart(style(fig,355),use_container_width=True)
    st.write("")
    heading("Business signals","Evidence-based observations and suggested next actions")
    best_sales=monthly.loc[monthly["item_sales"].idxmax()]
    best_orders=monthly.loc[monthly["orders"].idxmax()]
    c1,c2,c3=st.columns(3,gap="medium")
    with c1: st.markdown(f'<div class="insight"><div class="insight-title">🏆 Peak sales month</div><div class="insight-text"><b>{best_sales["month"]:%B %Y}</b> recorded {brl(best_sales["item_sales"])} in item sales. <br><b>Next:</b> compare its category mix with weaker months.</div></div>',unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="insight teal"><div class="insight-title">📦 Peak order volume</div><div class="insight-text"><b>{best_orders["month"]:%B %Y}</b> recorded {int(best_orders["orders"]):,} distinct orders. <br><b>Next:</b> check whether average order value also rose.</div></div>',unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="insight amber"><div class="insight-title">🔎 Data review flags</div><div class="insight-text">{int(monthly["is_sparse"].sum())} selected month(s) have fewer than 100 orders. <br><b>Next:</b> validate source coverage before interpreting a drop as demand decline.</div></div>',unsafe_allow_html=True)
    if sales_change_pct is not None:
        if sales_change_pct < -5:
            st.warning(f"Action signal: item sales are down {abs(sales_change_pct):.1f}% versus the previous comparable period. Review category mix, order status, and data coverage before making commercial changes.")
        elif sales_change_pct > 5:
            st.success(f"Action signal: item sales are up {sales_change_pct:.1f}% versus the previous comparable period. Identify which categories and order statuses contributed most.")
        else:
            st.info(f"Action signal: item sales are broadly stable versus the previous comparable period ({sales_change_pct:+.1f}%). Investigate category-level changes for hidden shifts.")
    if not categories.empty and {"category","item_sales"}.issubset(categories.columns):
        top=categories.loc[categories["item_sales"].idxmax()]
        st.info(f"Leading category in the full dataset: **{top['category']}** with {brl(top['item_sales'])} recorded item sales. Category results use the full dataset, not the sidebar date/status filters.")

elif page=="Sales analysis":
    c1,c2,c3=st.columns(3)
    c1.metric("Item sales",brl(sales)); c2.metric("Distinct orders",f"{orders:,}"); c3.metric("Freight charged",brl(freight))
    left,right=st.columns(2,gap="large")
    with left:
        heading("Monthly item sales","Sparse months are highlighted for review")
        plot=monthly.copy(); plot["regular_sales"]=plot["item_sales"].where(~plot["is_sparse"])
        fig=px.line(plot,x="month",y="regular_sales",markers=True,labels={"month":"Month","regular_sales":"Item sales (R$)"})
        fig.update_traces(line=dict(color="#38D9FF",width=3),marker=dict(size=6))
        sparse=plot[plot["is_sparse"]]
        if not sparse.empty:
            fig.add_trace(go.Scatter(x=sparse["month"],y=sparse["item_sales"],mode="markers",name="Sparse month (review)",marker=dict(color="#f59e0b",size=10,symbol="diamond"),customdata=sparse[["orders"]],hovertemplate="%{x|%b %Y}<br>Sales: R$%{y:,.2f}<br>Orders: %{customdata[0]}<extra></extra>"))
        fig.update_layout(yaxis_tickprefix="R$",yaxis_tickformat=",.0f")
        st.plotly_chart(style(fig,360),use_container_width=True)
    with right:
        heading("Monthly order volume","Distinct orders per calendar month")
        plot=monthly.copy(); plot["period_type"]=plot["is_sparse"].map({True:"Sparse month (review)",False:"Regular month"})
        fig=px.bar(plot,x="month",y="orders",color="period_type",color_discrete_map={"Regular month":"#38D9FF","Sparse month (review)":"#f59e0b"},labels={"month":"Month","orders":"Orders","period_type":"Month type"})
        st.plotly_chart(style(fig,360),use_container_width=True)
    heading("Category performance","Top categories from the full-dataset category report")
    if not categories.empty and {"category","item_sales"}.issubset(categories.columns):
        top=categories.nlargest(10,"item_sales").sort_values("item_sales")
        fig=px.bar(top,x="item_sales",y="category",orientation="h",labels={"item_sales":"Item sales (R$)","category":"Category"},color="item_sales",color_continuous_scale=["#263653","#38D9FF"])
        fig.update_layout(coloraxis_showscale=False,xaxis_tickprefix="R$",xaxis_tickformat=",.0f")
        st.plotly_chart(style(fig,410),use_container_width=True)
        st.dataframe(top,use_container_width=True,hide_index=True)
    else: st.info("Category report unavailable or missing category/item_sales columns.")
    if monthly["is_sparse"].any():
        st.warning("Low-volume months remain in the dataset. Review the source before interpreting them as a real drop in demand.")
        sparse=monthly.loc[monthly["is_sparse"],["month","orders","item_sales"]].copy()
        sparse["month"]=sparse["month"].dt.strftime("%B %Y")
        st.dataframe(sparse,use_container_width=True,hide_index=True)

elif page=="Forecasting":
    st.warning("Historical forecast only: the available Olist dataset ends in October 2018. The forecast below follows August 2018 and is not a prediction for 2026. September and October 2018 contain unusually few recorded orders and require review.")
    metrics=load_csv(str(FORECAST_METRICS_FILE))
    if not metrics.empty:
        expected={"model","backtest_windows","average_MAE","average_RMSE","average_WAPE_percent"}
        if expected.issubset(metrics.columns):
            metrics["average_WAPE_percent"]=pd.to_numeric(metrics["average_WAPE_percent"],errors="coerce")
            metrics=metrics.sort_values("average_WAPE_percent",na_position="last")
            best=metrics.dropna(subset=["average_WAPE_percent"]).head(1)
            if not best.empty:
                row=best.iloc[0]; a,b,c=st.columns(3)
                a.metric("Best backtested model",str(row["model"])); b.metric("Average validation WAPE",f'{row["average_WAPE_percent"]:.2f}%'); c.metric("Validation windows",str(row["backtest_windows"]))
            heading("Model comparison","Historical rolling-origin validation, not a guarantee of future accuracy")
            st.dataframe(metrics.round({"average_MAE":2,"average_RMSE":2,"average_WAPE_percent":2}),use_container_width=True,hide_index=True)
        else: st.info("Metrics file does not contain the expected backtest columns.")
    else: st.info("Model metrics not found. Run python src/profitos/sales_forecast.py.")
    forecast=load_csv(str(FORECAST_FILE))
    if not forecast.empty and {"forecast_month","forecast_item_sales"}.issubset(forecast.columns):
        forecast["forecast_month"]=pd.to_datetime(forecast["forecast_month"],errors="coerce")
        forecast["forecast_item_sales"]=pd.to_numeric(forecast["forecast_item_sales"],errors="coerce")
        forecast=forecast.dropna(subset=["forecast_month","forecast_item_sales"])
        historical=df.assign(month=df["purchase_timestamp"].dt.to_period("M").dt.to_timestamp()).groupby("month",as_index=False)["item_sales"].sum()
        historical=historical[historical["month"]<=pd.Timestamp("2018-08-01")].rename(columns={"month":"forecast_month","item_sales":"sales_value"})
        historical["series"]="Historical item sales"
        pred=forecast.rename(columns={"forecast_item_sales":"sales_value"}).copy(); pred["series"]="Historical forecast (2018)"
        plot=pd.concat([historical[["forecast_month","sales_value","series"]],pred[["forecast_month","sales_value","series"]]],ignore_index=True)
        heading("Historical forecast vs actuals","The historical forecast is retained for transparency and model evaluation")
        fig=px.line(plot,x="forecast_month",y="sales_value",color="series",markers=True,labels={"forecast_month":"Month","sales_value":"Item sales (R$)","series":"Series"})
        fig.update_layout(yaxis_tickprefix="R$",yaxis_tickformat=",.0f")
        st.plotly_chart(style(fig,390),use_container_width=True)
        st.dataframe(forecast,use_container_width=True,hide_index=True)
        st.download_button("Download forecast report (CSV)",forecast.to_csv(index=False).encode("utf-8"),"profitos_historical_forecast.csv","text/csv")
        heading("Forecast intelligence", "Decision guidance based on backtest results and the observed source coverage.")
        sparse_recent = monthly.loc[monthly["is_sparse"], ["month","orders","item_sales"]].copy()
        if not sparse_recent.empty:
            st.warning(f"{len(sparse_recent)} month(s) in the selected period have fewer than 100 orders. Sparse months can make a forecast look unusually low or unstable.")
            sparse_recent["month"] = sparse_recent["month"].dt.strftime("%B %Y")
            st.dataframe(sparse_recent, use_container_width=True, hide_index=True)
        if not metrics.empty and {"model","average_WAPE_percent"}.issubset(metrics.columns):
            valid_models = metrics.dropna(subset=["average_WAPE_percent"]).sort_values("average_WAPE_percent")
            if len(valid_models):
                best_model = valid_models.iloc[0]
                st.info(f"Model selection signal: **{best_model['model']}** has the lowest average WAPE among the loaded backtested models ({float(best_model['average_WAPE_percent']):.2f}%). This is a historical comparison, not a guarantee of future performance.")
                if float(best_model["average_WAPE_percent"]) > 20:
                    st.warning("The best available backtest error is above 20%; use the forecast cautiously and investigate additional features or model approaches.")
        st.caption("Before operational use: retrain with current data, compare against a seasonal baseline, inspect residuals, and add prediction intervals validated on rolling holdout windows.")
    else: st.info("Forecast file is unavailable or missing expected columns.")
    st.markdown('<div class="note"><b>Interpretation:</b> Forecast values are item-sales estimates, not actual results or profit. Backtest metrics summarize past validation windows. Sparse recent months and the age of the source data limit current relevance.</div>',unsafe_allow_html=True)

elif page=="Scenario planner":
    st.markdown('<div class="note"><b>Important:</b> This is an illustrative scenario model. The source data does not include a complete cost ledger, so modeled contribution is not actual accounting profit.</div>',unsafe_allow_html=True)
    regular=monthly.loc[~monthly["is_sparse"]]
    if regular.empty: regular=monthly
    default_orders=max(1,int(round(regular["orders"].median())))
    default_sales=max(0.0,float(regular["item_sales"].median()))
    heading("Set your assumptions","Change the inputs to explore possible business outcomes")
    c1,c2=st.columns(2,gap="large")
    with c1:
        baseline_orders=st.number_input("Baseline monthly orders",1,10_000_000,default_orders,100,key="sim_orders")
        baseline_sales=st.number_input("Baseline monthly item sales (R$)",0.0,1_000_000_000_000.0,default_sales,25_000.0,key="sim_sales")
        order_growth=st.slider("Expected order growth (%)",-50,100,10,5,key="sim_growth")
    with c2:
        item_change=st.slider("Average item value change (%)",-30,50,5,5,key="sim_item_value")
        cost_rate=st.slider("Assumed variable cost rate (%)",0,100,60,5,key="sim_cost_rate")
        fixed_costs=st.number_input("Assumed fixed monthly costs (R$)",0.0,1_000_000_000_000.0,100_000.0,10_000.0,key="sim_fixed_costs")
    baseline_aov=baseline_sales/baseline_orders
    scenario_orders=baseline_orders*(1+order_growth/100)
    scenario_aov=baseline_aov*(1+item_change/100)
    scenario_sales=scenario_orders*scenario_aov
    base_var=baseline_sales*cost_rate/100; scen_var=scenario_sales*cost_rate/100
    base_contrib=baseline_sales-base_var-fixed_costs; scen_contrib=scenario_sales-scen_var-fixed_costs
    a,b,c=st.columns(3)
    a.metric("Scenario monthly sales",brl(scenario_sales),delta=f"{scenario_sales-baseline_sales:+,.2f} R$ vs baseline")
    b.metric("Scenario monthly orders",f"{scenario_orders:,.0f}",delta=f"{scenario_orders-baseline_orders:+,.0f} orders")
    c.metric("Modeled contribution",brl(scen_contrib),delta=f"{scen_contrib-base_contrib:+,.2f} R$ vs baseline")
    table=pd.DataFrame({"Metric":["Monthly orders","Average item sales per order (R$)","Monthly item sales (R$)","Assumed variable costs (R$)","Assumed fixed costs (R$)","Modeled operating contribution (R$)"],"Baseline":[baseline_orders,baseline_aov,baseline_sales,base_var,fixed_costs,base_contrib],"Scenario":[scenario_orders,scenario_aov,scenario_sales,scen_var,fixed_costs,scen_contrib]})
    table["Change"]=table["Scenario"]-table["Baseline"]
    heading("Baseline vs scenario","Review the effect of your assumptions")
    st.dataframe(table.round(2),use_container_width=True,hide_index=True)
    st.download_button("Download scenario comparison (CSV)",table.to_csv(index=False).encode("utf-8"),"profitos_scenario_comparison.csv","text/csv")

elif page=="Order explorer":
    heading("Filtered order data","Inspect and export orders included by the sidebar filters")
    cols=[c for c in ["order_id","purchase_timestamp","order_status","item_count","item_sales","freight_charged","total_payment_value"] if c in filtered.columns]
    display=filtered[cols].sort_values("purchase_timestamp",ascending=False)
    search=st.text_input("Search order ID",placeholder="Type an order ID to narrow the table")
    if search.strip() and "order_id" in display.columns:
        display=display[display["order_id"].astype(str).str.contains(search.strip(),case=False,na=False)]
    st.caption(f"{len(display):,} order row(s) displayed")
    st.dataframe(display,use_container_width=True,hide_index=True)
    st.download_button("Download filtered orders (CSV)",filtered.to_csv(index=False).encode("utf-8"),"profitos_filtered_orders.csv","text/csv")


elif page=="Data quality & methodology":
    heading("Source coverage","Basic checks calculated from the processed order summary")
    total_rows = len(df)
    invalid_sales = int(pd.to_numeric(df["item_sales"], errors="coerce").isna().sum())
    negative_sales = int((df["item_sales"] < 0).sum())
    duplicate_order_rows = int(df["order_id"].duplicated().sum())
    missing_order_ids = int(df["order_id"].isna().sum())
    missing_status = int(df["order_status"].isna().sum())
    coverage_start = df["purchase_timestamp"].min()
    coverage_end = df["purchase_timestamp"].max()
    q1,q2,q3,q4=st.columns(4,gap="medium")
    with q1: metric("PROCESSED ROWS", f"{total_rows:,}", "Rows in processed summary")
    with q2: metric("DISTINCT ORDERS", f"{df['order_id'].nunique():,}", "Unique order IDs")
    with q3: metric("DUPLICATE ORDER ROWS", f"{duplicate_order_rows:,}", "Review only; row grain may vary")
    with q4: metric("NEGATIVE ITEM SALES", f"{negative_sales:,}", "Check refunds/adjustments")
    st.write("")
    checks = pd.DataFrame([
        {"Check":"Missing order IDs","Result":missing_order_ids,"Interpretation":"Rows without an order identifier"},
        {"Check":"Missing purchase timestamps","Result":int(pd.to_datetime(df["purchase_timestamp"],errors="coerce").isna().sum()),"Interpretation":"Rows excluded during timestamp cleaning may not be visible here"},
        {"Check":"Missing order status","Result":missing_status,"Interpretation":"Unknown statuses are normalized during loading"},
        {"Check":"Non-numeric item sales","Result":invalid_sales,"Interpretation":"Numeric conversion failures in the loaded data"},
        {"Check":"Negative item sales","Result":negative_sales,"Interpretation":"May reflect refunds or adjustments; investigate before excluding"},
        {"Check":"Months with fewer than 100 orders","Result":int((df.assign(month=df["purchase_timestamp"].dt.to_period("M")).groupby("month")["order_id"].nunique()<100).sum()),"Interpretation":"Review signal, not proof of incomplete data"},
    ])
    heading("Quality checks","Flags indicate where to investigate; they do not automatically mean the data is wrong")
    st.dataframe(checks,use_container_width=True,hide_index=True)
    st.write("")
    heading("Automated quality monitor", "Rule-based checks run whenever the dashboard loads; warnings require human review.")
    quality_rows = []
    def add_quality(name, passed, detail, severity="Warning"):
        quality_rows.append({"Check": name, "Status": "PASS" if passed else severity.upper(), "Detail": detail})
    add_quality("Required columns", {"order_id","purchase_timestamp","order_status","item_sales","freight_charged"}.issubset(df.columns),
                "Core fields are available in the loaded processed summary.", "Error")
    add_quality("Unique order grain", duplicate_order_rows == 0,
                f"{duplicate_order_rows:,} duplicate order IDs in processed rows; verify expected row grain.")
    add_quality("Non-negative item sales", negative_sales == 0,
                f"{negative_sales:,} rows have negative item sales; may be legitimate adjustments.")
    add_quality("Valid timestamps in loaded rows", int(df["purchase_timestamp"].isna().sum()) == 0,
                f"{int(df['purchase_timestamp'].isna().sum()):,} missing timestamps remain after load; invalid timestamps are dropped during loading.")
    add_quality("Recent-period volume", not bool((monthly["is_sparse"]).any()),
                f"{int(monthly['is_sparse'].sum())} selected month(s) have fewer than 100 orders.")
    add_quality("Forecast files available", FORECAST_FILE.exists() and FORECAST_METRICS_FILE.exists(),
                "Forecast and backtest files are both present.")
    quality_df = pd.DataFrame(quality_rows)
    st.dataframe(quality_df, use_container_width=True, hide_index=True)
    failed_count = int(quality_df["Status"].ne("PASS").sum())
    if failed_count:
        st.warning(f"Quality monitor flagged {failed_count} check(s). Review the detail column; flags are not automatically proof of bad data.")
    else:
        st.success("All configured quality checks passed for the loaded selection.")
    st.download_button("Download automated quality monitor (CSV)", quality_df.to_csv(index=False).encode("utf-8"),
                       "profitos_automated_quality_monitor.csv", "text/csv")
    st.write("")
    heading("Metric definitions")
    st.markdown("""
    - **Item sales:** sum of recorded item-level sales in the processed dataset; not profit.
    - **Freight charged:** recorded freight amount; not necessarily the seller's shipping cost.
    - **Average order value:** item sales divided by distinct orders in the current selection.
    - **Delivered order rate:** distinct delivered orders divided by all distinct orders in the current selection.
    - **Period comparison:** selected period compared with the immediately preceding window of equal calendar-day length.
    - **Forecast error:** historical backtest metric; it does not guarantee future accuracy.
    """)
    st.write("")
    heading("Known limitations")
    st.markdown("""
    - Olist is a historical Brazilian e-commerce dataset, with coverage primarily from 2016–2018.
    - Sparse late-period records can distort trend and forecast interpretation.
    - The source does not provide a complete cost ledger, so this app does not calculate actual accounting profit.
    - Category performance uses the supplied full-dataset report unless explicitly filtered in a future version.
    - Rule-based recommendations are decision support, not causal proof; validate findings before taking action.
    """)
    st.download_button("Download data-quality checks (CSV)", checks.to_csv(index=False).encode("utf-8"), "profitos_data_quality_checks.csv", "text/csv")


elif page=="Drill-down analytics":
    heading("Choose a drill-down path", "All figures use the active sidebar date and order-status filters.")
    drill_tab = st.radio("Analysis dimension", ["Monthly trend", "Order status", "Category detail"], horizontal=True, key="drill_dimension")
    if drill_tab == "Monthly trend":
        detail = monthly.copy()
        detail["month_label"] = detail["month"].dt.strftime("%B %Y")
        detail["average_item_sales_per_order"] = detail["item_sales"] / detail["orders"].replace(0, pd.NA)
        fig = px.bar(detail, x="month_label", y="item_sales", color="is_sparse",
                     color_discrete_map={False:"#38D9FF", True:"#FFB86B"},
                     labels={"month_label":"Month","item_sales":"Item sales (R$)","is_sparse":"Fewer than 100 orders"})
        fig.update_layout(yaxis_tickprefix="R$", yaxis_tickformat=",.0f")
        st.plotly_chart(style(fig, 360), use_container_width=True)
        heading("Monthly detail table", "Use the table to identify changes worth investigating.")
        st.dataframe(detail[["month_label","orders","item_sales","freight","average_item_sales_per_order","is_sparse"]].round(2),
                     use_container_width=True, hide_index=True)
        st.download_button("Export monthly drill-down (CSV)", detail.to_csv(index=False).encode("utf-8"),
                           "profitos_monthly_drilldown.csv", "text/csv")
    elif drill_tab == "Order status":
        detail = filtered.groupby("order_status", as_index=False).agg(
            orders=("order_id","nunique"), item_sales=("item_sales","sum"), freight=("freight_charged","sum"))
        detail["sales_share_pct"] = detail["item_sales"] / detail["item_sales"].sum() * 100 if detail["item_sales"].sum() else 0
        detail = detail.sort_values("item_sales", ascending=False)
        fig = px.bar(detail, x="order_status", y="item_sales", color="order_status",
                     labels={"order_status":"Order status","item_sales":"Item sales (R$)"})
        fig.update_layout(yaxis_tickprefix="R$", yaxis_tickformat=",.0f", showlegend=False)
        st.plotly_chart(style(fig, 340), use_container_width=True)
        st.dataframe(detail.round(2), use_container_width=True, hide_index=True)
        st.download_button("Export status drill-down (CSV)", detail.to_csv(index=False).encode("utf-8"),
                           "profitos_status_drilldown.csv", "text/csv")
    else:
        if not categories.empty and {"category","item_sales"}.issubset(categories.columns):
            cat = categories.copy()
            cat["item_sales"] = pd.to_numeric(cat["item_sales"], errors="coerce").fillna(0)
            if "orders" in cat.columns:
                cat["orders"] = pd.to_numeric(cat["orders"], errors="coerce")
            selected_cat = st.selectbox("Select a category", ["All categories"] + sorted(cat["category"].dropna().astype(str).unique().tolist()))
            if selected_cat != "All categories":
                cat = cat[cat["category"].astype(str).eq(selected_cat)]
            cat = cat.sort_values("item_sales", ascending=False)
            st.caption("Category report is based on the supplied full-dataset category file and is not affected by the sidebar date/status filters.")
            st.dataframe(cat, use_container_width=True, hide_index=True)
            st.download_button("Export category drill-down (CSV)", cat.to_csv(index=False).encode("utf-8"),
                               "profitos_category_drilldown.csv", "text/csv")
        else:
            st.info("Category drill-down needs reports/category_performance.csv with category and item_sales columns.")

elif page=="Sales target tracker":
    st.markdown('<div class="note"><b>Target tracking:</b> targets are editable for this browser session. They are not written to a permanent database and may reset in a new session.</div>', unsafe_allow_html=True)
    heading("Set a sales target", "Use a monthly target to review the selected period. This is a planning input, not a source-data field.")
    default_target = max(1.0, float(sales))
    target = st.number_input("Item-sales target for the selected period (R$)", min_value=0.0,
                             max_value=1_000_000_000_000.0, value=default_target, step=10000.0, key="target_sales")
    attainment = (sales / target * 100) if target > 0 else None
    gap = sales - target
    c1,c2,c3 = st.columns(3, gap="medium")
    c1.metric("Actual recorded item sales", brl(sales))
    c2.metric("Target attainment", "N/A" if attainment is None else f"{attainment:.1f}%")
    c3.metric("Gap to target", brl(gap), delta="Above target" if gap >= 0 else "Below target", delta_color="normal" if gap >= 0 else "inverse")
    if target > 0:
        st.progress(min(1.0, max(0.0, sales / target)), text=f"{min(100.0, max(0.0, attainment)):.1f}% of target reached")
    if target == 0:
        st.info("Set a target greater than zero to calculate attainment.")
    elif sales >= target:
        st.success("The selected period is at or above the target. Review which months and statuses contributed most.")
    else:
        st.warning(f"The selected period is {brl(target - sales)} below target. Review month-level performance and data coverage before deciding on action.")
    target_monthly = monthly.copy()
    target_monthly["target_allocation"] = target / max(1, len(target_monthly))
    target_monthly["gap_to_allocated_target"] = target_monthly["item_sales"] - target_monthly["target_allocation"]
    target_monthly["attainment_pct"] = target_monthly["item_sales"] / target_monthly["target_allocation"].replace(0, pd.NA) * 100
    heading("Month-by-month pace", "The period target is evenly allocated across months for a simple pacing view.")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=target_monthly["month"], y=target_monthly["item_sales"], name="Recorded item sales", marker_color="#38D9FF"))
    fig.add_trace(go.Scatter(x=target_monthly["month"], y=target_monthly["target_allocation"], name="Allocated target", mode="lines+markers", line=dict(color="#FFB86B", width=3, dash="dash")))
    fig.update_layout(yaxis_tickprefix="R$", yaxis_tickformat=",.0f")
    st.plotly_chart(style(fig, 360), use_container_width=True)
    st.dataframe(target_monthly[["month","orders","item_sales","target_allocation","gap_to_allocated_target","attainment_pct"]].round(2),
                 use_container_width=True, hide_index=True)
    target_export = target_monthly.copy()
    target_export["target_for_selected_period"] = target
    st.download_button("Download target tracker (CSV)", target_export.to_csv(index=False).encode("utf-8"),
                       "profitos_sales_target_tracker.csv", "text/csv")

elif page=="Executive report":
    heading("Executive snapshot", "A concise report generated from the current filters and available historical data.")
    if sales_change_pct is None:
        trend_text = "No percentage comparison is available because the previous comparable period has zero recorded sales."
    elif sales_change_pct > 0:
        trend_text = f"Recorded item sales increased {sales_change_pct:.1f}% versus the previous equal-length period."
    elif sales_change_pct < 0:
        trend_text = f"Recorded item sales decreased {abs(sales_change_pct):.1f}% versus the previous equal-length period."
    else:
        trend_text = "Recorded item sales were unchanged versus the previous equal-length period."
    best_sales = monthly.loc[monthly["item_sales"].idxmax()]
    sparse_count = int(monthly["is_sparse"].sum())
    report_metrics = pd.DataFrame([
        {"Metric":"Selected-period item sales (R$)","Value":round(sales,2)},
        {"Metric":"Distinct orders","Value":orders},
        {"Metric":"Average order value (R$)","Value":round(aov,2)},
        {"Metric":"Delivered order rate (%)","Value":round(delivery_rate,2)},
        {"Metric":"Freight charged (R$)","Value":round(freight,2)},
        {"Metric":"Previous-period sales (R$)","Value":round(prev_sales,2)},
        {"Metric":"Sales change vs previous period (%)","Value":"N/A" if sales_change_pct is None else round(sales_change_pct,2)},
        {"Metric":"Months with fewer than 100 orders","Value":sparse_count},
    ])
    r1,r2,r3,r4=st.columns(4)
    r1.metric("Item sales", brl(sales)); r2.metric("Orders", f"{orders:,}")
    r3.metric("Average order value", brl(aov)); r4.metric("Sparse months", str(sparse_count))
    st.markdown(f"**Performance signal:** {trend_text}")
    st.markdown(f"**Peak month:** {best_sales['month']:%B %Y}, with {brl(best_sales['item_sales'])} in recorded item sales.")
    st.markdown("**Recommended review:** inspect category mix, order status, and sparse-month coverage before treating changes as shifts in demand.")
    st.markdown("**Methodology note:** this dataset is historical Olist Brazilian e-commerce data, primarily from 2016–2018. Item sales are not profit; scenario contribution is based on assumptions.")
    heading("Report data")
    st.dataframe(report_metrics, use_container_width=True, hide_index=True)
    st.download_button("Download executive KPI report (CSV)", report_metrics.to_csv(index=False).encode("utf-8"),
                       "profitos_executive_report.csv", "text/csv")
    html_report = f"""<!doctype html><html><head><meta charset="utf-8"><title>ProfitOS Executive Report</title>
    <style>body{{font-family:Arial,sans-serif;max-width:900px;margin:40px auto;padding:0 24px;color:#172033}}
    h1{{color:#10213d}}.sub{{color:#596579}}table{{border-collapse:collapse;width:100%;margin:20px 0}}
    td,th{{border:1px solid #d9e1ee;padding:10px;text-align:left}}th{{background:#edf3fb}}
    .note{{background:#f2f7ff;padding:14px;border-left:4px solid #168fbb}}</style></head><body>
    <h1>ProfitOS — Executive Report</h1><p class="sub">Generated from selected filters: {start_date} to {end_date}</p>
    <div class="note"><b>Performance signal:</b> {trend_text}<br><b>Peak month:</b> {best_sales['month']:%B %Y} ({brl(best_sales['item_sales'])}).</div>
    {report_metrics.to_html(index=False, escape=True)}
    <h2>Suggested next steps</h2><ul><li>Review category mix and order status for meaningful changes.</li>
    <li>Investigate sparse months before interpreting trends.</li><li>Do not interpret item sales as profit.</li></ul>
    <p><b>Limitations:</b> historical Olist data primarily from 2016–2018; forecast estimates are historical and are not a 2026 forecast.</p>
    </body></html>"""
    st.download_button("Download shareable executive report (HTML)", html_report.encode("utf-8"),
                       "profitos_executive_report.html", "text/html")


st.markdown("---")
l,r=st.columns([3,1])
with l: st.caption("ProfitOS · Decision intelligence portfolio · Historical Olist e-commerce data")
with r: st.caption("Item sales are not profit")
