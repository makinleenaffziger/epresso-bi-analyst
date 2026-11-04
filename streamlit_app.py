"""E-Presso business dashboard. Original data and assistant modules stay in place."""
from pathlib import Path
import math

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="E-Presso | Revenue dashboard", page_icon="☕", layout="wide")
st.markdown("""
<style>
.stApp {background-color: #FFF7FA;}
[data-testid="stMainBlockContainer"] {max-width: 1440px; padding-top: 2rem; padding-bottom: 3rem;}
[data-testid="stSidebar"] {background-color: #FBE6EE;}
h1, h2, h3 {color: #682B48; letter-spacing: -0.025em;}
[data-testid="stMetric"] {background: #FFFFFF; border: 1px solid #EFD4DF; border-radius: 14px; padding: 18px 20px; height: 100%;}
[data-testid="stMetricLabel"] {color: #795665;}
[data-testid="stMetricValue"] {color: #682B48; font-size: clamp(1.35rem, 2.1vw, 2rem);}
[data-baseweb="tab-list"] {gap: 22px; border-bottom: 1px solid #EFD4DF; margin-bottom: 12px;}
[data-baseweb="tab"] {font-weight: 600;}
[data-baseweb="tab"][aria-selected="true"] {color: #A9366B;}
[data-baseweb="tab-highlight"] {background-color: #A9366B;}
[data-testid="stPlotlyChart"] {background: #FFFFFF; border: 1px solid #EFD4DF; border-radius: 14px; padding: 10px;}
[data-testid="stExpander"] {background: #FFFFFF; border-color: #EFD4DF; border-radius: 10px;}
[data-testid="stCaptionContainer"] {color: #795665;}
@media (prefers-color-scheme: dark) {
 .stApp {background-color: #22151E;}
 [data-testid="stSidebar"] {background-color: #321E2B;}
 h1, h2, h3 {color: #FBE5EF;}
 [data-testid="stMetric"], [data-testid="stExpander"] {background: #382331; border-color: #684454;}
 [data-testid="stMetricLabel"], [data-testid="stCaptionContainer"] {color: #E5C1D1;}
 [data-testid="stMetricValue"] {color: #FBE5EF;}
 [data-baseweb="tab"][aria-selected="true"] {color: #F3A3C7;}
}
</style>
""", unsafe_allow_html=True)

DATA_DIR = Path(__file__).resolve().parent / "data"
ROSE = "#A9366B"
BLUSH = "#D987AA"
PALETTE = [ROSE, BLUSH, "#BD6D95", "#AD8DA1", "#C99BAA"]


def require_columns(data, required, name):
    missing = sorted(set(required) - set(data.columns))
    if missing:
        st.error(f"{name} is missing these columns: {', '.join(missing)}")
        st.stop()


def read_source(upload, filename, name, kind="csv", **kwargs):
    source = upload if upload is not None else DATA_DIR / filename
    if upload is None and not source.is_file():
        st.error(f"Original {name} file is missing: data/{filename}. Add it to the data folder or upload a replacement in the sidebar.")
        st.stop()
    try:
        if kind == "excel":
            return pd.read_excel(source, **kwargs)
        return pd.read_csv(source, **kwargs)
    except (ValueError, OSError, ImportError, pd.errors.ParserError) as error:
        st.error(f"The {name} file could not be read. Check its format, column headings, and expected worksheet.")
        st.stop()


def chart_style(fig, height=340):
    fig.update_layout(
        template="plotly_white", height=height,
        margin=dict(l=16, r=20, t=24, b=24),
        font=dict(family="Arial, sans-serif", size=12, color="#735061"),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
    )
    fig.update_xaxes(showgrid=False, zeroline=False, title_font_size=12)
    fig.update_yaxes(gridcolor="#F0E1E8", zeroline=False, title_font_size=12)
    return fig


def show_profile(table, label, key):
    with st.expander(f"{label} · {len(table):,} records"):
        a, b, c = st.columns(3)
        a.metric("Records", f"{len(table):,}")
        b.metric("Duplicate IDs", f"{int(table[key].duplicated().sum()):,}")
        c.metric("Missing cells", f"{int(table.isna().sum().sum()):,}")
        st.dataframe(table, hide_index=True, use_container_width=True)
        st.caption("Missing values by column")
        st.dataframe(table.isna().sum().rename("Missing values"), use_container_width=True)


