import streamlit as st
import pandas as pd

st.title("Welcome to E-Presso!")
st.write("My business intelligence app is starting.")

st.subheader("What each row represents")

grain = pd.DataFrame([
    {
        "Table": "Stores",
        "One row represents": "One store or the website sales channel.",
        "Key": "ID",
        "Contains revenue?": "No"
    },
    {
        "Table": "Survey Results",
        "One row represents": "Survey results for one store in one year.",
        "Key": "Survey ID",
        "Contains revenue?": "No"
    },
    {
        "Table": "Sales",
        "One row represents": "One product's revenue at one store or the website for one month.",
        "Key": "Sales ID",
        "Contains revenue?": "Yes"
    },
    {
        "Table": "Products",
        "One row represents": "One product identified by its Product ID.",
        "Key": "Product ID",
        "Contains revenue?": "No"
    },
    {
        "Table": "Categories",
        "One row represents": "One product category.",
        "Key": "Category ID",
        "Contains revenue?": "No"
    }
])

st.dataframe(grain, hide_index=True)

st.subheader("Upload store data")
stores_file = st.file_uploader("Choose your Stores CSV file", type=["csv"])

if stores_file is not None:
    stores = pd.read_csv(stores_file, skiprows=1, dtype=str)
    st.dataframe(stores)
    st.write("Number of store records:", len(stores))
    st.write("Duplicate store IDs:", stores["ID"].duplicated().sum())

    st.subheader("Missing store values by column")
    st.dataframe(stores.isna().sum().rename("Missing values"))

st.subheader("Upload survey data")
survey_file = st.file_uploader("Choose your Survey Excel file", type=["xlsx"])

if survey_file is not None:
    survey = pd.read_excel(
        survey_file,
        sheet_name="Survey Results",
        skiprows=2
    )
    st.dataframe(survey)
    st.write("Number of survey records:", len(survey))
    st.write("Duplicate survey IDs:", survey["Survey ID"].duplicated().sum())

    st.subheader("Missing survey values by column")
    st.dataframe(survey.isna().sum().rename("Missing values"))

st.subheader("Upload sales data")
sales_file = st.file_uploader("Choose your Sales CSV file", type=["csv"])

if sales_file is not None:
    sales = pd.read_csv(sales_file)
    st.dataframe(sales)
    st.write("Number of sales records:", len(sales))
    st.write("Duplicate sales IDs:", sales["Sales ID"].duplicated().sum())

    st.subheader("Missing sales values by column")
    st.dataframe(sales.isna().sum().rename("Missing values"))

    sales["Revenue"] = pd.to_numeric(sales["Revenue"], errors="raise")
    total_revenue = sales["Revenue"].sum()
    st.metric("Total revenue — all uploaded sales", f"${total_revenue:,.2f}")

st.subheader("Upload product data")
products_file = st.file_uploader("Choose your Products CSV file", type=["csv"])

if products_file is not None:
    products = pd.read_csv(products_file, dtype=str)
    st.dataframe(products)
    st.write("Number of product records:", len(products))
    st.write("Duplicate product IDs:", products["Product ID"].duplicated().sum())

    st.subheader("Missing product values by column")
    st.dataframe(products.isna().sum().rename("Missing values"))

st.subheader("Upload category data")
categories_file = st.file_uploader("Choose your Categories CSV file", type=["csv"])

if categories_file is not None:
    categories = pd.read_csv(categories_file, dtype=str)
    st.dataframe(categories)
    st.write("Number of category records:", len(categories))
    st.write("Duplicate category IDs:", categories["Category ID"].duplicated().sum())

    st.subheader("Missing category values by column")
    st.dataframe(categories.isna().sum().rename("Missing values"))