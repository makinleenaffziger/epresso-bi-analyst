import pandas as pd


def prepare_data(data, tool, definition, year, channel, category, store):
    """Apply explicit filters and prepare a consistent result."""

    result = {
        "tool": tool,
        "value": None,
        "definition": definition,
        "scope": {
            "year": year,
            "channel": channel,
            "category": category,
            "store": store
        },
        "rows_used": 0,
        "caveats": ["Revenue is not profit."]
    }

    required = ["Date", "Revenue", "StoreType", "Category", "Store ID"]
    missing = [column for column in required if column not in data.columns]

    if missing:
        result["error"] = "Missing columns: " + ", ".join(missing)
        return None, result

    working = data.copy()
    working["Date"] = pd.to_datetime(working["Date"], errors="coerce")
    working["Revenue"] = pd.to_numeric(working["Revenue"], errors="coerce")
    working["Year"] = working["Date"].dt.year

    filters = [
        ("Year", year),
        ("StoreType", channel),
        ("Category", category),
        ("Store ID", store)
    ]

    for column, selected in filters:
        if selected is not None:
            allowed = working[column].dropna().unique().tolist()
            if selected not in allowed:
                result["error"] = f"Unknown {column}: {selected}"
                return None, result

    unreadable_dates = int(working["Date"].isna().sum())
    if year is not None and unreadable_dates:
        result["caveats"].append(
            f"{unreadable_dates} input rows have unreadable dates "
            "and cannot be assigned to the requested year."
        )

    for column, selected in filters:
        if selected is not None:
            working = working[working[column] == selected]

    if working.empty:
        result["error"] = "No sales match these filters."
        return None, result

    if working["Revenue"].isna().any():
        result["error"] = "Selected sales contain missing or unreadable revenue."
        return None, result

    return working, result


def get_revenue_by_channel(
    data, year=None, channel=None, category=None, store=None
):
    """Calculate revenue grouped by store type."""

    working, result = prepare_data(
        data,
        "get_revenue_by_channel",
        "Sum of revenue grouped by store type.",
        year, channel, category, store
    )
    if working is None:
        return result

    unknown = int(working["StoreType"].isna().sum())
    if unknown:
        result["caveats"].append(
            f"{unknown} rows have no store type and are grouped as Unknown."
        )

    working["StoreType"] = working["StoreType"].fillna("Unknown")
    totals = working.groupby("StoreType")["Revenue"].sum()

    result["value"] = {
        str(name): float(amount)
        for name, amount in totals.items()
    }
    result["rows_used"] = len(working)
    return result


def get_revenue_by_year(
    data, year=None, channel=None, category=None, store=None
):
    """Calculate revenue grouped by calendar year."""

    working, result = prepare_data(
        data,
        "get_revenue_by_year",
        "Sum of revenue grouped by calendar year; unreadable dates excluded.",
        year, channel, category, store
    )
    if working is None:
        return result

    excluded = int(working["Date"].isna().sum())
    if excluded:
        result["caveats"].append(
            f"{excluded} selected rows were excluded because their dates are unreadable."
        )

    working = working.dropna(subset=["Date"])
    if working.empty:
        result["error"] = "No readable dates are available for these filters."
        return result

    totals = working.groupby("Year")["Revenue"].sum().sort_index()

    result["value"] = {
        str(int(name)): float(amount)
        for name, amount in totals.items()
    }
    result["rows_used"] = len(working)
    return result


def get_monthly_revenue_share(
    data, year=None, channel=None, category=None, store=None
):
    """Calculate each month's share of selected dated revenue."""

    working, result = prepare_data(
        data,
        "get_monthly_revenue_share",
        "Calendar-month revenue divided by total dated revenue within "
        "the explicit filters. Shares are fractions: 0.25 means 25%.",
        year, channel, category, store
    )
    if working is None:
        return result

    excluded = int(working["Date"].isna().sum())
    if excluded:
        result["caveats"].append(
            f"{excluded} selected rows were excluded because their dates are unreadable."
        )

    working = working.dropna(subset=["Date"])
    if working.empty:
        result["error"] = "No readable dates are available for these filters."
        return result

    denominator = float(working["Revenue"].sum())
    if denominator == 0:
        result["error"] = "Monthly shares are undefined when total dated revenue is zero."
        return result

    working["Month"] = working["Date"].dt.month
    totals = working.groupby("Month")["Revenue"].sum().sort_index()

    months = []
    for month_number, revenue in totals.items():
        month_name = pd.Timestamp(
            year=2000, month=int(month_number), day=1
        ).month_name()
        months.append({
            "month": month_name,
            "revenue": float(revenue),
            "share": float(revenue / denominator)
        })

    result["value"] = {
        "total_dated_revenue": denominator,
        "months": months
    }
    result["rows_used"] = len(working)

    if year is None:
        result["caveats"].append(
            "Months are combined across all selected years, "
            "not averaged across yearly percentages."
        )

    return result