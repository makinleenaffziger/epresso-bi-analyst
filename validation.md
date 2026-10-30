E-Presso Validation Notes
Dashboard validation: October 28–29, 2026. Assistant testing and revisions continued October 30, 2026.
Power BI and Streamlit comparisons
Original data; all years, stores, and categories unless stated otherwise.
Measure	Power BI	Streamlit	Result
Total revenue, 2025–2029	$42,174,440.00	$42,174,440.00	Exact match
Website revenue	$27,218,880.00	$27,218,880.00	Exact match
Brick & Mortar revenue	$14,955,560.00	$14,955,560.00	Exact match
2025 revenue	$7,181,750.00	$7,181,750.00	Exact match
2026 revenue	$8,016,950.00	$8,016,950.00	Exact match
2027 revenue	$8,824,720.00	$8,824,720.00	Exact match
2028 revenue	$8,969,470.00	$8,969,470.00	Exact match
2029 revenue	$9,181,550.00	$9,181,550.00	Exact match
Additional measure: Website Beans, all years	$3,645,210.00	$3,645,210.00	Exact match


Exact Power BI values were checked using tables and chart tooltips. No numerical discrepancies were found in these comparisons.
Monthly revenue patterns
Scope: all years, store types, and categories. Each calendar month's combined revenue is divided by total dated revenue across the selected years. This is not an average of annual percentages.
Month	Power BI	Streamlit	Result
January	7.74%	7.74%	Match
February	3.83%	3.83%	Match
March	4.44%	4.44%	Match
April	5.15%	5.15%	Match
May	5.72%	5.72%	Match
June	6.50%	6.50%	Match
July	6.42%	6.42%	Match
August	6.45%	6.45%	Match
September	7.11%	7.11%	Match
October	8.31%	8.31%	Match
November	12.71%	12.71%	Match
December	25.61%	25.61%	Match


All percentages agree to the two decimal places displayed. The Power BI visual is titled “Percent of Annual Revenue per Month,” but this comparison used its all-years view. Agreement does not verify every possible filter combination.
Independent calculation
A separate Python calculation read Sales.csv directly, without joins, and summed Revenue. Result: $42,174,440.00.

Run from the project folder:
python3 -c 'import pandas as pd; print(pd.read_csv("Sales.csv")["Revenue"].sum())'
Sales contains 25,200 rows: 21 store/channel records × 20 products × 60 months. No store–product–month combination repeats.
Data quality
Table	Rows	Duplicate IDs	Missing values
Stores	21	0	City, State, PostalCode: one blank each
Survey Results	105	0	Satisfaction and Interest: five blanks each
Sales	25,200	0	None
Products	20	0	None
Categories	5	0	None


The blank location fields belong to Website record SH00. Missing survey values remain blank, not zero. Original Sales dates are readable. Three products share the name Base Model; Product ID identifies products.
Table connection checks
Sales uses left, many-to-one joins to Stores (Store ID → ID), Products (Product ID), and Categories (Category ID).
Connection	Rows before	Rows after	Revenue before	Revenue after	Unmatched sales
Stores	25,200	25,200	$42,174,440.00	$42,174,440.00	0
Products	25,200	25,200	$42,174,440.00	$42,174,440.00	0
Categories	25,200	25,200	$42,174,440.00	$42,174,440.00	0


No sales rows or revenue were added or removed. Survey Results is not joined to Sales.
Original-data filter checks
Year	Store type	Category	Expected	Actual
2025	All	All	$7,181,750.00	$7,181,750.00
All	Website	All	$27,218,880.00	$27,218,880.00
2025	Website	All	$3,160,230.00	$3,160,230.00
All	All	Beans	$5,672,720.00	$5,672,720.00
All	All	Espresso Machines	$27,093,220.00	$27,093,220.00
All	Website	Beans	$3,645,210.00	$3,645,210.00


Year, store-type, and category filters were also checked in the hosted dashboard.
$1,000 modified-data test
The hosted dashboard test was performed October 29, 2026. A separate Sales_test.csv changed only the first sales row's Revenue.
Item	Value
Original / modified file	Sales.csv / Sales_test.csv
Row / Excel cell	First data row / G2
Sales ID	S0020250101
Date	January 31, 2025
Store / channel	SH00 / Website
Product / category	P01 / C1 — Beans
Original revenue	$6,780.00
Modified revenue	$7,780.00
Increase	Exactly $1,000.00


Before upload, the prediction was a $1,000 increase belonging to 2025, Website, Beans, and January, with other years and the physical channel unchanged.
Dashboard check	Expected	Actual	Result
Modified total	$42,175,440.00	$42,175,440.00	Pass
Modified 2025 Website	$3,161,230.00	$3,161,230.00	Pass
2026, all channels/categories	$8,016,950.00	$8,016,950.00	Unchanged
2025 annual chart point	$7,182,750.00	$7,182,750.00	Pass
Restored total	$42,174,440.00	$42,174,440.00	Pass


No code edits or restart were used. Original Sales.csv was restored and its total verified during testing. Beans-specific and January-specific modified values have not been separately verified.
Assistant updated-data checks
The assistant has now been implemented. Channel revenue was tested before and after the same modified upload, without code edits or restart.
Assistant check	Original	Modified
Website, all years	$27,218,880.00	$27,219,880.00
Brick & Mortar, all years	$14,955,560.00	$14,955,560.00
Website, 2025	$3,160,230.00	$3,161,230.00


These amounts were observed during development. The student reports collecting the required numerical answer and tool-log screenshots, including updated-data evidence. See agent_tests.md for the test table, interpretation fixes, fallback behavior, and limitations. A fallback numerical answer is evidence of Python calculation behavior, not a successful live Gemini call.
Evidence and remaining verification
Retain the numerical assistant answer and tool-log screenshots with the submission. The validation tables and reproducible independent command provide the written calculation evidence.

The latest Gemini and causation-response changes require deployment and a fresh hosted-app check. A controlled timeout retest of the profit-question fallback remains outstanding.
Analytical limitations
Revenue is not profit. Costs and expenses are required to assess profitability. Association between satisfaction and revenue would not prove causation. Missing survey responses limit interpretation, and the current revenue tools do not analyze the survey-sales relationship.