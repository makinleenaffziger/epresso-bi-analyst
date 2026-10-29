from analytics import (
    get_revenue_by_channel,
    get_revenue_by_year,
    get_monthly_revenue_share
)

APPROVED_TOOLS = {
    "get_revenue_by_channel": get_revenue_by_channel,
    "get_revenue_by_year": get_revenue_by_year,
    "get_monthly_revenue_share": get_monthly_revenue_share
}

ALLOWED_ARGUMENTS = {"year", "channel", "category", "store"}

SUPPORTED_QUESTIONS = {
    "compare revenue by store type": "get_revenue_by_channel",
    "which store type has the most revenue": "get_revenue_by_channel",
    "show revenue by year": "get_revenue_by_year",
    "show monthly revenue shares": "get_monthly_revenue_share",
    "does revenue tell us profit": "get_revenue_by_channel"
}


def dispatch_tool(data, tool_name, arguments=None):
    """Run an approved tool and return its call log."""

    if arguments is None:
        arguments = {}

    log = {
        "function": tool_name,
        "arguments": arguments,
        "result": None
    }

    if tool_name not in APPROVED_TOOLS:
        log["result"] = {"error": "Unsupported analytical tool."}
        return log

    if not isinstance(arguments, dict):
        log["result"] = {"error": "Tool arguments must be named filters."}
        return log

    unknown = set(arguments) - ALLOWED_ARGUMENTS
    if unknown:
        log["result"] = {
            "error": "Unsupported filters: " + ", ".join(sorted(unknown))
        }
        return log

    for name, value in arguments.items():
        if name == "year":
            if value is not None and type(value) is not int:
                log["result"] = {
                    "error": "Year must be a whole-number year or None."
                }
                return log
        elif value is not None and not isinstance(value, str):
            log["result"] = {"error": f"{name} must be text or None."}
            return log

    explicit = {
        name: arguments.get(name)
        for name in ["year", "channel", "category", "store"]
    }
    log["arguments"] = explicit

    try:
        log["result"] = APPROVED_TOOLS[tool_name](data, **explicit)
    except Exception:
        log["result"] = {
            "error": "The calculation could not be completed. Check the loaded data."
        }

    return log


def answer_question(
    data, question, year=None, channel=None, category=None, store=None
):
    """Route supported questions to tools using explicit dashboard filters."""

    scope = {
        "year": year,
        "channel": channel,
        "category": category,
        "store": store
    }

    scope_text = (
        f"Scope: year={year if year is not None else 'All'}; "
        f"store type={channel if channel is not None else 'All'}; "
        f"category={category if category is not None else 'All'}; "
        f"store={store if store is not None else 'All'}."
    )

    normalized = " ".join(question.lower().strip().split()).rstrip("?.!")

    response = {
        "scope": scope_text,
        "findings": "",
        "interpretation": "",
        "next_steps": "",
        "tool_log": None
    }

    if normalized not in SUPPORTED_QUESTIONS:
        response["findings"] = "This question is not supported by this rules-based assistant."
        response["interpretation"] = (
            "It recognizes the listed questions and uses the dashboard filters. "
            "It does not interpret additional instructions inside a question."
        )
        response["next_steps"] = (
            "Choose a supported question and set the desired dashboard filters."
        )
        return response

    tool_name = SUPPORTED_QUESTIONS[normalized]
    log = dispatch_tool(data, tool_name, scope)
    response["tool_log"] = log
    result = log["result"]

    if "error" in result:
        response["findings"] = result["error"]
        response["interpretation"] = "There is insufficient usable data for this calculation."
        response["next_steps"] = "Check the uploaded data and filter selections."
        return response

    values = result["value"]

    if tool_name == "get_monthly_revenue_share":
        response["findings"] = "\n".join(
            f"- {row['month']}: ${row['revenue']:,.2f}, "
            f"{row['share']:.2%} of selected dated revenue."
            for row in values["months"]
        )
        response["interpretation"] = (
            "These shares describe the monthly pattern within the stated scope. "
            "When multiple years are included, their revenues are combined."
        )
    else:
        response["findings"] = "\n".join(
            f"- {name}: ${amount:,.2f}"
            for name, amount in values.items()
        )

        if tool_name == "get_revenue_by_year":
            response["interpretation"] = (
                "These are calendar-year totals within the selected scope. "
                "They do not explain what caused changes in revenue."
            )
        else:
            highest = max(values.values())
            leaders = [name for name, amount in values.items() if amount == highest]
            response["interpretation"] = (
                "Highest revenue among the selected store types: "
                + ", ".join(leaders) + "."
            )

    response["next_steps"] = (
        "No business action is justified by revenue alone. "
        "Consider costs, business context, and data limitations."
    )

    if normalized == "does revenue tell us profit":
        response["interpretation"] = (
            "Revenue does not establish profit. The supplied sales data does "
            "not include the costs and expenses needed to calculate profit."
        )
        response["next_steps"] = (
            "Obtain cost and expense data before assessing profitability."
        )

    caveats = result.get("caveats", [])
    if caveats:
        response["interpretation"] += "\n\nLimitations: " + " ".join(caveats)

    return response