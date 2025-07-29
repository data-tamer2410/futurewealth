"""Compute advanced financial indicators for banks."""

import pandas as pd
import numpy as np
import json


# === Proxy Functions ===
def proxy_duration_gap(df: pd.DataFrame) -> float:
    """Calculate Duration Gap using available data."""
    short_term = df.get("Deposits made by the Central Bank $m", 0) + df.get(
        "Deposits by Banks $m", 0
    )
    long_term = df.get("Total Senior Debt $m", 0) + df.get(
        "Subordinated Liabilities $m", 0
    )
    total_liab = df.get("Total Liabilities $m", pd.Series([np.nan] * len(df))).replace(
        0, np.nan
    )
    return ((long_term - short_term) / total_liab).mean()


def proxy_fx_mismatch(df: pd.DataFrame) -> float:
    """Calculate FX Mismatch using FX Assets and Liabilities."""
    fx_assets = df.get("Derivatives (Assets) $m", pd.Series([0] * len(df)))
    fx_liab = df.get("Derivatives (Liabilities) $m", pd.Series([0] * len(df)))
    equity = df.get("Total Equity $m", pd.Series([np.nan] * len(df))).replace(0, np.nan)
    return ((fx_assets - fx_liab).abs() / equity).mean()


def proxy_loan_to_deposit(df: pd.DataFrame) -> float:
    """Calculate Loan-to-Deposit Ratio using Gross Total Loans and Deposits."""
    loans = df.get("Gross Total Loans $m", pd.Series([np.nan] * len(df)))
    deposits = df.get("Gross Total Deposits $m", pd.Series([np.nan] * len(df))).replace(
        0, np.nan
    )
    return (loans / deposits).mean()


def proxy_cash_shortage(df: pd.DataFrame) -> float:
    """Calculate Cash Shortage Ratio using Cash and Interbank Assets."""
    cash = df.get("Cash and Balance at Central Bank(s) $m", pd.Series([0] * len(df)))
    interbank = df.get(
        "Loans and Advances to Financial Institutions $m", pd.Series([0] * len(df))
    )
    short_term_liab = df.get("Deposits made by the Central Bank $m", 0) + df.get(
        "Deposits by Banks $m", 0
    )
    short_term_liab = short_term_liab.replace(0, np.nan)
    return ((cash + interbank) / short_term_liab).mean()


def proxy_core_deposit_mix(df: pd.DataFrame) -> float:
    """Calculate Core Deposit Mix Ratio using Retail Customer Deposits and Gross Total Deposits."""
    retail = df.get("Retail Customer Deposits $m", pd.Series([0] * len(df)))
    deposits = df.get("Gross Total Deposits $m", pd.Series([np.nan] * len(df))).replace(
        0, np.nan
    )
    return (retail / deposits).mean()


def proxy_oci_losses(df: pd.DataFrame) -> tuple[float, float]:
    """Calculate Unrealized Losses using Available-for-Sale and Held-to-Maturity Securities."""
    oci = df.get("Available-for-Sale Securities $m", 0) + df.get(
        "Held-to-Maturity Securities $m", 0
    )
    equity = df.get("Total Equity $m", pd.Series([np.nan] * len(df))).replace(0, np.nan)
    assets = df.get("Total Assets $m", pd.Series([np.nan] * len(df))).replace(0, np.nan)
    return (oci / equity).mean(), (oci / assets).mean()


