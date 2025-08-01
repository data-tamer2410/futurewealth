import pandas as pd
import numpy as np
from project.compute_advanced_indicators.utils import cols_exist_and_not_na


def compute_core_deposit_mix_ratio(df: pd.DataFrame) -> dict:
    """Core Deposit Mix Ratio"""

    result = {}
    if cols_exist_and_not_na(
        df, ["Retail Customer Deposits $m", "Gross Total Deposits $m"]
    ):
        result["indicator"] = (
            df["Retail Customer Deposits $m"]
            / df["Gross Total Deposits $m"].replace(0, np.nan)
        ).mean()
        result["quality"] = "direct"
    else:
        result["indicator"] = proxy_core_deposit_mix_ratio(df)
        result["quality"] = "proxy"

    return result


def proxy_core_deposit_mix_ratio(df: pd.DataFrame) -> float | None:
    """Proxy for Core Deposit Mix Ratio based on Corporate Deposits Share"""
    if cols_exist_and_not_na(
        df, ["Corporate Customer Deposits $m", "Gross Total Deposits $m"]
    ):
        corp_share = df["Corporate Customer Deposits $m"] / df[
            "Gross Total Deposits $m"
        ].replace(0, np.nan)
        return (1 - corp_share).mean()
    return None
