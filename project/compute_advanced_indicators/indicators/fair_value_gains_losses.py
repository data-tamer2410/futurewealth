import pandas as pd
from project.compute_advanced_indicators.utils import cols_exist_and_not_na


def compute_fair_value_gains_losses(df: pd.DataFrame) -> dict:
    """Compute Fair Value Gains/Losses"""
    col = "Unrealized Gains or Losses on Financial Instruments Designated at Fair Value $m"
    result = {}
    if cols_exist_and_not_na(df, [col]):
        result["indicator"] = df[col].mean()
        result["quality"] = "direct"
    else:
        result["indicator"] = proxy_fair_value_gains_losses(df)
        result["quality"] = "proxy"
    return result


def proxy_fair_value_gains_losses(df: pd.DataFrame) -> float | None:
    """Proxy: use Net Trading Income as proxy for fair value gains/losses"""
    if cols_exist_and_not_na(df, ["Net Trading Income $m"]):
        return df["Net Trading Income $m"].mean()
    return None
