# E-Presso Business Intelligence App

An interactive Streamlit application for exploring E-Presso revenue
and checking the quality of its source data.

## Open the app

https://makinleenaffziger-epresso-bi-analyst-streamlit-app-5ax0cw.streamlit.app/

The app opens without a login. If it is sleeping, allow it time to start.

## Current features

- Uploads for Stores, Survey Results, Sales, Products, and Categories.
- Descriptions of what one row represents in each table.
- Row counts, duplicate-ID checks, and missing-value reports.
- Verified connections between Sales and its lookup tables.
- Revenue by store type, year, and calendar month.
- Year, store-type, and category filters.
- A rules-based analytical assistant with visible tool-call logs.
- A 15-question limit per assistant session.

## Upload the data

Use the upload boxes in the application.

| Upload | File | Reading method |
|---|---|---|
| Stores | Support_EX_B_Stores 2.csv | Skip the first title line; preserve text fields |
| Survey | Support_EX_B_Survey.xlsx | Survey Results sheet; skip the first two lines |
| Sales | Sales.csv | Read column headings from the first row |
| Products | Products.csv | Read column headings from the first row |
| Categories | Categories.csv | Read column headings from the first row |

Sales.csv, Products.csv, and Categories.csv were exported from the
supplied Microsoft Access database as comma-delimited files with field
names in the first row.

Stores, Sales, Products, and Categories are required for the dashboard.
The Survey upload is profiled separately and is not joined to Sales.

Uploads belong to the current browser session. They are not saved back
to the source files. Upload them again when starting a fresh session.

Updated files must retain the expected sheets, column names, and data
types. Values and rows may change. Filter options come from loaded data.

## Table grain and relationships

| Table | One row represents | Key |
|---|---|---|
| Stores | One store or the website sales channel | ID |
| Survey Results | One store's survey results for one year | Survey ID |
| Sales | One product's revenue at one store or the website for one month | Sales ID |
| Products | One product identified by its Product ID | Product ID |
| Categories | One product category | Category ID |

Sales connects to:
- Stores through Sales.Store ID → Stores.ID.
- Products through Product ID.
- Categories through Category ID.

The application uses left joins and checks that lookup keys are unique
and nonblank. It displays row counts, revenue totals, and unmatched
sales around each connection.

Product names are not unique, so Product ID is used for connections.

Survey Results is not joined to Sales. Joining only on Store ID would
risk repeating sales because each store has multiple survey years.

## Calculation definitions

Revenue is the sum of the currently loaded Sales.Revenue values.

The dashboard filters affect its revenue metric, tables, charts, and
assistant answers. Data profiles and connection checks describe the
full uploaded files.

Yearly revenue groups dated sales by calendar year.

Monthly share equals a calendar month's selected revenue divided by
total selected revenue with readable dates. When multiple years are
selected, their revenue is combined; yearly percentages are not averaged.

Missing or unreadable dates are reported and excluded from date-based
charts. Missing or unreadable revenue blocks dashboard calculations
until the file is corrected.

Unmatched lookup records remain in the left-joined data. Missing category
and channel labels appear as Unknown labels.

## Analytical assistant

The current implementation is rules-based, not a live language-model
agent. It recognizes these supported questions:

- Compare revenue by store type
- Which store type has the most revenue?
- Show revenue by year
- Show monthly revenue shares
- Does revenue tell us profit?

Set the dashboard filters before asking. The current router does not
interpret additional filters or instructions inside a question.

The assistant uses only these approved functions:
- get_revenue_by_channel
- get_revenue_by_year
- get_monthly_revenue_share

Each answer identifies its scope and separates findings, interpretation,
and next steps. Its visible tool log includes the function, explicit
arguments, and raw result.

The assistant does not modify the data or execute generated Python
or SQL. Unsupported questions receive an explanation.

The question box becomes disabled after 15 questions in a session.
Changing the uploaded data or filters clears previous answers, while
retaining the session question count.

A live language-model connection has not yet been implemented.
API access and availability have not yet been evaluated.

## Validation

The original uploaded data produced $42,174,440.00 in total revenue,
matching Power BI exactly.

Both channel totals, all five yearly totals, and Website Beans revenue
matched Power BI exactly. All 12 monthly percentages matched to the
two decimal places displayed.

A separate calculation summed Sales.csv directly without joins.

The modified-data test increased one revenue value by exactly $1,000.
The dashboard and assistant updated appropriately without code changes
or a restart. The original data was restored afterward.

These figures document the original-data tests. They are not hardcoded
analytical answers in the application.

See validation.md and agent_tests.md for procedures, results, and
remaining checks.

## Run locally

Install the packages listed in requirements.txt:

python3 -m pip install -r requirements.txt

Start the application:

python3 -m streamlit run streamlit_app.py

## Run automated tests

python3 test_analytics.py

python3 test_agent.py

The tests use small made-up datasets with answers that can be checked
by hand.

## Main files

| File | Purpose |
|---|---|
| streamlit_app.py | Uploads, profiles, connections, filters, and charts |
| analytics.py | Three approved analytical functions |
| agent.py | Approved-tool dispatcher and rules-based question handling |
| assistant_ui.py | Chat interface, history, session limit, and visible logs |
| test_analytics.py | Calculation and data-handling tests |
| test_agent.py | Dispatcher and question-handling tests |
| validation.md | Power BI comparisons and dashboard modified-data test |
| agent_tests.md | Assistant testing evidence and remaining checks |
| requirements.txt | Python packages needed by the hosted app |

streamlit_app.py is the active application entry point.
The older app.py is not used by the hosted app.

## Limitations

- Revenue is not profit; costs and expenses are not supplied.
- Correlation would not establish causation.
- Missing survey responses limit satisfaction analysis.
- The assistant supports a fixed question list.
- Session uploads must be supplied again in a fresh session.
- Further updated-data and edge-case checks may be needed for real use.

## Team contributions

The final contribution statement, teammate commits, reflection, and
individual defense preparation remain to be completed.