import pandas as pd
import numpy as np
from project.compute_advanced_indicators.utils import cols_exist_and_not_na


def compute_cost_of_risk(df: pd.DataFrame) -> dict:
    """Compute Cost of Risk"""
    result = {}
    cols = ["Loan Impairment Provisions $m", "Gross Total Loans $m"]
    if cols_exist_and_not_na(df, cols):
        result["indicator"] = (df[cols[0]] / df[cols[1]].replace(0, np.nan)).mean()
        result["quality"] = "direct"
    else:
        result["indicator"] = proxy_cost_of_risk(df)
        result["quality"] = "proxy"
    return result


def proxy_cost_of_risk(df: pd.DataFrame) -> float | None:
    """Proxy: Use Allowance for Loan Losses instead of provisions"""
    cols = ["Allowance for Loan Losses $m", "Gross Total Loans $m"]
    if cols_exist_and_not_na(df, cols):
        return (df[cols[0]] / df[cols[1]].replace(0, np.nan)).mean()
    return None
