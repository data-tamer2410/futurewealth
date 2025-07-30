import pandas as pd
import numpy as np
from project.compute_advanced_indicators.utils import cols_exist_and_not_na


def compute_fx_mismatch(df: pd.DataFrame) -> dict:
    """Foreign Exchange Mismatch"""

    result = {}
    if cols_exist_and_not_na(df, ["FX Assets", "FX Liabilities", "Total Equity $m"]):
        fx_diff = (df["FX Assets"] - df["FX Liabilities"]).abs()
        result["indicator"] = (
            fx_diff / df["Total Equity $m"].replace(0, np.nan)
        ).mean()
        result["quality"] = "direct"
    else:
        result["indicator"] = proxy_fx_mismatch(df)
        result["quality"] = "proxy"

    return result


def proxy_fx_mismatch(df: pd.DataFrame) -> float | None:
    """Calculate FX Mismatch using FX Assets and Liabilities."""

    if cols_exist_and_not_na(
        df,
        ["Derivatives (Assets) $m", "Derivatives (Liabilities) $m", "Total Equity $m"],
    ):
        fx_assets = df["Derivatives (Assets) $m"]
        fx_liab = df["Derivatives (Liabilities) $m"]
        equity = df["Total Equity $m"].replace(0, np.nan)
        return ((fx_assets - fx_liab).abs() / equity).mean()

    return None
