import pandas as pd
import json
import os
from rich.table import Table
from rich import box
from rich.console import Console

THRESHOLDS = {
    # Liquidity: if > 1.5, the bank has issued more loans than it has collected in deposits
    "Loan_to_Deposit_Ratio": {"threshold": 1.5, "sign": ">"},
    # Unrealized losses to assets: below -10% — significant risk
    "OCI_Based_Unrealized_Losses_to_Assets": {"threshold": -0.10, "sign": "<"},
    # Unrealized losses to equity: below -30% — critical
    "OCI_Based_Unrealized_Losses_to_Equity": {"threshold": -0.30, "sign": "<"},
    # NSFR: < 1.0 means stable funding covers less than 100% of assets
    "Net_Stable_Funding_Ratio": {"threshold": 1.0, "sign": "<"},
    # FX mismatch > 20% of equity — elevated risk
    "FX_Mismatch": {"threshold": 0.20, "sign": ">"},
    # Duration Gap: more than 3 years — high interest rate sensitivity risk
    "Duration_Gap": {"threshold": 3.0, "sign": ">"},
    # Cash + interbank assets / short-term liabilities > 50% — liquidity shortage
    "Cash_Shortage_Proxy": {"threshold": 0.5, "sign": ">"},
    # Share of retail deposits < 20% — unstable funding base
    "Core_Deposit_Mix_Ratio": {"threshold": 0.2, "sign": "<"},
    # Core deposit stability < 50% — potentially risky deposit structure
    "Core_Deposit_Stability": {"threshold": 0.5, "sign": "<"},
    # Cost of risk > 2% — high level of credit losses
    "Cost_of_Risk": {"threshold": 0.02, "sign": ">"},
    # Derivatives exposure > 10% of assets — elevated market risk
    "Derivatives_Exposure": {"threshold": 0.10, "sign": ">"},
    # Fair value gains/losses < -5% of income — negative signal
    "Fair_Value_Gains_Losses": {"threshold": -0.05, "sign": "<"},
    # Share of non-recurring income > 10% — high dependency on unstable sources
    "Non_Recurring_Income_Ratio": {"threshold": 0.10, "sign": ">"},
    # RWA / Total Assets > 80% — high-risk asset profile
    "RWA_to_Assets": {"threshold": 0.80, "sign": ">"},
}


def detect_flags(indicators: dict) -> dict:
    """
    Detect flags based on computed indicators and predefined thresholds.

    True is Bad, False is Good.
    """
    flags = {}
    for key, value in indicators.items():
        threshold = THRESHOLDS[key]["threshold"]
        sign = THRESHOLDS[key]["sign"]
        if value is None or pd.isna(value):
            flags[key] = None
            continue

        if sign == "<":
            # Explicitly convert to built-in Python bool to avoid issues with NumPy types during JSON serialization
            flags[key] = True if value < threshold else False
        else:
            flags[key] = True if value > threshold else False

    return flags


def create_summary(
    result_bank_indicators: pd.DataFrame, output_dir: str, console: Console
) -> None:
    """Create a summary of the top 5 banks with the most risk based on threshold breaches."""
    summary_rows = []
    for bank in result_bank_indicators:
        flags = bank["flags"]
        indicators = bank["indicators"]
        bank_name = bank["meta"].get("bank_name", "Unknown Bank")
        not_none_flags = {k: v for k, v in flags.items() if v is not None}
        count_flags = sum(not_none_flags.values())
        flagged = ", ".join(
            [f"{k} ({indicators[k]})" for k, v in not_none_flags.items() if v]
        )
        summary_rows.append((bank_name, count_flags, flagged))

    summary_df = pd.DataFrame(
        summary_rows, columns=["bank_name", "flag_count", "flagged_indicators"]
    )
    summary_df = summary_df.sort_values("flag_count", ascending=False).head(5)

    summary_file = os.path.join(output_dir, "summary.txt")
    with open(summary_file, "w") as f:
        f.write("Top 5 Most Risky Banks Based on Threshold Breaches:\n\n")
        for _, row in summary_df.iterrows():
            f.write(
                f"{row['bank_name']} — Flags: {row['flag_count']} | Indicators: {row['flagged_indicators']}\n"
            )

    table = Table(
        title="Top 5 Most Risky Banks",
        title_style="bold magenta",
        box=box.SIMPLE_HEAVY,
    )
    table.add_column("Bank Name", style="cyan")
    table.add_column("Flags Count", justify="right", style="red")
    table.add_column("Flagged Indicators", style="yellow")

    for _, row in summary_df.iterrows():
        table.add_row(
            row["bank_name"], str(row["flag_count"]), row["flagged_indicators"]
        )

    console.print("\n\n")
    console.print(table)


def cols_exist_and_not_na(df: pd.DataFrame, cols: list[str]) -> bool:
    """Helper function to check if all columns exist and are not all NaN"""
    return all(col in df.columns and not df[col].isna().all() for col in cols)


def save_json(data: dict, filename: str):
    """Save the computed indicators to a JSON file."""

    for key, value in data["indicators_full"].items():
        if value is not None:
            value = [None if pd.isna(v) else v for v in value.tolist()]
            data["indicators_full"][key] = value

    for key, item in data["indicators"].items():
        if pd.isna(item):
            data["indicators"][key] = None

    with open(filename, "w") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def read_bank_data(file_path: str) -> pd.DataFrame:
    """Read bank data from a CSV or Excel file."""
    if file_path.endswith(".csv"):
        return pd.read_csv(file_path)
    elif file_path.endswith(".xlsx"):
        return pd.read_excel(file_path)
    else:
        raise ValueError("Unsupported file format. Please provide a CSV or Excel file.")


def save_bank_indicators_to_table(
    indicators: list[dict],
    output_file: str,
):
    """Save the computed indicators to a table format (CSV or Excel)."""

    flattened_data = []
    for indicator in indicators:
        row = {}

        row.update(indicator["meta"])
        row.update(indicator["indicators"])
        row.update({f"{k}_quality": i for k, i in indicator["quality"].items()})
        row.update({f"{k}_flag": i for k, i in indicator["flags"].items()})
        flattened_data.append(row)

    df = pd.DataFrame(flattened_data)

    if output_file.endswith(".csv"):
        df.to_csv(output_file, index=False)
    elif output_file.endswith(".xlsx"):
        df.to_excel(output_file, index=False)
    else:
        raise ValueError(
            "Unsupported output file format. Please provide a CSV or Excel file."
        )
