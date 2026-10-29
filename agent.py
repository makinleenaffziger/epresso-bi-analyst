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
        log["result"] = {
            "error": "Unsupported tool. Choose an approved analytical function."
        }
        return log

    if not isinstance(arguments, dict):
        log["result"] = {
            "error": "Tool arguments must be named filters."
        }
        return log

    unknown_arguments = set(arguments) - ALLOWED_ARGUMENTS
    if unknown_arguments:
        log["result"] = {
            "error": "Unsupported filters: "
            + ", ".join(sorted(unknown_arguments))
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
            log["result"] = {
                "error": f"{name} must be text or None."
            }
            return log

    explicit_arguments = {
        name: arguments.get(name)
        for name in ["year", "channel", "category", "store"]
    }
    log["arguments"] = explicit_arguments

    try:
        function = APPROVED_TOOLS[tool_name]
        log["result"] = function(data, **explicit_arguments)
    except Exception:
        log["result"] = {
            "error": "The calculation could not be completed. Check the loaded data."
        }

    return log