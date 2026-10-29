import pandas as pd
from agent import dispatch_tool, answer_question

data = pd.DataFrame({
    "Date": ["2025-01-31", "2025-02-28", "2026-01-31"],
    "Revenue": [100, 200, 50],
    "StoreType": ["Website", "Brick & Mortar", "Website"],
    "Category": ["Beans", "Beans", "Syrups"],
    "Store ID": ["SH00", "SH01", "SH00"]
})
original = data.copy(deep=True)

# Approved dispatch and complete log.
log = dispatch_tool(data, "get_revenue_by_channel", {"year": 2025})
assert log["function"] == "get_revenue_by_channel"
assert log["arguments"] == {
    "year": 2025, "channel": None, "category": None, "store": None
}
assert log["result"]["value"] == {
    "Brick & Mortar": 200.0, "Website": 100.0
}

assert dispatch_tool(
    data, "get_revenue_by_year"
)["result"]["value"] == {"2025": 300.0, "2026": 50.0}

assert dispatch_tool(
    data, "get_monthly_revenue_share"
)["result"]["value"]["total_dated_revenue"] == 350.0

print("PASS: All approved tools and logs work.")

# Rejected requests.
for name, arguments in [
    ("delete_sales", {}),
    ("get_revenue_by_channel", {"profit": True}),
    ("get_revenue_by_channel", {"year": "2025"}),
    ("get_revenue_by_channel", ["2025"]),
    ("get_revenue_by_channel", {"store": "SH99"})
]:
    assert "error" in dispatch_tool(data, name, arguments)["result"]

print("PASS: Unsupported tools and invalid arguments are rejected.")

# Each supported question calls the intended tool.
questions = {
    "Compare revenue by store type": "get_revenue_by_channel",
    "Which store type has the most revenue?": "get_revenue_by_channel",
    "Show revenue by year": "get_revenue_by_year",
    "Show monthly revenue shares": "get_monthly_revenue_share"
}

for question, expected_tool in questions.items():
    answer = answer_question(data, question)
    assert answer["tool_log"]["function"] == expected_tool
    assert "error" not in answer["tool_log"]["result"]
    assert answer["scope"].startswith("Scope:")
    assert answer["findings"]
    assert answer["interpretation"]
    assert answer["next_steps"]

print("PASS: Supported questions call the correct tools.")

# Dashboard filters must reach the tool explicitly.
answer = answer_question(
    data,
    "Compare revenue by store type",
    year=2025,
    channel="Website",
    category="Beans",
    store="SH00"
)
assert answer["tool_log"]["result"]["value"] == {"Website": 100.0}
assert answer["tool_log"]["arguments"]["store"] == "SH00"
print("PASS: Answers use the explicit filters.")

# Unsupported questions must not invent an answer.
answer = answer_question(data, "What will sales be next year?")
assert answer["tool_log"] is None
assert "not supported" in answer["findings"]
print("PASS: Unsupported questions are identified.")

# Profit questions must explain the missing evidence.
answer = answer_question(data, "Does revenue tell us profit?")
assert "does not establish profit" in answer["interpretation"]
assert "cost" in answer["next_steps"].lower()
print("PASS: Revenue is not presented as profit.")

# Missing data must be explained.
missing = data.copy()
missing.loc[0, "Revenue"] = None
answer = answer_question(missing, "Compare revenue by store type")
assert "error" in answer["tool_log"]["result"]
assert "insufficient" in answer["interpretation"]
print("PASS: Missing revenue is explained.")

# The same question must respond to changed data.
changed = data.copy()
changed.loc[0, "Revenue"] += 1000
answer = answer_question(changed, "Compare revenue by store type")
assert answer["tool_log"]["result"]["value"]["Website"] == 1150.0
print("PASS: Answers change when the supplied data changes.")

pd.testing.assert_frame_equal(data, original)
print("PASS: Original data remains unchanged.")

print("All dispatcher and question tests passed.")