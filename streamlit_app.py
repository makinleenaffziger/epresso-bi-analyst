import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Welcome to E-Presso!")
st.write("My business intelligence app is starting.")

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
    st.subheader(f"Missing {name} values by column")
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
    sales["Revenue"] = pd.to_numeric(sales["Revenue"], errors="raise")
    total_revenue = sales["Revenue"].sum()
    st.metric("Total revenue — all uploaded sales", f"${total_revenue:,.2f}")

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

if stores_file is not None and sales_file is not None:
    if stores["ID"].isna().any() or stores["ID"].duplicated().any():
        st.error("Stores must have a unique, nonblank ID for every row.")
    else:
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

        st.subheader("Revenue by store type")
        channel_revenue = (
            combined.assign(
                StoreType=combined["StoreType"].fillna("Unknown store type")
            )
            .groupby("StoreType")["Revenue"]
            .sum()
            .reset_index()
        )
        st.dataframe(
            channel_revenue.style.format({"Revenue": "${:,.2f}"}),
            hide_index=True
        )

        chart = px.bar(
            channel_revenue,
            x="StoreType",
            y="Revenue",
            title="Total revenue by store type — all uploaded sales",
            labels={"StoreType": "Store type", "Revenue": "Revenue (USD)"}
        )
        chart.update_yaxes(tickprefix="$", tickformat=",.0f")
        chart.update_traces(
            hovertemplate="%{x}<br>Revenue: $%{y:,.2f}<extra></extra>"
        )
        st.plotly_chart(chart, use_container_width=True)
else:
    st.info("Upload both Stores and Sales to connect them.")

st.subheader("Revenue by year")

if sales_file is not None:
    dated_sales = sales.copy()
    dated_sales["Date"] = pd.to_datetime(
        dated_sales["Date"], errors="coerce"
    )
    invalid_dates = dated_sales["Date"].isna().sum()
    st.write("Sales records with missing or unreadable dates:", invalid_dates)

    if invalid_dates > 0:
        st.warning(
            "Rows with missing or unreadable dates are excluded from "
            "the yearly and monthly results."
        )

    dated_sales = dated_sales.dropna(subset=["Date"])
    dated_sales["Year"] = dated_sales["Date"].dt.year

    annual_revenue = (
        dated_sales.groupby("Year")["Revenue"]
        .sum()
        .reset_index()
        .sort_values("Year")
    )
    st.dataframe(
        annual_revenue.style.format({
            "Year": "{:.0f}", "Revenue": "${:,.2f}"
        }),
        hide_index=True
    )

    annual_chart = px.line(
        annual_revenue,
        x="Year",
        y="Revenue",
        markers=True,
        title="Total revenue by year — all uploaded sales",
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
        "Each percentage is that calendar month's revenue across all "
        "uploaded years, divided by total revenue with a readable date. "
        "This is a combined share, not an average of yearly percentages."
    )

    dated_sales["Month number"] = dated_sales["Date"].dt.month
    monthly_revenue = (
        dated_sales.groupby("Month number")["Revenue"]
        .sum()
        .reset_index()
        .sort_values("Month number")
    )
    monthly_revenue["Month"] = pd.to_datetime(
        monthly_revenue["Month number"].astype(str),
        format="%m"
    ).dt.month_name()

    denominator = dated_sales["Revenue"].sum()

    if denominator == 0:
        st.info("Monthly revenue shares cannot be calculated when total revenue is zero.")
    else:
        monthly_revenue["Revenue share"] = (
            monthly_revenue["Revenue"] / denominator
        )

        st.dataframe(
            monthly_revenue[["Month", "Revenue", "Revenue share"]]
            .style.format({
                "Revenue": "${:,.2f}",
                "Revenue share": "{:.2%}"
            }),
            hide_index=True
        )

        monthly_chart = px.bar(
            monthly_revenue,
            x="Month",
            y="Revenue share",
            title="Monthly share of revenue — all uploaded years combined",
            labels={"Revenue share": "Share of total revenue"},
            category_orders={"Month": monthly_revenue["Month"].tolist()}
        )
        monthly_chart.update_yaxes(tickformat=".0%")
        monthly_chart.update_traces(
            hovertemplate="%{x}<br>Revenue share: %{y:.2%}<extra></extra>"
        )
        st.plotly_chart(monthly_chart, use_container_width=True)
else:
    st.info("Upload Sales to see yearly and monthly revenue.")