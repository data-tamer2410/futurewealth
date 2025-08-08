import pandas as pd
import numpy as np
from project.compute_advanced_indicators.utils import cols_exist_and_not_na


def compute_derivatives_exposure(df: pd.DataFrame) -> dict:
    """Compute Derivatives Exposure"""
    result = {}
    cols = [
        "Derivatives (Assets) $m",
        "Derivatives (Liabilities) $m",
        "Total Assets $m",
    ]
    if cols_exist_and_not_na(df, cols):
        indicator = (
            df["Derivatives (Assets) $m"] + df["Derivatives (Liabilities) $m"]
        ) / df["Total Assets $m"].replace(0, np.nan)

        result["indicator_full"] = indicator
        result["indicator"] = indicator.mean()
        result["quality"] = "direct"
    else:
        result["indicator_full"] = proxy_derivatives_exposure(df, full=True)
        result["indicator"] = proxy_derivatives_exposure(df)
        result["quality"] = "proxy"
    return result


def proxy_derivatives_exposure(
    df: pd.DataFrame, full: bool = False
) -> float | pd.Series | None:
    """Proxy: Use Trading Liabilities + Trading Securities / Total Assets"""
    cols = ["Trading Liabilities $m", "Trading Securities $m", "Total Assets $m"]
    if cols_exist_and_not_na(df, cols):
        proxy = (df["Trading Liabilities $m"] + df["Trading Securities $m"]) / df[
            "Total Assets $m"
        ].replace(0, np.nan)

        if full:
            return proxy
        return proxy.mean()
    return None
