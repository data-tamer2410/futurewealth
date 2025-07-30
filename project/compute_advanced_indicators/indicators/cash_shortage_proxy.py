import pandas as pd
import numpy as np
from project.compute_advanced_indicators.utils import cols_exist_and_not_na


def compute_cash_shortage_proxy(df: pd.DataFrame) -> dict:
    """Cash Shortage Proxy"""

    result = {}
    if cols_exist_and_not_na(
        df,
        [
            "Cash and Balance at Central Bank(s) $m",
            "Loans and Advances to Financial Institutions $m",
            "Deposits made by the Central Bank $m",
            "Deposits by Banks $m",
        ],
    ):
        cash = df["Cash and Balance at Central Bank(s) $m"]
        interbank = df["Loans and Advances to Financial Institutions $m"]
        short_term_liab = (
            df["Deposits made by the Central Bank $m"] + df["Deposits by Banks $m"]
        )
        result["indicator"] = (
            (cash + interbank) / short_term_liab.replace(0, np.nan)
        ).mean()
        result["quality"] = "direct"
    else:
        result["indicator"] = None
        result["quality"] = "proxy"

    return result
