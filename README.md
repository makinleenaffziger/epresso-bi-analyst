# E-Presso Business Intelligence App

A Streamlit dashboard for exploring E-Presso revenue, checking data quality, and asking an analytical assistant business questions.

## Open the app

https://makinleenaffziger-epresso-bi-analyst-streamlit-app-5ax0cw.streamlit.app/

The app opens without a login and automatically loads the original E-Presso data. If it is sleeping, allow time for it to start.

Keep the application deployed and this repository available until grading is complete.

## Dashboard features

- Revenue metrics for the selected data.
- Three interactive charts: annual revenue, revenue by store type, and monthly revenue shares.
- Filters for year, store type, and category.
- Replacement uploads for testing updated data.
- Data profiles, missing-value reports, duplicate-ID checks, and verified table connections.
- A Gemini analytical assistant with approved tools and visible calculation logs.
- A rules-based fallback and a 15-question session limit.

The dashboard has three tabs:

| Tab | Purpose |
|---|---|
| Revenue overview | Revenue metrics, charts, exact figures, and a selected-sales download |
| Analytical assistant | Business questions, calculated answers, and tool-call logs |
| Data quality | Table profiles, grains, missing values, duplicate IDs, and merge checks |

## Original data and replacement uploads

Original files load automatically from the repository’s data folder:

| Table | File | Reading method |
|---|---|---|
| Stores | data/Stores.csv | Skip the first title line; preserve text fields |
| Survey Results | data/Survey.xlsx | Survey Results sheet; skip the first two lines |
| Sales | data/Sales.csv | First row contains column names |
| Products | data/Products.csv | First row contains column names |
| Categories | data/Categories.csv | First row contains column names |

Sales, Products, and Categories were exported from the supplied Microsoft Access database.

To test updated data, expand **Manage data** in the sidebar and upload a replacement for the appropriate table. Removing an upload restores that table’s original data.

Uploads apply to the current browser session and do not overwrite the original files. Updated files must retain the expected columns, worksheet names, and data types. Values and rows may change. Filter options come from the loaded data.

## Table grains and relationships

| Table | One row represents | Key |
|---|---|---|
| Stores | One store or the website channel | ID |
| Survey Results | One store’s survey results for one year | Survey ID |
| Sales | One product’s revenue at one store or channel for one month | Sales ID |
| Products | One product | Product ID |
| Categories | One product category | Category ID |

Sales uses left joins to connect to:

- Stores through Sales.Store ID → Stores.ID.
- Products through Product ID.
- Categories through Category ID.

Lookup keys must be unique and nonblank. Each join uses a many-to-one check and records row counts, revenue before and after, and unmatched sales.

Product names are not unique, so Product ID identifies products.

Survey Results is profiled separately and is not joined to Sales. Joining only on Store ID could repeat revenue across survey years. Missing survey responses remain blank, not zero.

## Calculation definitions

Revenue is the sum of the currently loaded Sales.Revenue values within the selected filters.

Annual revenue groups sales with readable dates by calendar year.

Monthly share is a calendar month’s selected revenue divided by total selected revenue with readable dates. When multiple years are selected, their revenue is combined. Annual percentages are not averaged.

The overview and assistant use the dashboard filters. Data profiles and merge checks describe the full loaded data.

Missing or unreadable dates are reported and excluded from date-based calculations. Missing, unreadable, or nonfinite revenue blocks dashboard calculations until corrected. Unmatched lookup records remain in the data, with missing labels displayed as Unknown labels.

## Analytical assistant

Check **Use Gemini** in the Analytical assistant tab to enable the live language-model connection. Uncheck it to use the rules-based assistant.

The configured model is **gemini-3.1-flash-lite**.

Example questions:

- Compare revenue by store type.
- Which store type has the most revenue?
- Show revenue by year.
- Show monthly revenue shares.
- Does revenue tell us profit?
- Does higher customer satisfaction cause higher revenue?

Set dashboard filters before asking. The assistant does not change filters based on instructions inside a question.

### Approved tools

- get_revenue_by_channel
- get_revenue_by_year
- get_monthly_revenue_share

Gemini selects an approved tool. Python validates the requested filters, executes the calculation, and formats the numerical findings. Gemini receives the result and provides an explanation.

Each analytical tool returns:

- Tool name
- Calculated value
- Calculation definition
- Scope
- Number of rows used
- Caveats

Answers display **Scope, Findings, Interpretation, and Next steps**. A visible tool-call log records the function, arguments, and raw result. If no analytical tool runs, the app states that clearly.

