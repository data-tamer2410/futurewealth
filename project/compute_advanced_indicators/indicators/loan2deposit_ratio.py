import pandas as pd
import numpy as np
from project.compute_advanced_indicators.utils import cols_exist_and_not_na


def compute_loan_to_deposit_ratio(df: pd.DataFrame) -> dict:
    """Loan-to-Deposit Ratio (LDR)"""

    result = {}
    if cols_exist_and_not_na(
        df, ["Gross Total Loans $m", "Retail Customer Deposits $m"]
    ):
        result["indicator"] = (
            df["Gross Total Loans $m"]
            / df["Retail Customer Deposits $m"].replace(0, np.nan)
        ).mean()
        result["quality"] = "direct"
    else:
        result["indicator"] = proxy_loan_to_deposit(df)
        result["quality"] = "proxy"

    return result


def proxy_loan_to_deposit(df: pd.DataFrame) -> float:
    """Calculate Loan-to-Deposit Ratio using Gross Total Loans and Deposits."""

    if cols_exist_and_not_na(df, ["Gross Total Loans $m", "Gross Total Deposits $m"]):
        loans = df["Gross Total Loans $m"]
        deposits = df["Gross Total Deposits $m"].replace(0, np.nan)
        return (loans / deposits).mean()

    return None
