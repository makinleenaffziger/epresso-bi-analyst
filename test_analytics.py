import math
import pandas as pd

from analytics import (
    get_revenue_by_channel,
    get_revenue_by_year,
    get_monthly_revenue_share
)

data = pd.DataFrame({
    "Date": ["2025-01-31", "2025-02-28", "2026-01-31"],
    "Revenue": [100, 200, 50],
    "StoreType": ["Website", "Brick & Mortar", "Website"],
    "Category": ["Beans", "Beans", "Syrups"],
    "Store ID": ["SH00", "SH01", "SH00"]
})

original = data.copy(deep=True)

# Channel totals: Website = 100 + 50. Physical stores = 200.
result = get_revenue_by_channel(data)
assert result["value"] == {"Brick & Mortar": 200.0, "Website": 150.0}
assert result["rows_used"] == 3
print("PASS: Channel totals are correct.")

# Yearly totals: 2025 = 100 + 200. 2026 = 50.
result = get_revenue_by_year(data)
assert result["value"] == {"2025": 300.0, "2026": 50.0}
assert result["rows_used"] == 3
print("PASS: Yearly totals are correct.")

# Across both years: January = 150, February = 200, total = 350.
result = get_monthly_revenue_share(data)
months = {row["month"]: row for row in result["value"]["months"]}
assert result["value"]["total_dated_revenue"] == 350.0
assert months["January"]["revenue"] == 150.0
assert months["February"]["revenue"] == 200.0
assert math.isclose(months["January"]["share"], 150 / 350)
assert math.isclose(months["February"]["share"], 200 / 350)
assert math.isclose(sum(row["share"] for row in months.values()), 1.0)
print("PASS: Monthly amounts and shares are correct.")

# Selecting 2025 changes the monthly denominator to 300.
result = get_monthly_revenue_share(data, year=2025)
months = {row["month"]: row for row in result["value"]["months"]}
assert result["value"]["total_dated_revenue"] == 300.0
assert math.isclose(months["January"]["share"], 100 / 300)
assert math.isclose(months["February"]["share"], 200 / 300)
assert result["rows_used"] == 2
print("PASS: Monthly shares use the selected year's total.")

tools = [
    get_revenue_by_channel,
    get_revenue_by_year,
    get_monthly_revenue_share
]

for tool in tools:
    # All four filters together select just the first row.
    result = tool(
        data,
        year=2025,
        channel="Website",
        category="Beans",
        store="SH00"
    )
    assert "error" not in result
    assert result["rows_used"] == 1
    assert result["scope"] == {
        "year": 2025,
        "channel": "Website",
        "category": "Beans",
        "store": "SH00"
    }

    result = tool(data, store="SH99")
    assert "error" in result
    assert result["value"] is None

    result = tool(data, year=2026, channel="Brick & Mortar")
    assert "error" in result

    missing = data.copy()
    missing.loc[0, "Revenue"] = None
    assert "error" in tool(missing)

    assert "error" in tool(data.drop(columns=["Revenue"]))

    print(f"PASS: Filters and error handling for {tool.__name__}.")

# Unreadable dates must be excluded and explained by date-based tools.
bad_dates = data.copy()
bad_dates.loc[0, "Date"] = "not a date"

result = get_revenue_by_year(bad_dates)
assert result["value"] == {"2025": 200.0, "2026": 50.0}
assert result["rows_used"] == 2
assert len(result["caveats"]) > 1

result = get_monthly_revenue_share(bad_dates)
assert result["value"]["total_dated_revenue"] == 250.0
assert result["rows_used"] == 2
assert len(result["caveats"]) > 1
print("PASS: Unreadable dates are excluded and explained.")

# A zero denominator must return an explanation.
zero_data = data.copy()
zero_data["Revenue"] = 0
result = get_monthly_revenue_share(zero_data)
assert "error" in result
assert result["value"] is None
print("PASS: Zero total revenue is handled.")

# Increasing the first row by $1,000 updates every relevant calculation.
changed = data.copy()
changed.loc[0, "Revenue"] += 1000

assert get_revenue_by_channel(changed)["value"] == {
    "Brick & Mortar": 200.0,
    "Website": 1150.0
}
assert get_revenue_by_year(changed)["value"] == {
    "2025": 1300.0,
    "2026": 50.0
}

result = get_monthly_revenue_share(changed)
months = {row["month"]: row for row in result["value"]["months"]}
assert result["value"]["total_dated_revenue"] == 1350.0
assert months["January"]["revenue"] == 1150.0
assert months["February"]["revenue"] == 200.0
assert math.isclose(months["January"]["share"], 1150 / 1350)
print("PASS: All three tools respond to updated data.")

pd.testing.assert_frame_equal(data, original)
print("PASS: Original data remains unchanged.")

print("All tests passed.")