with st.sidebar:
    st.title("E-Presso")
    st.caption("REVENUE WORKSPACE")
    st.divider()
    filter_area = st.container()
    st.divider()
    with st.expander("Manage data", expanded=False):
        st.caption("Original data loads automatically. Upload a file to replace one table for this session. Remove the upload to restore the original.")
        stores_upload = st.file_uploader("Stores CSV", type=["csv"], key="stores_upload")
        survey_upload = st.file_uploader("Survey workbook", type=["xlsx"], key="survey_upload")
        sales_upload = st.file_uploader("Sales CSV", type=["csv"], key="sales_upload")
        products_upload = st.file_uploader("Products CSV", type=["csv"], key="products_upload")
        categories_upload = st.file_uploader("Categories CSV", type=["csv"], key="categories_upload")

stores = read_source(stores_upload, "Stores.csv", "Stores", skiprows=1, dtype=str)
survey = read_source(survey_upload, "Survey.xlsx", "Survey Results", kind="excel", sheet_name="Survey Results", skiprows=2)
sales = read_source(sales_upload, "Sales.csv", "Sales")
products = read_source(products_upload, "Products.csv", "Products", dtype=str)
categories = read_source(categories_upload, "Categories.csv", "Categories", dtype=str)
for table, required, label in [
    (stores, ["ID", "StoreType"], "Stores"),
    (survey, ["Survey ID"], "Survey Results"),
    (sales, ["Sales ID", "Store ID", "Product ID", "Category ID", "Date", "Revenue"], "Sales"),
    (products, ["Product ID", "Product"], "Products"),
    (categories, ["Category ID", "Category"], "Categories"),
]:
    require_columns(table, required, label)

sales["Revenue"] = pd.to_numeric(sales["Revenue"], errors="coerce")
bad_revenue = ~sales["Revenue"].map(lambda value: pd.notna(value) and math.isfinite(value))
if bad_revenue.any():
    st.error(f"{int(bad_revenue.sum())} sales rows have missing or unreadable revenue. Correct the Sales file before using the dashboard.")
    st.stop()
for label, table, key in [("Stores", stores, "ID"), ("Products", products, "Product ID"), ("Categories", categories, "Category ID")]:
    if table[key].isna().any() or table[key].astype(str).str.strip().eq("").any() or table[key].duplicated().any():
        st.error(f"{label} must have a unique, nonblank {key} for every row.")
        st.stop()

combined = sales.copy()
merge_records = []
for label, lookup, left_key, right_key in [
    ("Stores", stores[["ID", "StoreType"]], "Store ID", "ID"),
    ("Products", products[["Product ID", "Product"]], "Product ID", "Product ID"),
    ("Categories", categories[["Category ID", "Category"]], "Category ID", "Category ID"),
]:
    before_rows, before_revenue = len(combined), combined["Revenue"].sum()
    combined = combined.merge(lookup, left_on=left_key, right_on=right_key, how="left", validate="many_to_one", indicator=True)
    merge_records.append({"Connection": label, "Rows before": before_rows, "Rows after": len(combined), "Revenue before": before_revenue, "Revenue after": combined["Revenue"].sum(), "Unmatched sales": int(combined["_merge"].eq("left_only").sum())})
    combined = combined.drop(columns="_merge")
merge_report = pd.DataFrame(merge_records)
combined["StoreType"] = combined["StoreType"].fillna("Unknown store type")
combined["Category"] = combined["Category"].fillna("Unknown category")
combined["Product"] = combined["Product"].fillna("Unknown product")
combined["Date"] = pd.to_datetime(combined["Date"], errors="coerce")
combined["Year"] = combined["Date"].dt.year
invalid_dates = int(combined["Date"].isna().sum())

with filter_area:
    st.subheader("Filter revenue")
    selected_year = st.selectbox("Year", ["All years"] + sorted(combined["Year"].dropna().astype(int).unique().tolist()))
    selected_channel = st.selectbox("Store type", ["All store types"] + sorted(combined["StoreType"].unique().tolist()))
    selected_category = st.selectbox("Category", ["All categories"] + sorted(combined["Category"].unique().tolist()))
    st.caption("Applies to the overview and assistant. Data checks use all loaded rows.")

