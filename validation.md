# E-Presso Validation Notes

## Total revenue comparison

| Measure | Power BI | Streamlit | Result |
|---|---:|---:|---|
| Total revenue, 2025–2029 | $42,174,440.00 | $42,174,440.00 | Exact match |
| Website revenue, all years | $27,218,880.00 | $27,218,880.00 | Exact match |

Streamlit brick-and-mortar revenue is $14,955,560.00.
An exact Power BI comparison for this combined amount is still needed.

Exact annual comparisons, the complete monthly comparison, and an
additional business measure still need to be documented.

## Independent calculation check

A separate Python calculation read the exported Sales.csv directly,
without joining other tables, and summed its Revenue column.

Result: $42,174,440.00, matching Streamlit and Power BI.

Reproduce the check from the project folder with:

python3 -c 'import pandas as pd; print(pd.read_csv("Sales.csv")["Revenue"].sum())'

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

Product names are not unique: three products are called Base Model.
Product ID is used to identify products.

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

- Power BI exact revenue screenshot.
- Table connection check screenshot.
- Screenshots of the modified total, filtered result, annual chart,
  unaffected year, and restored total where available.