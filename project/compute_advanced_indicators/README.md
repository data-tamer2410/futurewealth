# Bank Financial Risk Analysis Tool

## Overview

This script calculates **14 key financial indicators** for banks and automatically detects risks if the metrics breach predefined thresholds.
For each indicator, if there is not enough data for a direct calculation, an **alternative proxy function** is used.

## Calculated Indicators

1. **Cash Shortage Proxy** – liquidity shortfall.
2. **Core Deposit Mix Ratio** – share of retail deposits.
3. **Duration Gap** – interest rate sensitivity.
4. **FX Mismatch** – foreign exchange gap.
5. **Loan to Deposit Ratio** – loans-to-deposits ratio.
6. **Net Stable Funding Ratio (NSFR)** – funding stability.
7. **OCI-Based Unrealized Losses to Assets** – unrealized losses to assets.
8. **OCI-Based Unrealized Losses to Equity** – unrealized losses to equity.
9. **Core Deposit Stability** – stability of core deposits.
10. **Cost of Risk** – credit loss ratio.
11. **Derivatives Exposure** – exposure to derivatives.
12. **Fair Value Gains/Losses** – gains/losses at fair value.
13. **Non-Recurring Income Ratio** – share of one-off income.
14. **RWA to Assets** – share of risk-weighted assets in total assets.

> For all possible indicators, **proxy methods** are implemented and used when the primary data is unavailable.

---

## Command-Line Interface

### Example usage:

```bash
python compute_advanced_indicators.py \
    --input_dir path/to/bank/data \
    --output_dir path/to/results \
    --date_col_name "Date" \
    --bank_name_col "Bank Name"
```

### Parameters:

* `--input_dir` (**required**) – directory containing bank data files (`.csv` or `.xlsx`).
* `--output_dir` (**required**) – directory where results will be saved.
* `--date_col_name` (optional) – name of the date column.
* `--bank_name_col` (optional) – name of the bank name column.

---

## Output

1. **Individual JSON reports** for each bank:

   * Meta information (bank name, period, source file)
   * Indicators
   * Quality scores
   * Risk flags

2. **Consolidated table** in `.xlsx` or `.csv` with all banks, including indicator quality scores and flags.

3. **Text summary** (`summary.txt`) and a color-coded console table showing **Top 5 riskiest banks**.

---

## Risk Detection Logic

* Each indicator has a **threshold value** and a risk direction (`>` or `<`).
* If the value breaches the threshold in the “bad” direction – `True` (risk) is set.
* If no data is available – `None`.
