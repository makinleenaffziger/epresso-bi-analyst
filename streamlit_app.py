import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Welcome to E-Presso!")
st.write("Explore revenue and check the uploaded data.")

st.subheader("What each row represents")
grain = pd.DataFrame([
    ["Stores", "One store or the website sales channel.", "ID", "No"],
    ["Survey Results", "Survey results for one store in one year.", "Survey ID", "No"],
    ["Sales", "One product's revenue at one store or the website for one month.", "Sales ID", "Yes"],
    ["Products", "One product identified by its Product ID.", "Product ID", "No"],
    ["Categories", "One product category.", "Category ID", "No"]
], columns=["Table", "One row represents", "Key", "Contains revenue?"])
st.dataframe(grain, hide_index=True)


def show_profile(data, name, key):
    st.dataframe(data)
    st.write(f"Number of {name} records:", len(data))
    st.write(f"Duplicate {name} IDs:", data[key].duplicated().sum())
    st.write("Missing values by column:")
    st.dataframe(data.isna().sum().rename("Missing values"))


st.subheader("Upload store data")
stores_file = st.file_uploader("Choose your Stores CSV file", type=["csv"])
if stores_file is not None:
    stores = pd.read_csv(stores_file, skiprows=1, dtype=str)
    show_profile(stores, "store", "ID")

st.subheader("Upload survey data")
survey_file = st.file_uploader("Choose your Survey Excel file", type=["xlsx"])
if survey_file is not None:
    survey = pd.read_excel(
        survey_file, sheet_name="Survey Results", skiprows=2
    )
    show_profile(survey, "survey", "Survey ID")

st.subheader("Upload sales data")
sales_file = st.file_uploader("Choose your Sales CSV file", type=["csv"])
if sales_file is not None:
    sales = pd.read_csv(sales_file)
    show_profile(sales, "sales", "Sales ID")
    sales["Revenue"] = pd.to_numeric(sales["Revenue"], errors="coerce")
    bad_revenue = sales["Revenue"].isna().sum()
    if bad_revenue > 0:
        st.error(
            f"{bad_revenue} sales rows have missing or unreadable revenue. "
            "Correct the file before using the dashboard."
        )
        st.stop()
    st.metric(
        "Total revenue — all uploaded sales",
        f"${sales['Revenue'].sum():,.2f}"
    )

st.subheader("Upload product data")
products_file = st.file_uploader("Choose your Products CSV file", type=["csv"])
if products_file is not None:
    products = pd.read_csv(products_file, dtype=str)
    show_profile(products, "product", "Product ID")

st.subheader("Upload category data")
categories_file = st.file_uploader("Choose your Categories CSV file", type=["csv"])
if categories_file is not None:
    categories = pd.read_csv(categories_file, dtype=str)
    show_profile(categories, "category", "Category ID")

st.subheader("Connect Sales to Stores")

if stores_file is None or sales_file is None:
    st.info("Upload both Stores and Sales to use the dashboard.")
    st.stop()

if stores["ID"].isna().any() or stores["ID"].duplicated().any():
    st.error("Stores must have a unique, nonblank ID for every row.")
    st.stop()

combined = sales.merge(
    stores,
    left_on="Store ID",
    right_on="ID",
    how="left",
    validate="many_to_one",
    indicator=True
)

merge_check = pd.DataFrame({
    "Check": ["Sales rows", "Total revenue"],
    "Before connection": [
        f"{len(sales):,}",
        f"${sales['Revenue'].sum():,.2f}"
    ],
    "After connection": [
        f"{len(combined):,}",
        f"${combined['Revenue'].sum():,.2f}"
    ]
})
st.dataframe(merge_check, hide_index=True)

unmatched = (combined["_merge"] == "left_only").sum()
st.write("Sales records without a matching store:", unmatched)
if unmatched > 0:
    st.warning("Some sales have no matching store. Check the store IDs.")

combined["StoreType"] = combined["StoreType"].fillna("Unknown store type")
combined["Date"] = pd.to_datetime(combined["Date"], errors="coerce")
combined["Year"] = combined["Date"].dt.year

invalid_dates = combined["Date"].isna().sum()
st.write("Sales records with missing or unreadable dates:", invalid_dates)
if invalid_dates > 0:
    st.warning(
        "Undated rows are included when All years is selected, but excluded "
        "from yearly and monthly charts and individual year selections."
    )

