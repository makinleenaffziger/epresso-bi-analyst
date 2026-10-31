# E-Presso Assistant Testing

The assistant uses the currently uploaded data and explicit dashboard
filters. Gemini can select from three approved analytical tools.
Python calculates and formats the numerical findings.

If Gemini is unavailable or its explanation fails validation, the app
clearly labels its rules-based fallback. Certain limitation questions
receive a labeled rules-based response without an API call.

## Required tests

| Test | Question and scope | Function used | Expected behavior | Actual result |
| --- | --- | --- | --- | --- |
| 1. Numerical calculation | “Compare revenue by store type”; Year = 2025, Store type = Website, Category = All | get_revenue_by_channel | Website revenue = $3,160,230.00 | Matched. The tool log showed the selected filters and 240 rows. |
| 2. Numerical comparison | “Compare revenue by store type”; all filters = All | get_revenue_by_channel | Website = $27,218,880.00; Brick & Mortar = $14,955,560.00 | Matched. Website had higher revenue. Live Gemini and fallback responses were both observed during testing. |
| 3. Missing information | “Does revenue tell us profit?”; all filters = All | get_revenue_by_channel | Explain that revenue alone cannot establish profit because costs and expenses are missing | Passed with a live Gemini response. It identified the missing financial information. |
| 4. Analytical judgment | “Does higher customer satisfaction cause higher revenue?”; all filters = All | None | Explain that association does not establish causation and that the available tools do not analyze this relationship | Initial response was too vague. After revision, the labeled limitation response explained causation, alternative explanations, and the need for an appropriate study design. Retest passed. |
| 5. Updated data | Repeat the channel-revenue question after uploading Sales_test.csv without editing code or restarting | get_revenue_by_channel | Website increases by $1,000 to $27,219,880.00; Brick & Mortar remains $14,955,560.00 | The updated amounts were observed during testing. Before/after numerical screenshots were collected. |

## Numerical verification

The original channel totals reconcile to total revenue:

$27,218,880.00 + $14,955,560.00 = $42,174,440.00.

These amounts were compared with the Power BI report.

The modified Sales_test.csv increases one Website sales record by
exactly $1,000. Therefore, the expected modified total is
$42,175,440.00.

Numerical screenshots are saved separately in the project evidence
folder. They show answers and expanded tool-call logs.

## Additional checks

- Yearly revenue matched the validated Power BI amounts:
  - 2025: $7,181,750.00
  - 2026: $8,016,950.00
  - 2027: $8,824,720.00
  - 2028: $8,969,470.00
  - 2029: $9,181,550.00
- Monthly shares matched the validated results, including December
  at 25.61% of selected dated revenue.
- “Predict next year's profit” received an unsupported-request
  response and ran no analytical tool.
- The per-session question limit disabled further questions after
  the limit was reached.
- API connection failures and timeouts displayed a labeled fallback
  instead of crashing the dashboard.

## Revisions and retests

### Causation explanation

Problem: The satisfaction-and-revenue question received only a
generic unsupported-request message.

Revision: Added an explicit, labeled rules-based limitation response.
It explains that association does not prove causation, that the
current tools do not analyze survey-sales relationships, and that
other factors may affect both variables.

Retest: The same question returned the intended explanation without
running an analytical tool. Passed.

### Incorrect interpretation of scope

Problem: Gemini incorrectly stated that grouping revenue by year
excluded other channels. It also produced misleading wording about
whether months or years could be compared.

Revision: Clarified the explanation instructions, added checks for
known misleading phrases, and made Python supply the channel-scope
statement.

Retest: The yearly response correctly described rising revenue and
stated that no store-type filter was applied. Passed.

### Profit-question fallback

Problem: When Gemini timed out during its explanation, the fallback
answered a channel comparison instead of the original profit question.

Revision: Preserved the response to the original supported question
for use when Gemini fails.

Retest status: The live profit response passed after the revision.
The specific timeout-during-explanation path still needs a controlled
retest before claiming that fallback fix is fully verified.

## Limitations

Gemini requests sometimes returned connection timeouts or server
errors. A fallback result verifies the Python calculation and fallback
behavior, but does not demonstrate a successful live Gemini response.

The assistant cannot calculate profit without costs and expenses.
Its revenue tools cannot establish causation or forecast future
performance.

The latest local changes still need deployment and verification on
the hosted application.

## Hosted verification — October 30, 2026

The latest code was deployed and Gemini Secrets configured.

- Live Gemini returned the correct original channel totals.
- Year = 2025 and Store type = Website returned $3,160,230.00.
- The causation question returned the explicit limitation response.
- Uploading Sales_test.csv increased Website revenue to
  $27,219,880.00 while Brick & Mortar remained $14,955,560.00.
- Restoring Sales.csv returned Website revenue to $27,218,880.00.
- Both automated test suites passed after the local revisions.

These results supersede earlier notes that hosted verification was pending.

Remaining checks: controlled retest of the profit fallback during an
explanation timeout, and verification of Maci's own-account GitHub commit.

Known wording limitation: one filtered Gemini answer described the
single-channel result as though the full dataset contained one channel.
The scope and tool log correctly identified the Website filter.

## Controlled fallback retest — October 31, 2026

test_gemini_fallback.py simulated a successful channel calculation
followed by a timeout while requesting Gemini's explanation.

Passed: the fallback answered the original profit question, explained
the missing costs and expenses, retained the correct calculation and
filters in the log, and left the original data unchanged.

No real Gemini requests were made. This completes the previously
outstanding controlled profit-fallback retest.