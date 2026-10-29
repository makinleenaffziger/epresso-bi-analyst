# E-Presso Analytical Assistant Tests

Tests performed October 29, 2026.

## Implementation

The current assistant is rules-based. It recognizes a fixed list of
supported questions and calls approved analytical functions.

It is not yet connected to a language-model API.

Approved tools:
- get_revenue_by_channel
- get_revenue_by_year
- get_monthly_revenue_share

Each calculated answer displays its scope, findings, interpretation,
next steps, and a tool-call log containing the function name, explicit
arguments, and raw result.

## Test results

| Test | Question | Function | Expected behavior | Actual result | Status |
|---|---|---|---|---|---|
| Numerical calculation | Compare revenue by store type | get_revenue_by_channel | Original channel totals | Website $27,218,880; Brick & Mortar $14,955,560 | Pass locally and online |
| Numerical comparison | Which store type has the most revenue? | get_revenue_by_channel | Identify the highest channel using calculated evidence | Website identified with both channel totals shown | Pass locally |
| Missing information | Does revenue tell us profit? | get_revenue_by_channel | Explain that cost and expense data are unavailable | No profit calculated; missing costs and expenses explained | Pass locally |
| Analytical judgment | Does revenue tell us profit? | get_revenue_by_channel | Avoid treating revenue as profitability | Recommended obtaining costs and expenses before assessing profit | Pass locally |
| Updated data | Compare revenue by store type | get_revenue_by_channel | Changing one Website revenue value by $1,000 updates its answer | Website rose to $27,219,880; Brick & Mortar stayed $14,955,560 | Pass locally and online |
| Unsupported request | What will sales be next year? | None | Decline unsupported forecasting without inventing numbers | Explained supported scope; no tool executed | Pass locally |
| Yearly calculation | Show revenue by year | get_revenue_by_year | Match validated annual totals | All five annual totals matched | Pass locally |
| Monthly calculation | Show monthly revenue shares | get_monthly_revenue_share | Match dashboard monthly values | January 7.74%; December 25.61%; denominator $42,174,440 | Pass locally |
| Filtered calculation | Compare revenue by store type | get_revenue_by_channel | Apply 2025 and Website filters explicitly | $3,160,230; scope and log showed the filters; 240 rows used | Pass locally |
| Filtered updated data | Compare revenue by store type | get_revenue_by_channel | Modified 2025 Website revenue rises by $1,000 | $3,161,230 | Pass locally |
| Restore original data | Compare revenue by store type | get_revenue_by_channel | Original answer returns after restoring Sales.csv | All-years Website returned to $27,218,880; filtered 2025 Website returned to $3,160,230 | Pass |

The missing-information and analytical-judgment checks above used the
same profit question to assess two different requirements.

## Original annual totals checked through the assistant

| Year | Revenue |
|---|---:|
| 2025 | $7,181,750.00 |
| 2026 | $8,016,950.00 |
| 2027 | $8,824,720.00 |
| 2028 | $8,969,470.00 |
| 2029 | $9,181,550.00 |

## Updated-data procedure

Sales_test.csv changed the first data row's revenue from $6,780 to
$7,780. The affected row was dated January 31, 2025, with Store ID SH00,
Product ID P01, and Category ID C1.

The same channel question was asked using modified and original data.
No source-code change or app restart was needed.

Replacing an upload temporarily reset dashboard filters when the file
was removed. Filters were reselected before the filtered comparison.
The displayed answer scope was checked rather than assumed.

Original Sales.csv was restored after testing.

## Troubleshooting and retest

During development, test code was accidentally placed in agent.py.
This caused an ImportError because agent.py tried to import functions
from itself.

The application code was restored to agent.py, and the test code was
placed in test_agent.py. Running python3 test_agent.py then reported:
“All dispatcher and question tests passed.”

This records a file-placement fix and successful retest. A separate
analytical or answer-behavior improvement should also be documented
before final submission.

An initially high Website answer was traced to Sales_test.csv still
being loaded locally. Uploading original Sales.csv returned Website
revenue from $27,219,880 to $27,218,880. The calculation was correct for
each supplied file.

## Automated checks

python3 test_analytics.py
- Channel, annual, and monthly calculations.
- Explicit filters.
- Unknown values and missing columns.
- Missing revenue and unreadable dates.
- Zero denominator.
- Updated data.
- Original data preservation.

python3 test_agent.py
- Approved dispatcher functions and complete logs.
- Rejection of unsupported tools and invalid arguments.
- Correct routing of supported questions.
- Scope and explicit filters.
- Unsupported questions.
- Profit limitations.
- Missing revenue.
- Updated data and original data preservation.

Both test scripts passed.

## Remaining checks and evidence

- PASS: On the live app, the question box became disabled at the 15-question session limit.- Save screenshots showing answers and tool-call logs for numerical tests.
- Document an analytical or answer-behavior fix and retest.
- If a live model is added, test API failure or quota fallback.
- Repeat relevant assistant tests after any implementation changes.