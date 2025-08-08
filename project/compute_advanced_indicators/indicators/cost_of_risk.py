import pandas as pd
import numpy as np
from project.compute_advanced_indicators.utils import cols_exist_and_not_na


def compute_cost_of_risk(df: pd.DataFrame) -> dict:
    """Compute Cost of Risk"""
    result = {}
    cols = ["Loan Impairment Provisions $m", "Gross Total Loans $m"]
    if cols_exist_and_not_na(df, cols):
        indicator = df[cols[0]] / df[cols[1]].replace(0, np.nan)

        result["indicator_full"] = indicator
        result["indicator"] = indicator.mean()
        result["quality"] = "direct"
    else:
        result["indicator_full"] = proxy_cost_of_risk(df, full=True)
        result["indicator"] = proxy_cost_of_risk(df)
        result["quality"] = "proxy"
    return result


def proxy_cost_of_risk(
    df: pd.DataFrame, full: bool = False
) -> float | pd.Series | None:
    """Proxy: Use Allowance for Loan Losses instead of provisions"""
    cols = ["Allowance for Loan Losses $m", "Gross Total Loans $m"]
    if cols_exist_and_not_na(df, cols):
        proxy = df[cols[0]] / df[cols[1]].replace(0, np.nan)

        if full:
            return proxy
        return proxy.mean()
    return None
