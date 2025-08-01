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
        exposure = (
            df["Derivatives (Assets) $m"] + df["Derivatives (Liabilities) $m"]
        ) / df["Total Assets $m"].replace(0, np.nan)
        result["indicator"] = exposure.mean()
        result["quality"] = "direct"
    else:
        result["indicator"] = proxy_derivatives_exposure(df)
        result["quality"] = "proxy"
    return result


def proxy_derivatives_exposure(df: pd.DataFrame) -> float | None:
    """Proxy: Use Trading Liabilities + Trading Securities / Total Assets"""
    cols = ["Trading Liabilities $m", "Trading Securities $m", "Total Assets $m"]
    if cols_exist_and_not_na(df, cols):
        proxy_val = (df["Trading Liabilities $m"] + df["Trading Securities $m"]) / df[
            "Total Assets $m"
        ].replace(0, np.nan)
        return proxy_val.mean()
    return None
