E-Presso Business Intelligence App
An interactive Streamlit dashboard for exploring fictional E-Presso revenue, checking data quality, and asking analytical questions.
Open the hosted app
Open E-Presso

The hosted dashboard has been tested without a login. Allow it time to wake if sleeping. The latest local Gemini and causation-response changes still require upload and verification on the hosted app.
Features
- Upload Stores, Survey Results, Sales, Products, and Categories.
- Display table grains, row counts, duplicate IDs, and missing values.
- Verify Sales-to-lookup joins with row counts, revenue, and unmatched records.
- Filter revenue by year, store type, and category.
- Explore revenue by store type, year, and calendar month.
- Use Gemini to select approved analytical tools and explain their results.
- Display exact Python findings, scope, and tool-call logs.
- Fall back to labeled rules-based answers when Gemini fails.
- Limit assistant use to 15 questions per session.
Data uploads
Upload	Source	Reading method
Stores	Supplied Stores CSV	Skip first title line; preserve text fields
Survey	Supplied Survey workbook	Survey Results sheet; skip first two lines
Sales	Sales.csv	First row contains column names
Products	Products.csv	First row contains column names
Categories	Categories.csv	First row contains column names


Sales, Products, and Categories were exported from Access as comma-delimited files with field names. Stores, Sales, Products, and Categories are required for the dashboard. Survey is profiled separately.

Uploads are session data and do not overwrite source files. A fresh browser session may require uploading again. Updated files must retain the expected sheets, columns, and types; values and rows may change. Filter lists come from loaded data.
Table grains and joins
Table	One row represents	Key
Stores	One store or website channel	ID
Survey Results	One store's survey results in one year	Survey ID
Sales	One product's revenue at one store/channel for one month	Sales ID
Products	One product	Product ID
Categories	One product category	Category ID


Sales left-joins Stores through Store ID → ID, Products through Product ID, and Categories through Category ID. Lookup keys must be unique and nonblank. Join checks report rows, revenue, and unmatched sales. Product names are not unique.

Survey is not joined to Sales. Joining only on Store ID could duplicate sales across survey years.
Calculation definitions
Revenue is the sum of loaded Sales.Revenue within explicit filters. Profiles and join checks describe full uploads; the revenue metric, charts, tables, and assistant calculations use the selected scope.

Yearly revenue groups readable dates by calendar year. Monthly share is a calendar month's selected revenue divided by total selected dated revenue. Multiple years are combined, not averaged as yearly percentages.

Unreadable dates are reported and excluded from date-based calculations. Missing or unreadable revenue blocks dashboard calculations. Unmatched lookup records remain in left-joined data; missing channel/category labels appear as Unknown.
Assistant behavior
Check Use Gemini to enable the live connection. The tested model is gemini-3.1-flash-lite using the Google Gen AI SDK. Uncheck it to use the rules-based question router.

Example questions:
- Compare revenue by store type
- Which store type has the most revenue?
- Show revenue by year
- Show monthly revenue shares
- Does revenue tell us profit?
- Does higher customer satisfaction cause higher revenue?
Set filters on the dashboard first. The Gemini route validates tool arguments against the dashboard scope and the dispatcher validates parameter types and loaded values. It does not change filters based on question text. The rules-based route recognizes its supported wording.

Approved tools:
- get_revenue_by_channel
- get_revenue_by_year
- get_monthly_revenue_share
Python calculates and formats numerical findings. Each tool returns tool, value, definition, scope, rows_used, and caveats, or an error. Answers show Findings, Interpretation, Next steps, and the function/arguments/raw result log.

Gemini explains results but cannot execute arbitrary Python or SQL or modify source data. Output checks reject certain known misleading explanations; they do not guarantee every generated sentence is correct. Review interpretations against tool evidence.

The supported satisfaction-causation question receives an explicit rules-based limitation response even when Gemini is selected. It explains association versus causation and runs no analytical tool or API request. It does not claim to have analyzed survey-sales relationships.

Connection errors, quota errors, or invalid explanations produce labeled fallbacks. Live calls have experienced server errors and timeouts. Each request has a 60-second timeout setting; a successful question normally uses two model requests. Response time is not guaranteed.

Changing uploads or filters clears displayed answers while retaining the session question count. The chat input is disabled after 15 questions. This is a session limit, not an account-wide spending control.
Run locally
python3 -m pip install -r requirements.txt
python3 -m streamlit run streamlit_app.py
Open the Local URL printed in the terminal; the port can vary.

For Gemini, create .streamlit/secrets.toml privately:
GEMINI_API_KEY = "YOUR_PRIVATE_KEY"
Add .streamlit/secrets.toml to .gitignore. Never commit or manually upload this file. For hosting, enter the key in Streamlit Community Cloud's Secrets settings. Use only fictional or instructor-approved data with external providers.

Required dependencies:
streamlit>=1.40
pandas>=2.0
plotly>=5.20
openpyxl>=3.1
google-genai==2.34.0
Testing and validation
python3 test_analytics.py
python3 test_agent.py
These tests use small made-up datasets with hand-checkable answers. Earlier versions passed; rerun after the latest changes before final submission.

Original total revenue was $42,174,440.00. Channel totals, five yearly totals, Website Beans revenue, and monthly shares matched Power BI. A separate script summed Sales.csv directly without joins.

A $1,000 change in Sales_test.csv updated the dashboard and assistant calculations without code edits or restarting. The original data was restored during development. Numerical screenshots have been collected by the student.

See validation.md and agent_tests.md for exact results, test scope, revisions, and outstanding checks. Recorded expected values are test evidence, not hardcoded application answers.
Main files
File	Purpose
streamlit_app.py	Active entry point: uploads, profiles, joins, filters, charts
analytics.py	Approved analytical functions
agent.py	Dispatcher, rules-based answers, causation limitation
gemini_agent.py	Live tool selection, explanation, validation, fallback
assistant_ui.py	Chat, history, mode selection, session limit, logs
test_analytics.py	Calculation/data-handling tests
test_agent.py	Dispatcher/question-handling tests
test_connection.py	Manual Gemini connection diagnostic
validation.md	Reconciliation, data quality, modified-data evidence
agent_tests.md	Assistant test results and revisions
requirements.txt	Hosted/local dependencies


The older app.py is not the active hosted entry point.
Limitations and completion status
Revenue cannot establish profit. The tools do not estimate causation, analyze satisfaction relationships, or forecast performance. Missing survey responses limit interpretation. New sessions may require reuploading files. Model availability varies and generated explanations require review.

Before final submission: deploy the latest changes, configure hosted Secrets, rerun automated checks, verify the hosted app, complete the controlled profit-fallback retest, and finish the reflection and contribution statement. Every teammate must have meaningful commits and be able to explain calculations and limitations.