st.subheader("Dashboard filters")
st.caption("These filters affect the dashboard below. Data profiles above use all rows.")

years = sorted(combined["Year"].dropna().astype(int).unique().tolist())
channels = sorted(combined["StoreType"].unique().tolist())

selected_year = st.selectbox("Year", ["All years"] + years)
selected_channel = st.selectbox("Store type", ["All store types"] + channels)

filtered = combined.copy()
if selected_year != "All years":
    filtered = filtered[filtered["Year"] == selected_year]
if selected_channel != "All store types":
    filtered = filtered[filtered["StoreType"] == selected_channel]

st.write(f"Scope: {selected_year}; {selected_channel}")
st.metric("Revenue for selected filters", f"${filtered['Revenue'].sum():,.2f}")
st.write("Sales records for selected filters:", len(filtered))

if filtered.empty:
    st.info("No sales match these filters. Choose another combination.")
    st.stop()

st.subheader("Revenue by store type")
channel_revenue = (
    filtered.groupby("StoreType")["Revenue"].sum().reset_index()
)
st.dataframe(
    channel_revenue.style.format({"Revenue": "${:,.2f}"}),
    hide_index=True
)
channel_chart = px.bar(
    channel_revenue,
    x="StoreType",
    y="Revenue",
    title="Revenue by store type — selected filters",
    labels={"StoreType": "Store type", "Revenue": "Revenue (USD)"}
)
channel_chart.update_yaxes(tickprefix="$", tickformat=",.0f")
channel_chart.update_traces(
    hovertemplate="%{x}<br>Revenue: $%{y:,.2f}<extra></extra>"
)
st.plotly_chart(channel_chart, use_container_width=True)

dated = filtered.dropna(subset=["Date"]).copy()
if dated.empty:
    st.info("No readable dates are available for the yearly and monthly charts.")
    st.stop()

dated["Year"] = dated["Year"].astype(int)

st.subheader("Revenue by year")
annual = (
    dated.groupby("Year")["Revenue"].sum().reset_index().sort_values("Year")
)
st.dataframe(
    annual.style.format({"Year": "{:.0f}", "Revenue": "${:,.2f}"}),
    hide_index=True
)
annual_chart = px.line(
    annual,
    x="Year",
    y="Revenue",
    markers=True,
    title="Revenue by year — selected filters",
    labels={"Revenue": "Revenue (USD)"}
)
annual_chart.update_xaxes(dtick=1, tickformat="d")
annual_chart.update_yaxes(
    tickprefix="$", tickformat=",.0f", rangemode="tozero"
)
annual_chart.update_traces(
    hovertemplate="Year: %{x}<br>Revenue: $%{y:,.2f}<extra></extra>"
)
st.plotly_chart(annual_chart, use_container_width=True)

st.subheader("Monthly revenue patterns")
st.write(
    "Each month’s share equals its revenue divided by total dated revenue "
    "within the selected filters. With All years selected, years are combined."
)

dated["Month number"] = dated["Date"].dt.month
monthly = (
    dated.groupby("Month number")["Revenue"]
    .sum().reset_index().sort_values("Month number")
)
monthly["Month"] = pd.to_datetime(
    monthly["Month number"].astype(str), format="%m"
).dt.month_name()

denominator = dated["Revenue"].sum()
if denominator == 0:
    st.info("Monthly shares cannot be calculated when total dated revenue is zero.")
else:
    monthly["Revenue share"] = monthly["Revenue"] / denominator
    st.dataframe(
        monthly[["Month", "Revenue", "Revenue share"]].style.format({
            "Revenue": "${:,.2f}",
            "Revenue share": "{:.2%}"
        }),
        hide_index=True
    )
    monthly_chart = px.bar(
        monthly,
        x="Month",
        y="Revenue share",
        title="Monthly share of revenue — selected filters",
        labels={"Revenue share": "Share of selected dated revenue"},
        category_orders={"Month": monthly["Month"].tolist()}
    )
    monthly_chart.update_yaxes(tickformat=".0%")
    monthly_chart.update_traces(
        hovertemplate="%{x}<br>Revenue share: %{y:.2%}<extra></extra>"
    )
    st.plotly_chart(monthly_chart, use_container_width=True)