import pandas as pd
import numpy as np
from project.compute_advanced_indicators.utils import cols_exist_and_not_na


def compute_non_recurring_income_ratio(df: pd.DataFrame) -> dict:
    """Compute Non-Recurring Income Ratio"""
    result = {}
    cols = [
        "Total Profit or Loss on Discontinued Operations & Extraordinary Items $m",
        "Total Operating Income $m",
    ]
    if cols_exist_and_not_na(df, cols):
        indicator = df[cols[0]] / df[cols[1]].replace(0, np.nan)

        result["indicator_full"] = indicator
        result["indicator"] = indicator.mean()
        result["quality"] = "direct"
    else:
        result["indicator_full"] = proxy_non_recurring_income_ratio(df, full=True)
        result["indicator"] = proxy_non_recurring_income_ratio(df)
        result["quality"] = "proxy"
    return result


def proxy_non_recurring_income_ratio(
    df: pd.DataFrame, full: bool = False
) -> float | pd.Series | None:
    """Proxy: Use Other Non-Interest Income to Total Operating Income"""
    cols = ["Other Non-Interest Income $m", "Total Operating Income $m"]
    if cols_exist_and_not_na(df, cols):
        proxy = df[cols[0]] / df[cols[1]].replace(0, np.nan)

        if full:
            return proxy
        return proxy.mean()
    return None
