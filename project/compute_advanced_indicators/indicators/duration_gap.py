import pandas as pd
import numpy as np
from project.compute_advanced_indicators.utils import cols_exist_and_not_na


def compute_duration_gap(df: pd.DataFrame) -> dict:
    """Duration Gap"""

    result = {}
    if cols_exist_and_not_na(
        df, ["Avg Duration of Assets", "Avg Duration of Liabilities"]
    ):
        indicator = df["Avg Duration of Assets"] - df["Avg Duration of Liabilities"]

        result["indicator_full"] = indicator
        result["indicator"] = indicator.mean()
        result["quality"] = "direct"
    else:
        result["indicator_full"] = proxy_duration_gap(df, full=True)
        result["indicator"] = proxy_duration_gap(df)
        result["quality"] = "proxy"

    return result


def proxy_duration_gap(
    df: pd.DataFrame, full: bool = False
) -> float | pd.Series | None:
    """Calculate Duration Gap using available data."""

    if cols_exist_and_not_na(
        df,
        [
            "Deposits made by the Central Bank $m",
            "Deposits by Banks $m",
            "Total Senior Debt $m",
            "Subordinated Liabilities $m",
            "Total Liabilities $m",
        ],
    ):
        short_term = (
            df["Deposits made by the Central Bank $m"] + df["Deposits by Banks $m"]
        )
        long_term = df["Total Senior Debt $m"] + df["Subordinated Liabilities $m"]
        total_liab = df["Total Liabilities $m"].replace(0, np.nan)
        proxy = (long_term - short_term) / total_liab

        if full:
            return proxy
        return proxy.mean()

    return None
