import pandas as pd
from agent import dispatch_tool

data = pd.DataFrame({
    "Date": ["2025-01-31", "2025-02-28", "2026-01-31"],
    "Revenue": [100, 200, 50],
    "StoreType": ["Website", "Brick & Mortar", "Website"],
    "Category": ["Beans", "Beans", "Syrups"],
    "Store ID": ["SH00", "SH01", "SH00"]
})

original = data.copy(deep=True)

# Run an approved tool and check its log.
log = dispatch_tool(
    data,
    "get_revenue_by_channel",
    {"year": 2025}
)

assert log["function"] == "get_revenue_by_channel"
assert log["arguments"] == {
    "year": 2025,
    "channel": None,
    "category": None,
    "store": None
}
assert log["result"]["value"] == {
    "Brick & Mortar": 200.0,
    "Website": 100.0
}
print("PASS: Approved calculation and call log work.")

# Confirm the other two tools can also run.
log = dispatch_tool(data, "get_revenue_by_year")
assert log["result"]["value"] == {"2025": 300.0, "2026": 50.0}

log = dispatch_tool(data, "get_monthly_revenue_share")
assert log["result"]["value"]["total_dated_revenue"] == 350.0
print("PASS: All three approved tools are available.")

# Reject a tool that is not approved.
log = dispatch_tool(data, "delete_sales")
assert "error" in log["result"]
print("PASS: Unsupported tools are rejected.")

# Reject filters the tools do not accept.
log = dispatch_tool(
    data,
    "get_revenue_by_channel",
    {"profit": True}
)
assert "error" in log["result"]
print("PASS: Unsupported filters are rejected.")

# Reject an incorrectly formatted year.
log = dispatch_tool(
    data,
    "get_revenue_by_channel",
    {"year": "2025"}
)
assert "error" in log["result"]
print("PASS: Incorrect argument types are rejected.")

# Reject incorrectly structured arguments.
log = dispatch_tool(data, "get_revenue_by_channel", ["2025"])
assert "error" in log["result"]
print("PASS: Arguments must be named filters.")

# Let the analytical tool explain an unknown store.
log = dispatch_tool(
    data,
    "get_revenue_by_channel",
    {"store": "SH99"}
)
assert "error" in log["result"]
print("PASS: Unknown stores return an explanation.")

# Check that replacing the data changes the logged answer.
changed = data.copy()
changed.loc[0, "Revenue"] += 1000
log = dispatch_tool(changed, "get_revenue_by_channel")
assert log["result"]["value"]["Website"] == 1150.0
print("PASS: The dispatcher uses the supplied data.")

pd.testing.assert_frame_equal(data, original)
print("PASS: Original data remains unchanged.")

print("All dispatcher tests passed.")