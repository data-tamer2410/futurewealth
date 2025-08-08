import pandas as pd
import numpy as np
from project.compute_advanced_indicators.utils import cols_exist_and_not_na


def compute_fx_mismatch(df: pd.DataFrame) -> dict:
    """Foreign Exchange Mismatch"""

    result = {}
    if cols_exist_and_not_na(df, ["FX Assets", "FX Liabilities", "Total Equity $m"]):
        fx_diff = (df["FX Assets"] - df["FX Liabilities"]).abs()
        indicator = fx_diff / df["Total Equity $m"].replace(0, np.nan)

        result["indicator_full"] = indicator
        result["indicator"] = indicator.mean()
        result["quality"] = "direct"
    else:
        result["indicator_full"] = proxy_fx_mismatch(df, full=True)
        result["indicator"] = proxy_fx_mismatch(df)
        result["quality"] = "proxy"

    return result


def proxy_fx_mismatch(df: pd.DataFrame, full: bool = False) -> float | pd.Series | None:
    """Calculate FX Mismatch using FX Assets and Liabilities."""

    if cols_exist_and_not_na(
        df,
        ["Derivatives (Assets) $m", "Derivatives (Liabilities) $m", "Total Equity $m"],
    ):
        fx_assets = df["Derivatives (Assets) $m"]
        fx_liab = df["Derivatives (Liabilities) $m"]
        equity = df["Total Equity $m"].replace(0, np.nan)
        proxy = (fx_assets - fx_liab).abs() / equity

        if full:
            return proxy
        return proxy.mean()
    return None
