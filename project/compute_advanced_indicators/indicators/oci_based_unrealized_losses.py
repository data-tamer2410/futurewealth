import pandas as pd
import numpy as np
from project.compute_advanced_indicators.utils import cols_exist_and_not_na


def compute_oci(df: pd.DataFrame) -> float | None:
    """Calculate Other Comprehensive Income (OCI)"""
    if cols_exist_and_not_na(
        df, ["Available-for-Sale Securities $m", "Held-to-Maturity Securities $m"]
    ):
        oci = (
            df["Available-for-Sale Securities $m"]
            + df["Held-to-Maturity Securities $m"]
        )
        return oci.mean()
    else:
        return None


def compute_oci_based_unrealized_losses_to_equity(df: pd.DataFrame) -> dict | None:
    """OCI-based Unrealized Losses to Equity"""
    oci = compute_oci(df)

    result = {}
    if oci is not None and cols_exist_and_not_na(df, ["Total Equity $m"]):
        result["indicator"] = (oci / df["Total Equity $m"].replace(0, np.nan)).mean()
        result["quality"] = "direct"
    else:
        result["indicator"] = None
        result["quality"] = "proxy"

    return result


def compute_oci_based_unrealized_losses_to_assets(df: pd.DataFrame) -> dict | None:
    """OCI-based Unrealized Losses to Assets"""
    oci = compute_oci(df)

    result = {}
    if oci is not None and cols_exist_and_not_na(df, ["Total Assets $m"]):
        result["indicator"] = (oci / df["Total Assets $m"].replace(0, np.nan)).mean()
        result["quality"] = "direct"
    else:
        result["indicator"] = None
        result["quality"] = "proxy"

    return result
