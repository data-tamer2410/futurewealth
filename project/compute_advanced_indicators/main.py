"""Compute advanced financial indicators for banks."""

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from rich.console import Console
from rich.progress import track
import pandas as pd
import argparse
from project.compute_advanced_indicators.utils import (
    save_json,
    read_bank_data,
    save_bank_indicators_to_table,
    detect_flags,
    create_summary,
)
from project.compute_advanced_indicators.indicators.cash_shortage_proxy import (
    compute_cash_shortage_proxy,
)
from project.compute_advanced_indicators.indicators.core_deposit_mix_ratio import (
    compute_core_deposit_mix_ratio,
)
from project.compute_advanced_indicators.indicators.duration_gap import (
    compute_duration_gap,
)
from project.compute_advanced_indicators.indicators.fx_mismatch import (
    compute_fx_mismatch,
)
from project.compute_advanced_indicators.indicators.loan2deposit_ratio import (
    compute_loan_to_deposit_ratio,
)
from project.compute_advanced_indicators.indicators.net_stable_funding_ratio import (
    compute_net_stable_funding_ratio,
)
from project.compute_advanced_indicators.indicators.oci_based_unrealized_losses import (
    compute_oci_based_unrealized_losses_to_assets,
    compute_oci_based_unrealized_losses_to_equity,
)

console = Console()


# === Main Function to Compute Indicators ===
def compute_advanced_indicators(
    df: pd.DataFrame,
    source_file: str = None,
    date_col_name: str = None,
    bank_name_col: str = None,
) -> dict:
    """
    Compute financial indicators and return structured JSON for a bank.
    Automatically detects period based on available date columns or index.
    """
    indicators = {}
    quality = {}

    # Compute indicators

    # 1. Cash Shortage Proxy
    indicator_data = compute_cash_shortage_proxy(df)
    indicators["Cash_Shortage_Proxy"] = indicator_data["indicator"]
    quality["Cash_Shortage_Proxy"] = indicator_data["quality"]

    # 2. Core Deposit Mix Ratio
    indicator_data = compute_core_deposit_mix_ratio(df)
    indicators["Core_Deposit_Mix_Ratio"] = indicator_data["indicator"]
    quality["Core_Deposit_Mix_Ratio"] = indicator_data["quality"]

    # 3. Duration Gap
    indicator_data = compute_duration_gap(df)
    indicators["Duration_Gap"] = indicator_data["indicator"]
    quality["Duration_Gap"] = indicator_data["quality"]

    # 4. FX Mismatch
    indicator_data = compute_fx_mismatch(df)
    indicators["FX_Mismatch"] = indicator_data["indicator"]
    quality["FX_Mismatch"] = indicator_data["quality"]

    # 5. Loan to Deposit Ratio
    indicator_data = compute_loan_to_deposit_ratio(df)
    indicators["Loan_to_Deposit_Ratio"] = indicator_data["indicator"]
    quality["Loan_to_Deposit_Ratio"] = indicator_data["quality"]

    # 6. Net Stable Funding Ratio
    indicator_data = compute_net_stable_funding_ratio(df)
    indicators["Net_Stable_Funding_Ratio"] = indicator_data["indicator"]
    quality["Net_Stable_Funding_Ratio"] = indicator_data["quality"]

    # 7. OCI Based Unrealized Losses
    oci_unrealized_losses_assets = compute_oci_based_unrealized_losses_to_assets(df)
    indicators["OCI_Based_Unrealized_Losses_to_Assets"] = oci_unrealized_losses_assets[
        "indicator"
    ]
    quality["OCI_Based_Unrealized_Losses_to_Assets"] = oci_unrealized_losses_assets[
        "quality"
    ]

    oci_unrealized_losses_equity = compute_oci_based_unrealized_losses_to_equity(df)
    indicators["OCI_Based_Unrealized_Losses_to_Equity"] = oci_unrealized_losses_equity[
        "indicator"
    ]
    quality["OCI_Based_Unrealized_Losses_to_Equity"] = oci_unrealized_losses_equity[
        "quality"
    ]

    indicators = {k: round(v, 2) for k, v in indicators.items()}

    # Flags detection
    flags = detect_flags(indicators)

    # Period detection
    if date_col_name is not None and date_col_name in df.columns:
        df[date_col_name] = pd.to_datetime(df[date_col_name])
        min_date = df[date_col_name].min()
        max_date = df[date_col_name].max()
        period = (
            f"{min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}"
            if pd.notna(min_date) and pd.notna(max_date)
            else None
        )
    else:
        period = None

    # Get the bank name
    if bank_name_col is not None:
        bank_name = df.iloc[0][bank_name_col]
    else:
        bank_name = None

    return {
        "meta": {
            "bank_name": bank_name,
            "period": period,
            "source_file": source_file,
        },
        "indicators": indicators,
        "quality": quality,
        "flags": flags,
    }


def main(
    input_dir: str,
    output_dir: str,
    bank_indicators_table: str = "bank_indicators_table.xlsx",
    date_col_name: str = None,
    bank_name_col: str = None,
):

    os.makedirs(output_dir, exist_ok=True)

    result_bank_indicators = []
    for file in track(os.listdir(input_dir), description="Processing bank data..."):
        df = read_bank_data(os.path.join(input_dir, file))
        bank_indicators = compute_advanced_indicators(
            df,
            source_file=file,
            date_col_name=date_col_name,
            bank_name_col=bank_name_col,
        )
        result_bank_indicators.append(bank_indicators)

        file = file.replace(".csv", "").replace(".xlsx", "")
        output_file = os.path.join(output_dir, f"{file}_indicators.json")
        save_json(bank_indicators, output_file)

    save_bank_indicators_to_table(
        result_bank_indicators, f"{output_dir}/{bank_indicators_table}"
    )
    create_summary(result_bank_indicators, output_dir, console)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Compute advanced financial indicators for banks."
    )
    parser.add_argument(
        "--input_dir",
        required=True,
        help="Path to the input directory containing bank data files.",
    )
    parser.add_argument(
        "--output_dir",
        required=True,
        help="Path to the output directory to save results.",
    )
    parser.add_argument(
        "--date_col_name", help="Name of the date column in the bank data files."
    )
    parser.add_argument(
        "--bank_name_col",
        help="Name of the column containing bank names in the data files.",
    )

    args = parser.parse_args()

    main(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        date_col_name=args.date_col_name,
        bank_name_col=args.bank_name_col,
    )