year = None if selected_year == "All years" else int(selected_year)
channel = None if selected_channel == "All store types" else selected_channel
category = None if selected_category == "All categories" else selected_category
filtered = combined.copy()
for col, value in [("Year", year), ("StoreType", channel), ("Category", category)]:
    if value is not None:
        filtered = filtered[filtered[col] == value]

st.caption("E-PRESSO / BUSINESS INTELLIGENCE")
st.title("Revenue dashboard")
st.write("Track sales performance across channels, years, and product categories.")
source_count = sum(u is not None for u in [stores_upload, survey_upload, sales_upload, products_upload, categories_upload])
st.caption(f"{'Original data' if not source_count else f'Original data + {source_count} uploaded replacement(s)'}  ·  {len(sales):,} sales records loaded")
st.caption(f"Selected scope: {selected_year} · {selected_channel} · {selected_category}")
if merge_report["Unmatched sales"].sum():
    st.warning("Some sales have no matching lookup record. They remain included under Unknown labels. See Data quality for details.")
if invalid_dates:
    st.warning(f"{invalid_dates:,} rows have missing or unreadable dates. They remain in All years totals but are excluded from date-based charts and individual year selections.")

metrics = st.columns(4)
metrics[0].metric("Selected revenue", f"${filtered['Revenue'].sum():,.2f}")
metrics[1].metric("Website revenue", f"${filtered.loc[filtered['StoreType'].eq('Website'), 'Revenue'].sum():,.2f}")
metrics[2].metric("Brick & Mortar revenue", f"${filtered.loc[filtered['StoreType'].eq('Brick & Mortar'), 'Revenue'].sum():,.2f}")
metrics[3].metric("Sales records", f"{len(filtered):,}")
st.caption("All metrics use the selected filters. Revenue is not profit.")

overview, assistant, quality = st.tabs(["Revenue overview", "Analytical assistant", "Data quality"])
with overview:
    if filtered.empty:
        st.info("No sales match these filters. Choose another combination.")
    else:
        channels_df = filtered.groupby("StoreType", as_index=False)["Revenue"].sum()
        dated = filtered.dropna(subset=["Date"]).copy()
        annual = dated.groupby("Year", as_index=False)["Revenue"].sum().sort_values("Year")
        if not annual.empty:
            annual["Year"] = annual["Year"].astype(int)
        left, right = st.columns([1.6, 1], gap="large")
        with left:
            st.subheader("Revenue over time")
            st.caption("Calendar-year totals within the selected scope.")
            if annual.empty:
                st.info("No readable dates are available for annual revenue.")
            else:
                fig = px.line(annual, x="Year", y="Revenue", markers=True, labels={"Revenue": "Revenue (USD)"})
                fig.update_traces(line_color=ROSE, line_width=3, marker_size=8, hovertemplate="Year %{x}<br>$%{y:,.2f}<extra></extra>")
                fig.update_xaxes(dtick=1, tickformat="d")
                fig.update_yaxes(tickprefix="$", tickformat="~s", rangemode="tozero")
                st.plotly_chart(chart_style(fig), use_container_width=True, config={"displaylogo": False})
        with right:
            st.subheader("Revenue by store type")
            st.caption("Compare channels within the same filters.")
            fig = px.bar(channels_df, x="StoreType", y="Revenue", color="StoreType", color_discrete_map={"Website": ROSE, "Brick & Mortar": BLUSH}, labels={"StoreType": "Store type", "Revenue": "Revenue (USD)"})
            fig.update_traces(hovertemplate="%{x}<br>$%{y:,.2f}<extra></extra>")
            fig.update_yaxes(tickprefix="$", tickformat="~s", rangemode="tozero")
            st.plotly_chart(chart_style(fig), use_container_width=True, config={"displaylogo": False})
        st.divider()
        st.subheader("Monthly revenue pattern")
        st.caption("Monthly shares combine the selected years; they are not averages of annual percentages.")
        monthly = pd.DataFrame(columns=["Month", "Revenue", "Revenue share"])
        denominator = dated["Revenue"].sum()
        if dated.empty:
            st.info("No readable dates are available for monthly revenue.")
        elif denominator == 0:
            st.info("Monthly shares cannot be calculated when selected dated revenue is zero.")
        else:
            dated["Month number"] = dated["Date"].dt.month
            monthly = dated.groupby("Month number", as_index=False)["Revenue"].sum().sort_values("Month number")
            monthly["Month"] = pd.to_datetime(monthly["Month number"].astype(str), format="%m").dt.month_name()
            monthly["Revenue share"] = monthly["Revenue"] / denominator
            fig = px.bar(monthly, x="Month", y="Revenue share", custom_data=["Revenue"], category_orders={"Month": monthly["Month"].tolist()}, labels={"Revenue share": "Share of selected dated revenue"})
            fig.update_traces(marker_color=[BLUSH if v == monthly['Revenue'].max() else ROSE for v in monthly['Revenue']], hovertemplate="%{x}<br>Revenue: $%{customdata[0]:,.2f}<br>Share: %{y:.2%}<extra></extra>")
            fig.update_yaxes(tickformat=".0%")
            fig.update_xaxes(tickangle=0)
            st.plotly_chart(chart_style(fig, 310), use_container_width=True, config={"displaylogo": False})
        with st.expander("View exact figures and download tables"):
            st.caption("Store type")
            st.dataframe(channels_df.style.format({"Revenue": "${:,.2f}"}), hide_index=True, use_container_width=True)
            st.caption("Year")
            st.dataframe(annual.style.format({"Year": "{:.0f}", "Revenue": "${:,.2f}"}), hide_index=True, use_container_width=True)
            if not monthly.empty:
                st.caption("Month")
                st.dataframe(monthly[["Month", "Revenue", "Revenue share"]].style.format({"Revenue": "${:,.2f}", "Revenue share": "{:.2%}"}), hide_index=True, use_container_width=True)
            st.download_button("Download selected sales", filtered.to_csv(index=False).encode("utf-8"), file_name="epresso_selected_sales.csv", mime="text/csv")

