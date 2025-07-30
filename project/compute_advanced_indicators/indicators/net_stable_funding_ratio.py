import pandas as pd
from project.compute_advanced_indicators.utils import cols_exist_and_not_na


def compute_net_stable_funding_ratio(df: pd.DataFrame) -> dict:
    """Net Stable Funding Ratio (NSFR)"""

    result = {}
    if cols_exist_and_not_na(df, ["Net Stable Funding Ratio %"]):
        result["indicator"] = (df["Net Stable Funding Ratio %"] / 100.0).mean()
        result["quality"] = "direct"
    else:
        result["indicator"] = None
        result["quality"] = "proxy"

    return result
