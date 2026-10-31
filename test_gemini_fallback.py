from types import SimpleNamespace
from unittest.mock import patch

import pandas as pd

from gemini_agent import answer_with_gemini


data = pd.DataFrame({
    "Date": ["2025-01-31", "2025-01-31"],
    "Revenue": [100.0, 200.0],
    "StoreType": ["Website", "Brick & Mortar"],
    "Category": ["Beans", "Beans"],
    "Store ID": ["SH00", "SH01"],
})

original = data.copy(deep=True)

scope = {
    "year": None,
    "channel": None,
    "category": None,
    "store": None,
}

selection = SimpleNamespace(
    function_calls=[
        SimpleNamespace(
            name="get_revenue_by_channel",
            args=scope,
        )
    ]
)


class SimulatedClient:
    def __init__(self):
        self.models = self
        self.calls = 0

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def generate_content(self, **kwargs):
        self.calls += 1

        if self.calls == 1:
            return selection

        raise TimeoutError("Simulated explanation timeout")


client = SimulatedClient()

with patch(
    "gemini_agent.create_client",
    return_value=client,
):
    response = answer_with_gemini(
        data,
        "Does revenue tell us profit?",
        api_key="unused-test-key",
    )

assert client.calls == 2
assert response["mode"].startswith("Rules-based fallback:")
assert "requesting an explanation" in response["mode"]

interpretation = response["interpretation"].lower()
assert "costs and expenses" in interpretation
assert "profit" in interpretation
assert "highest revenue" not in interpretation
assert "cost and expense" in response["next_steps"].lower()

log = response["tool_log"][0]
assert log["function"] == "get_revenue_by_channel"
assert log["arguments"] == scope
assert log["result"]["value"]["Website"] == 100.0
assert log["result"]["value"]["Brick & Mortar"] == 200.0

pd.testing.assert_frame_equal(data, original)

print("PASS: Explanation timeout uses the original profit answer.")
print("PASS: Correct calculation and filters remain in the log.")
print("PASS: Original data remains unchanged.")
print("No real Gemini requests were made.")
print("All Gemini fallback tests passed.")