The assistant cannot modify the data or execute arbitrary model-generated Python or SQL. Unsupported questions receive a response explaining its available capabilities.

The supported satisfaction-causation question receives a clearly labeled rules-based limitation response. No correlation or causal analysis is claimed or performed.

### Session limit and fallback

The question box is disabled after 15 questions in a browser session. Changing filters or loaded analytical data clears previous answers while retaining the question count.

Gemini requests have experienced server errors and timeouts. When a request fails, the app provides a labeled rules-based fallback where supported. The fallback uses actual Python calculations.

Generated explanations require review. A filtered response previously confused the selected single-channel result with the full dataset. Correct numbers and tool logs do not guarantee that every explanatory sentence is accurate.

## Validation and testing

Original-data results matched Power BI:

| Measure | Verified result |
|---|---:|
| Total revenue, 2025–2029 | $42,174,440.00 |
| Website revenue | $27,218,880.00 |
| Brick & Mortar revenue | $14,955,560.00 |
| 2025 Website revenue | $3,160,230.00 |
| Website Beans revenue, all years | $3,645,210.00 |

All five annual totals matched exactly. All 12 monthly revenue shares matched to the two decimal places displayed.

A separate Python calculation summed Revenue directly from the original Sales.csv without joins.

### Modified-data test

One Website sales record was increased from $6,780.00 to $7,780.00 in a separate Sales_test.csv.

The dashboard total increased to $42,175,440.00. The assistant’s Website total increased to $27,219,880.00, while Brick & Mortar remained $14,955,560.00.

Results updated without code edits or an app restart. Restoring the original data restored the original totals.

Beans-only and January-only modified results were not separately checked. The monthly comparison does not verify every possible filter combination.

### Automated checks

Run from the project folder:

```bash
python3 test_analytics.py
python3 test_agent.py
python3 test_gemini_fallback.py
```

The analytics and dispatcher tests use small datasets with hand-checkable answers. The fallback test simulates an explanation timeout without making real Gemini requests.

All three test files passed during the November 4, 2026 review. The hosted app also produced a successful Gemini answer after earlier 503/504 failures.

See validation.md and agent_tests.md for detailed development records. Some records retain earlier pending notes followed by dated completion updates.

These numerical values document tests; application answers are calculated from loaded data rather than hardcoded.

## Run locally

Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Start the app:

```bash
python3 -m streamlit run streamlit_app.py
```

Open the Local URL printed in the terminal. The port may vary.

For local Gemini access, create a private .streamlit/secrets.toml file containing:

```toml
GEMINI_API_KEY = "YOUR_PRIVATE_KEY"
```

Keep this file out of GitHub. For the hosted app, configure the key in Streamlit Community Cloud’s Secrets settings.

Never paste an API key into AI chats, documentation, screenshots, or public code.

## Main files

| File | Purpose |
|---|---|
| streamlit_app.py | Active dashboard entry point |
| analytics.py | Three approved analytical functions |
| agent.py | Dispatcher and rules-based responses |
| gemini_agent.py | Gemini tool selection, explanations, checks, and fallback |
| assistant_ui.py | Chat interface, history, session limit, and logs |
| test_analytics.py | Calculation and data-handling tests |
| test_agent.py | Dispatcher and question-handling tests |
| test_gemini_fallback.py | Simulated explanation-timeout test |
| validation.md | Power BI comparisons and modified-data records |
| agent_tests.md | Assistant tests, revisions, and retests |
| contributions.md | Team responsibilities |
| reflection.md | Development reflection |
| requirements.txt | Required Python packages |
| data/ | Original E-Presso data for automatic loading |

The older app.py is not the hosted entry point.

## Team contributions

**Makinlee Naffziger:** Implemented and ran AI-assisted code, tested and deployed the app, performed validation and assistant tests, saved evidence, and prepared documentation.

**Maci St. Cyr:** Retrieved Power BI information, guided comparisons, reviewed validation values, and committed her review using her own GitHub account, macistcyr.

Both teammates reviewed the reflection and contribution statement.

## Limitations

- Revenue is not profit; cost and expense data are not supplied.
- Revenue summaries cannot establish causation.
- Survey responses have missing values, and the tools do not analyze survey-sales relationships.
- Gemini availability varies, and explanations require human review.
- The rules-based assistant recognizes a limited set of questions.
- Broader testing and additional controls would be needed before relying on the app for major business decisions.