with assistant:
    from assistant_ui import show_assistant
    show_assistant(combined, year=year, channel=channel, category=category)

with quality:
    st.subheader("Data quality and connections")
    st.caption("Checks describe the full loaded data, before dashboard filters.")
    st.write("All loaded sales revenue:", f"${sales['Revenue'].sum():,.2f}")
    st.write("Sales with missing or unreadable dates:", invalid_dates)
    st.dataframe(merge_report.style.format({"Revenue before": "${:,.2f}", "Revenue after": "${:,.2f}"}), hide_index=True, use_container_width=True)
    with st.expander("What each row represents"):
        grain = pd.DataFrame([
            ["Stores", "One store or the website channel", "ID"],
            ["Survey Results", "One store's survey results for one year", "Survey ID"],
            ["Sales", "One product at one store/channel for one month", "Sales ID"],
            ["Products", "One product", "Product ID"],
            ["Categories", "One product category", "Category ID"],
        ], columns=["Table", "One row represents", "Key"])
        st.dataframe(grain, hide_index=True, use_container_width=True)
        st.write("Sales joins Stores, Products, and Categories by their IDs. Survey Results is profiled separately and is not joined to Sales. Missing survey responses remain blank, not zero.")
    for table, label, key in [(stores, "Stores", "ID"), (survey, "Survey Results", "Survey ID"), (sales, "Sales", "Sales ID"), (products, "Products", "Product ID"), (categories, "Categories", "Category ID")]:
        show_profile(table, label, key)
    with st.expander("Data sources"):
        st.dataframe(pd.DataFrame([
            {"Table": label, "Source": u.name if u is not None else f"Original: data/{filename}"}
            for label, u, filename in [("Stores", stores_upload, "Stores.csv"), ("Survey Results", survey_upload, "Survey.xlsx"), ("Sales", sales_upload, "Sales.csv"), ("Products", products_upload, "Products.csv"), ("Categories", categories_upload, "Categories.csv")]
        ]), hide_index=True, use_container_width=True)

st.divider()
st.caption("E-Presso · Revenue analysis | Results reflect the loaded data and selected scope. Costs and expenses are required to assess profit.")