# === Main Function to Compute Indicators ===
def compute_advanced_indicators(
    df: pd.DataFrame,
    bank_name: str = None,
    source_file: str = None,
    date_col_name: str = None,
) -> dict:
    """
    Compute financial indicators and return structured JSON for a bank.
    Automatically detects period based on available date columns or index.
    """
    indicators = {}
    quality = {}

    # Helper function to check if all columns exist and are not all NaN
    def cols_exist_and_not_na(cols):
        return all(col in df.columns and not df[col].isna().all() for col in cols)

    # 1. Loan-to-Deposit Ratio (LDR)
    if cols_exist_and_not_na(["Gross Total Loans $m", "Retail Customer Deposits $m"]):
        indicators["Loan-to-Deposit Ratio"] = (
            df["Gross Total Loans $m"]
            / df["Retail Customer Deposits $m"].replace(0, np.nan)
        ).mean()
        quality["Loan-to-Deposit Ratio"] = "direct"
    else:
        indicators["Loan-to-Deposit Ratio"] = proxy_loan_to_deposit(df)
        quality["Loan-to-Deposit Ratio"] = "proxy"

    # 2. Cash Shortage Proxy
    if cols_exist_and_not_na(
        [
            "Cash and Balance at Central Bank(s) $m",
            "Loans and Advances to Financial Institutions $m",
            "Deposits made by the Central Bank $m",
            "Deposits by Banks $m",
        ]
    ):
        cash = df["Cash and Balance at Central Bank(s) $m"]
        interbank = df["Loans and Advances to Financial Institutions $m"]
        short_term_liab = (
            df["Deposits made by the Central Bank $m"] + df["Deposits by Banks $m"]
        )
        indicators["Cash Shortage Proxy"] = (
            (cash + interbank) / short_term_liab.replace(0, np.nan)
        ).mean()
        quality["Cash Shortage Proxy"] = "direct"
    else:
        indicators["Cash Shortage Proxy"] = proxy_cash_shortage(df)
        quality["Cash Shortage Proxy"] = "proxy"

    # 3. Duration Gap
    if cols_exist_and_not_na(["Avg Duration of Assets", "Avg Duration of Liabilities"]):
        indicators["Duration Gap"] = (
            df["Avg Duration of Assets"] - df["Avg Duration of Liabilities"]
        ).mean()
        quality["Duration Gap"] = "direct"
    else:
        indicators["Duration Gap"] = proxy_duration_gap(df)
        quality["Duration Gap"] = "proxy"

    # 4. Core Deposit Mix Ratio
    if cols_exist_and_not_na(
        ["Retail Customer Deposits $m", "Gross Total Deposits $m"]
    ):
        indicators["Core Deposit Mix Ratio"] = (
            df["Retail Customer Deposits $m"]
            / df["Gross Total Deposits $m"].replace(0, np.nan)
        ).mean()
        quality["Core Deposit Mix Ratio"] = "direct"
    else:
        indicators["Core Deposit Mix Ratio"] = proxy_core_deposit_mix(df)
        quality["Core Deposit Mix Ratio"] = "proxy"

    # 5. Net Stable Funding Ratio (NSFR)
    if (
        "Net Stable Funding Ratio %" in df.columns
        and not df["Net Stable Funding Ratio %"].isna().all()
    ):
        indicators["NSFR"] = (df["Net Stable Funding Ratio %"] / 100.0).mean()
        quality["NSFR"] = "direct"
    else:
        indicators["NSFR"] = None
        quality["NSFR"] = "proxy"

    # 6. OCI-based Unrealized Losses
    if cols_exist_and_not_na(
        ["Available-for-Sale Securities $m", "Held-to-Maturity Securities $m"]
    ):
        oci = (
            df["Available-for-Sale Securities $m"]
            + df["Held-to-Maturity Securities $m"]
        )
        indicators["OCI-based Losses to Equity"] = (
            oci / df["Total Equity $m"].replace(0, np.nan)
        ).mean()
        indicators["OCI-based Losses to Assets"] = (
            oci / df["Total Assets $m"].replace(0, np.nan)
        ).mean()
        quality["OCI-based Losses to Equity"] = "direct"
        quality["OCI-based Losses to Assets"] = "direct"
    else:
        loss_to_equity, loss_to_assets = proxy_oci_losses(df)
        indicators["OCI-based Losses to Equity"] = loss_to_equity
        indicators["OCI-based Losses to Assets"] = loss_to_assets
        quality["OCI-based Losses to Equity"] = "proxy"
        quality["OCI-based Losses to Assets"] = "proxy"

    # 7. FX Mismatch
    if cols_exist_and_not_na(["FX Assets", "FX Liabilities"]):
        fx_diff = (df["FX Assets"] - df["FX Liabilities"]).abs()
        indicators["FX Mismatch"] = (
            fx_diff / df["Total Equity $m"].replace(0, np.nan)
        ).mean()
        quality["FX Mismatch"] = "direct"
    else:
        indicators["FX Mismatch"] = proxy_fx_mismatch(df)
        quality["FX Mismatch"] = "proxy"

    # Replace NaN with None for JSON serialization
    for k, v in indicators.items():
        if pd.isna(v):
            indicators[k] = None

    # Period detection
    if date_col_name is not None and date_col_name in df.columns:
        df[date_col_name] = pd.to_datetime(df[date_col_name], errors="coerce")
        min_date = df[date_col_name].min()
        max_date = df[date_col_name].max()
        period = (
            f"{min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}"
            if pd.notna(min_date) and pd.notna(max_date)
            else None
        )
    else:
        period = None

    return {
        "meta": {
            "bank_name": bank_name,
            "period": period,
            "source_file": source_file,
        },
        "indicators": indicators,
        "quality": quality,
    }


def save_json(data: dict, filename: str):
    """
    Save the computed indicators to a JSON file.
    """
    with open(filename, "w") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    banks_list = [
        "916_Bank_of_China.xlsx",
        "3537_Nord_LB_Luxembourg.xlsx",
        "2938_KBC_Group.xlsx",
        "4367_Standard_Chartered.xlsx",
        "1258_Barclays.xlsx",
        "3166_Lloyds_TSB_Bank.xlsx",
        "3932_Royal_Bank_of_Canada.xlsx",
        "3404_First_Abu_Dhabi_Bank.xlsx",
        "1275_Basler_Kantonalbank.xlsx",
    ]

    for bank_file in banks_list:
        df = pd.read_excel(f"project/data/{bank_file}", header=1)
        df.drop(index=len(df) - 1, inplace=True)
        bank_name = bank_file.split("_", 1)[-1].replace(".xlsx", "").replace("_", " ")
        result = compute_advanced_indicators(
            df, bank_name=bank_name, source_file=bank_file, date_col_name="FYE"
        )

        save_json(result, f"output/{bank_name}_indicators.json")
