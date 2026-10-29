# E-Presso Validation Notes

Validation performed October 28–29, 2026.

## Power BI and Streamlit comparisons

Both applications used the original E-Presso data.
All years, stores, and categories were included unless stated otherwise.

| Measure | Power BI | Streamlit | Result |
|---|---:|---:|---|
| Total revenue, 2025–2029 | $42,174,440.00 | $42,174,440.00 | Exact match |
| Website revenue | $27,218,880.00 | $27,218,880.00 | Exact match |
| Brick & Mortar revenue | $14,955,560.00 | $14,955,560.00 | Exact match |
| 2025 revenue | $7,181,750.00 | $7,181,750.00 | Exact match |
| 2026 revenue | $8,016,950.00 | $8,016,950.00 | Exact match |
| 2027 revenue | $8,824,720.00 | $8,824,720.00 | Exact match |
| 2028 revenue | $8,969,470.00 | $8,969,470.00 | Exact match |
| 2029 revenue | $9,181,550.00 | $9,181,550.00 | Exact match |
| Additional measure: Website Beans revenue, all years | $3,645,210.00 | $3,645,210.00 | Exact match |

Exact Power BI values were checked using table totals and chart tooltips.
No numerical discrepancies were found in these comparisons.

## Monthly revenue patterns

Scope: all years, store types, and categories.

Streamlit calculates each calendar month's revenue across all five years
divided by total revenue across those years. This is a combined revenue
share, not an average of annual percentages.

| Month | Power BI | Streamlit | Result |
|---|---:|---:|---|
| January | 7.74% | 7.74% | Match |
| February | 3.83% | 3.83% | Match |
| March | 4.44% | 4.44% | Match |
| April | 5.15% | 5.15% | Match |
| May | 5.72% | 5.72% | Match |
| June | 6.50% | 6.50% | Match |
| July | 6.42% | 6.42% | Match |
| August | 6.45% | 6.45% | Match |
| September | 7.11% | 7.11% | Match |
| October | 8.31% | 8.31% | Match |
| November | 12.71% | 12.71% | Match |
| December | 25.61% | 25.61% | Match |

All monthly percentages agree to the two decimal places displayed.
The Power BI visual is titled “Percent of Annual Revenue per Month,”
but this comparison used its all-years view. Agreement in that view
does not verify the calculation under every possible filter.

## Independent calculation check

A separate Python calculation read Sales.csv directly, without joining
other tables, and summed its Revenue column.

Result: $42,174,440.00, matching Streamlit and Power BI.

To reproduce, run this command from the project folder:

python3 -c 'import pandas as pd; print(pd.read_csv("Sales.csv")["Revenue"].sum())'

The Sales file contains 25,200 rows: 21 store/channel records ×
20 products × 60 months. No store–product–month combination repeats.

## Data quality

| Table | Rows | Duplicate IDs | Missing values |
|---|---:|---:|---|
| Stores | 21 | 0 | City, State, and PostalCode each have 1 blank |
| Survey Results | 105 | 0 | Satisfaction and Interest each have 5 blanks |
| Sales | 25,200 | 0 | None |
| Products | 20 | 0 | None |
| Categories | 5 | 0 | None |

The blank location fields belong to the Website record, SH00.
Missing survey responses remain blank; they are not treated as zero.
The original Sales file has no missing or unreadable dates.

Three products share the name Base Model. Product ID, rather than
product name, identifies each product.

## Table connection checks

Sales connects to Stores using Store ID → ID.
Sales connects to Products using Product ID.
Sales connects to Categories using Category ID.

Each connection uses a left join with a many-to-one check.

| Connection | Rows before | Rows after | Revenue before | Revenue after | Unmatched sales |
|---|---:|---:|---:|---:|---:|
| Stores | 25,200 | 25,200 | $42,174,440.00 | $42,174,440.00 | 0 |
| Products | 25,200 | 25,200 | $42,174,440.00 | $42,174,440.00 | 0 |
| Categories | 25,200 | 25,200 | $42,174,440.00 | $42,174,440.00 | 0 |

No sales rows were added or removed, and revenue did not change.
Survey Results has not been joined to Sales.

## Filter checks using original data

| Year | Store type | Category | Expected revenue | Actual revenue |
|---|---|---|---:|---:|
| 2025 | All | All | $7,181,750.00 | $7,181,750.00 |
| All | Website | All | $27,218,880.00 | $27,218,880.00 |
| 2025 | Website | All | $3,160,230.00 | $3,160,230.00 |
| All | All | Beans | $5,672,720.00 | $5,672,720.00 |
| All | All | Espresso Machines | $27,093,220.00 | $27,093,220.00 |
| All | Website | Beans | $3,645,210.00 | $3,645,210.00 |

The year, store type, and category filters were also checked in the
hosted application.

## $1,000 modified-data test

Test performed October 29, 2026, in the hosted Streamlit app.

A separate copy named Sales_test.csv was created.
Only the first sales row's Revenue value was changed.

| Item | Value |
|---|---|
| Original source | Sales.csv |
| Modified copy | Sales_test.csv |
| CSV data row / Excel cell | First data row / G2 |
| Sales ID | S0020250101 |
| Date | January 31, 2025 |
| Store ID | SH00 |
| Channel | Website |
| Product ID | P01 |
| Category | C1 — Beans |
| Original revenue | $6,780.00 |
| Modified revenue | $7,780.00 |
| Increase | Exactly $1,000.00 |

Before uploading, we predicted that total revenue would rise by $1,000
and that the increase would belong to 2025, Website, Beans, and January.

| Check | Expected | Actual | Result |
|---|---:|---:|---|
| All sales after modification | $42,175,440.00 | $42,175,440.00 | Pass |
| 2025 Website, all categories | $3,161,230.00 | $3,161,230.00 | Pass |
| 2026, all channels and categories | $8,016,950.00 | $8,016,950.00 | Unchanged as expected |
| 2025 point on annual chart | $7,182,750.00 | $7,182,750.00 | Pass |
| Total after restoring Sales.csv | $42,174,440.00 | $42,174,440.00 | Pass |

The modified copy was uploaded without code changes or an app restart.
The original Sales.csv was then uploaded again and its total verified.

The Beans-specific and January-specific changes have not yet been
separately verified in this test.

The analytical assistant has not been built yet. Its before-and-after
updated-data test remains outstanding.

## Evidence to retain

- Power BI revenue totals and tooltip screenshots.
- Streamlit table connection checks.
- Monthly comparison screenshots.
- Modified-data test screenshots where available.
- Assistant tool-call logs and test evidence once implemented.

## Analytical limitations

Revenue is not profit. Cost and expense data would be needed to
evaluate profitability or justify closing a store.

A relationship between satisfaction and revenue would not establish
causation. Missing survey responses also limit interpretation.