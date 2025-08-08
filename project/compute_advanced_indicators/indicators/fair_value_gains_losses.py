import pandas as pd
from project.compute_advanced_indicators.utils import cols_exist_and_not_na


def compute_fair_value_gains_losses(df: pd.DataFrame) -> dict:
    """Compute Fair Value Gains/Losses"""
    col = "Unrealized Gains or Losses on Financial Instruments Designated at Fair Value $m"
    result = {}
    if cols_exist_and_not_na(df, [col]):
        indicator = df[col]

        result["indicator_full"] = indicator
        result["indicator"] = df[col].mean()
        result["quality"] = "direct"
    else:
        result["indicator_full"] = proxy_fair_value_gains_losses(df, full=True)
        result["indicator"] = proxy_fair_value_gains_losses(df)
        result["quality"] = "proxy"
    return result


def proxy_fair_value_gains_losses(
    df: pd.DataFrame, full: bool = False
) -> float | pd.Series | None:
    """Proxy: use Net Trading Income as proxy for fair value gains/losses"""
    if cols_exist_and_not_na(df, ["Net Trading Income $m"]):
        proxy = df["Net Trading Income $m"]

        if full:
            return proxy
        return df["Net Trading Income $m"].mean()
    return None
