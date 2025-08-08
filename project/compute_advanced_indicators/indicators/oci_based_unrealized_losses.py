import pandas as pd
import numpy as np
from project.compute_advanced_indicators.utils import cols_exist_and_not_na


def compute_oci(df: pd.DataFrame, full: bool = False) -> float | pd.Series | None:
    """Calculate Other Comprehensive Income (OCI)"""
    if cols_exist_and_not_na(
        df, ["Available-for-Sale Securities $m", "Held-to-Maturity Securities $m"]
    ):
        oci = (
            df["Available-for-Sale Securities $m"]
            + df["Held-to-Maturity Securities $m"]
        )
        if full:
            return oci
        return oci.mean()
    else:
        return proxy_oci(df, full=full)


def proxy_oci(df: pd.DataFrame, full: bool = False) -> float | pd.Series | None:
    """Proxy for Other Comprehensive Income based on Available-for-Sale Securities"""
    if cols_exist_and_not_na(df, ["Available-for-Sale Securities $m"]):
        if full:
            return df["Available-for-Sale Securities $m"]
        return df["Available-for-Sale Securities $m"].mean()
    return None


def compute_oci_based_unrealized_losses_to_equity(df: pd.DataFrame) -> dict | None:
    """OCI-based Unrealized Losses to Equity"""
    result = {}
    oci_full = compute_oci(df, full=True)
    oci_mean = compute_oci(df, full=False)

    if oci_mean is not None and cols_exist_and_not_na(df, ["Total Equity $m"]):
        indicator_full = oci_full / df["Total Equity $m"].replace(0, np.nan)
        result["indicator_full"] = indicator_full
        result["indicator"] = indicator_full.mean()
        result["quality"] = "direct"
    else:
        proxy_full = proxy_oci(df, full=True)
        if proxy_full is not None and cols_exist_and_not_na(df, ["Total Equity $m"]):
            indicator_full = proxy_full / df["Total Equity $m"].replace(0, np.nan)
            result["indicator_full"] = indicator_full
            result["indicator"] = indicator_full.mean()
            result["quality"] = "proxy"
        else:
            result["indicator_full"] = None
            result["indicator"] = None
            result["quality"] = "proxy"

    return result


def compute_oci_based_unrealized_losses_to_assets(df: pd.DataFrame) -> dict | None:
    """OCI-based Unrealized Losses to Assets"""
    result = {}
    oci_full = compute_oci(df, full=True)
    oci_mean = compute_oci(df, full=False)

    if oci_mean is not None and cols_exist_and_not_na(df, ["Total Assets $m"]):
        indicator_full = oci_full / df["Total Assets $m"].replace(0, np.nan)
        result["indicator_full"] = indicator_full
        result["indicator"] = indicator_full.mean()
        result["quality"] = "direct"
    else:
        proxy_full = proxy_oci(df, full=True)
        if proxy_full is not None and cols_exist_and_not_na(df, ["Total Assets $m"]):
            indicator_full = proxy_full / df["Total Assets $m"].replace(0, np.nan)
            result["indicator_full"] = indicator_full
            result["indicator"] = indicator_full.mean()
            result["quality"] = "proxy"
        else:
            result["indicator_full"] = None
            result["indicator"] = None
            result["quality"] = "proxy"

    return result
