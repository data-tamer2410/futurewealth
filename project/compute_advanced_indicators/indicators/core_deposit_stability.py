import pandas as pd
import numpy as np
from project.compute_advanced_indicators.utils import cols_exist_and_not_na


def compute_core_deposit_stability(df: pd.DataFrame) -> dict:
    """Compute Core Deposit Stability Proxy"""
    result = {}
    cols = ["Retail Customer Deposits $m", "Gross Total Deposits $m"]
    if cols_exist_and_not_na(df, cols):
        indicator = df[cols[0]] / df[cols[1]].replace(0, np.nan)

        result["indicator_full"] = indicator
        result["indicator"] = indicator.mean()
        result["quality"] = "direct"
    else:
        result["indicator_full"] = proxy_core_deposit_stability(df, full=True)
        result["indicator"] = proxy_core_deposit_stability(df)
        result["quality"] = "proxy"
    return result


def proxy_core_deposit_stability(
    df: pd.DataFrame, full: bool = False
) -> float | pd.Series | None:
    """Proxy: Use ratio of Retail Deposits to Total Liabilities"""
    if cols_exist_and_not_na(
        df, ["Retail Customer Deposits $m", "Total Liabilities $m"]
    ):
        proxy = df["Retail Customer Deposits $m"] / df["Total Liabilities $m"].replace(
            0, np.nan
        )

        if full:
            return proxy
        return proxy.mean()
    return None
