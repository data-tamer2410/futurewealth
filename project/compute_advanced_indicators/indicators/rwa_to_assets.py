import pandas as pd
import numpy as np
from project.compute_advanced_indicators.utils import cols_exist_and_not_na


def compute_rwa_to_assets(df: pd.DataFrame) -> dict:
    """Compute RWA to Total Assets Ratio"""
    result = {}
    cols = ["Total Risk-Weighted Assets $m", "Total Assets $m"]

    if cols_exist_and_not_na(df, cols):
        indicator_full = df[cols[0]] / df[cols[1]].replace(0, np.nan)
        result["indicator_full"] = indicator_full
        result["indicator"] = indicator_full.mean()
        result["quality"] = "direct"
    else:
        proxy_full = proxy_rwa_to_assets(df, full=True)
        if proxy_full is not None:
            result["indicator_full"] = proxy_full
            result["indicator"] = proxy_full.mean()
            result["quality"] = "proxy"
        else:
            result["indicator_full"] = None
            result["indicator"] = None
            result["quality"] = "proxy"

    return result


def proxy_rwa_to_assets(
    df: pd.DataFrame, full: bool = False
) -> float | pd.Series | None:
    """Proxy: Use Credit RWA instead of Total RWA"""
    cols = ["Credit Risk-Weighted Assets $m", "Total Assets $m"]

    if cols_exist_and_not_na(df, cols):
        proxy = df[cols[0]] / df[cols[1]].replace(0, np.nan)
        if full:
            return proxy
        return proxy.mean()
    return None
