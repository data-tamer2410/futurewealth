import pandas as pd
import numpy as np
from project.compute_advanced_indicators.utils import cols_exist_and_not_na


def compute_rwa_to_assets(df: pd.DataFrame) -> dict:
    """Compute RWA to Total Assets Ratio"""
    result = {}
    cols = ["Total Risk-Weighted Assets $m", "Total Assets $m"]
    if cols_exist_and_not_na(df, cols):
        result["indicator"] = (df[cols[0]] / df[cols[1]].replace(0, np.nan)).mean()
        result["quality"] = "direct"
    else:
        result["indicator"] = proxy_rwa_to_assets(df)
        result["quality"] = "proxy"
    return result


def proxy_rwa_to_assets(df: pd.DataFrame) -> float | None:
    """Proxy: Use Credit RWA instead of Total RWA"""
    cols = ["Credit Risk-Weighted Assets $m", "Total Assets $m"]
    if cols_exist_and_not_na(df, cols):
        return (df[cols[0]] / df[cols[1]].replace(0, np.nan)).mean()
    return None
