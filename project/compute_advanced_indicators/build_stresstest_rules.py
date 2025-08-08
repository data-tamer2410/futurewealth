"""
Build stress-test logic rules (causal mapping) based on indicators.
"""

import os
import pandas as pd
import json


def clean_indicators(indicators_full: dict) -> dict:
    """Drop NaN inside each series and remove empty series entirely."""
    clean_data = {}
    for k, v in indicators_full.items():
        if v is not None:
            v = v.dropna()
            if not v.empty:
                clean_data[k] = v
    return clean_data


def quantile(series: pd.Series, value: float) -> float:
    """Compute quantile as float."""
    return float(series.quantile(value))


def fmt(x: float, nd: int = 4) -> str:
    """Format number for embedding into condition strings."""
    return f"{x:.{nd}f}"


def decimals_for(name: str) -> int:
    """
    Return number of decimals for formatting based on indicator name.
    """
    two = {"Loan_to_Deposit_Ratio", "Net_Stable_Funding_Ratio", "Duration_Gap"}
    return 2 if name in two else 4


def signed_direction(series: pd.Series, default_direction: str) -> str:
    """
    Decide direction based on data sign when metric can be negative or positive.
    If median < 0 -> '<' (more negative is worse), else use default_direction.
    """
    med = float(series.median())
    return "<" if med < 0 else default_direction


def pick_threshold(
    name: str, series: pd.Series, direction: str, expr: str | None = None
) -> dict:
    """
    Pick dynamic WARNING/CRITICAL thresholds from quantiles and immediately
    build the condition strings using the provided direction.

      direction:
        '>' : warn = q75, critical = q90  (higher is worse)
        '<' : warn = q25, critical = q10  (lower is worse)

    expr:
        Optional left-hand expression for the condition (e.g., 'abs(Duration_Gap)').
        Defaults to the indicator name.
    """
    q10 = quantile(series, 0.10)
    q25 = quantile(series, 0.25)
    q75 = quantile(series, 0.75)
    q90 = quantile(series, 0.90)

    if direction == ">":
        warn, crit = q75, q90
        op = ">"
    else:
        warn, crit = q25, q10
        op = "<"

    nd = decimals_for(name)
    lhs = expr if expr is not None else name

    return {
        "name": name,
        "warn": warn,
        "critical": crit,
        "condition_warning": f"{lhs} {op} {fmt(warn, nd)}",
        "condition_critical": f"{lhs} {op} {fmt(crit, nd)}",
    }


def add_rule(
    rules: list, condition_warning: str, condition_critical: str, rationale: str
):
    """Append a simple rule object."""
    rules.append(
        {
            "condition_warning": condition_warning,
            "condition_critical": condition_critical,
            "rationale": rationale,
        }
    )


def build_rules_from_bank_data(bank_data: dict) -> list:
    """
    Build rules from available indicators using only their own distributions.
    """
    indicators_full = clean_indicators(bank_data["indicators_full"])
    rules = []

    def has(k):
        return k in indicators_full and indicators_full[k].count() >= 2

    # --------------------
    # Liquidity (single)
    # --------------------
    if has("Loan_to_Deposit_Ratio"):
        name = "Loan_to_Deposit_Ratio"
        thr = pick_threshold(name, indicators_full[name], ">")
        add_rule(
            rules,
            thr["condition_warning"],
            thr["condition_critical"],
            "High Loan-to-Deposit Ratio indicates potential liquidity stress.",
        )

    if has("Net_Stable_Funding_Ratio"):
        name = "Net_Stable_Funding_Ratio"
        thr = pick_threshold(name, indicators_full[name], "<")
        add_rule(
            rules,
            thr["condition_warning"],
            thr["condition_critical"],
            "NSFR below internal history hints funding stress.",
        )

    if has("Cash_Shortage_Proxy"):
        name = "Cash_Shortage_Proxy"
        thr = pick_threshold(name, indicators_full[name], ">")
        add_rule(
            rules,
            thr["condition_warning"],
            thr["condition_critical"],
            "Deterioration in short-term liquidity conditions.",
        )

    if has("Core_Deposit_Mix_Ratio"):
        name = "Core_Deposit_Mix_Ratio"
        thr = pick_threshold(name, indicators_full[name], "<")
        add_rule(
            rules,
            thr["condition_warning"],
            thr["condition_critical"],
            "Low share of core deposits weakens funding stability.",
        )

    if has("Core_Deposit_Stability"):
        name = "Core_Deposit_Stability"
        thr = pick_threshold(name, indicators_full[name], "<")
        add_rule(
            rules,
            thr["condition_warning"],
            thr["condition_critical"],
            "Declining deposit stability increases funding risk.",
        )

    # --------------------
    # Market / IRRBB
    # --------------------
    if has("Duration_Gap"):
        name = "Duration_Gap"
        thr = pick_threshold(name, indicators_full[name], ">", expr=f"abs({name})")
        add_rule(
            rules,
            thr["condition_warning"],
            thr["condition_critical"],
            "Large duration gap increases interest rate risk (IRRBB).",
        )

    if has("Derivatives_Exposure"):
        name = "Derivatives_Exposure"
        thr = pick_threshold(name, indicators_full[name], ">")
        add_rule(
            rules,
            thr["condition_warning"],
            thr["condition_critical"],
            "Higher derivatives exposure may raise market/counterparty risk.",
        )

    if has("FX_Mismatch"):
        name = "FX_Mismatch"
        thr = pick_threshold(name, indicators_full[name], ">")
        add_rule(
            rules,
            thr["condition_warning"],
            thr["condition_critical"],
            "FX asset/liability imbalance indicates currency risk.",
        )

    if has("Fair_Value_Gains_Losses"):
        name = "Fair_Value_Gains_Losses"
        thr = pick_threshold(name, indicators_full[name], "<")
        add_rule(
            rules,
            thr["condition_warning"],
            thr["condition_critical"],
            "Negative fair-value remeasurements indicate valuation pressure.",
        )

    # --------------------
    # Capital / Balance Sheet
    # --------------------
    if has("RWA_to_Assets"):
        name = "RWA_to_Assets"
        thr = pick_threshold(name, indicators_full[name], ">")
        add_rule(
            rules,
            thr["condition_warning"],
            thr["condition_critical"],
            "High RWA density implies risk-heavy balance sheet.",
        )

    # OCI-based unrealized losses (auto-direction by median sign)
    if has("OCI_Based_Unrealized_Losses_to_Equity"):
        name = "OCI_Based_Unrealized_Losses_to_Equity"
        direction = signed_direction(indicators_full[name], default_direction=">")
        thr = pick_threshold(name, indicators_full[name], direction)
        add_rule(
            rules,
            thr["condition_warning"],
            thr["condition_critical"],
            (
                "Large OCI-based unrealized losses weigh on capital."
                if direction == ">"
                else "More negative OCI-based unrealized losses weigh on capital."
            ),
        )

    if has("OCI_Based_Unrealized_Losses_to_Assets"):
        name = "OCI_Based_Unrealized_Losses_to_Assets"
        direction = signed_direction(indicators_full[name], default_direction=">")
        thr = pick_threshold(name, indicators_full[name], direction)
        add_rule(
            rules,
            thr["condition_warning"],
            thr["condition_critical"],
            (
                "Large OCI-based unrealized losses relative to assets signal valuation risk."
                if direction == ">"
                else "More negative OCI-based unrealized losses (to assets) signal valuation risk."
            ),
        )

    # --------------------
    # Credit / Earnings
    # --------------------
    if has("Cost_of_Risk"):
        name = "Cost_of_Risk"
        thr = pick_threshold(name, indicators_full[name], ">")
        add_rule(
            rules,
            thr["condition_warning"],
            thr["condition_critical"],
            "Rising cost of risk indicates credit deterioration.",
        )

    if has("Non_Recurring_Income_Ratio"):
        name = "Non_Recurring_Income_Ratio"
        thr = pick_threshold(name, indicators_full[name], ">")
        add_rule(
            rules,
            thr["condition_warning"],
            thr["condition_critical"],
            "High share of non-recurring income undermines earnings quality.",
        )

    # --------------------
    # Combo rules (AND)
    # --------------------
    # Liquidity: high LDR AND low NSFR
    if has("Loan_to_Deposit_Ratio") and has("Net_Stable_Funding_Ratio"):
        ldr = pick_threshold(
            "Loan_to_Deposit_Ratio", indicators_full["Loan_to_Deposit_Ratio"], ">"
        )
        nsfr = pick_threshold(
            "Net_Stable_Funding_Ratio", indicators_full["Net_Stable_Funding_Ratio"], "<"
        )
        add_rule(
            rules,
            f"({ldr['condition_warning']}) and ({nsfr['condition_warning']})",
            f"({ldr['condition_critical']}) and ({nsfr['condition_critical']})",
            "High LDR together with low NSFR flags elevated liquidity stress.",
        )

    # Capital: high RWA density AND large OCI losses (equity or assets)
    if has("RWA_to_Assets") and (
        has("OCI_Based_Unrealized_Losses_to_Equity")
        or has("OCI_Based_Unrealized_Losses_to_Assets")
    ):
        rwa = pick_threshold("RWA_to_Assets", indicators_full["RWA_to_Assets"], ">")
        if has("OCI_Based_Unrealized_Losses_to_Equity"):
            oname = "OCI_Based_Unrealized_Losses_to_Equity"
        else:
            oname = "OCI_Based_Unrealized_Losses_to_Assets"
        odir = signed_direction(indicators_full[oname], default_direction=">")
        othr = pick_threshold(oname, indicators_full[oname], odir)
        add_rule(
            rules,
            f"({rwa['condition_warning']}) and ({othr['condition_warning'] if odir == '>' else othr['condition_warning']})",
            f"({rwa['condition_critical']}) and ({othr['condition_critical'] if odir == '>' else othr['condition_critical']})",
            "Risk-dense balance sheet combined with sizable OCI losses points to capital pressure.",
        )

    # Liquidity: cash shortage proxy AND weak core deposit stability
    if has("Cash_Shortage_Proxy") and has("Core_Deposit_Stability"):
        csp = pick_threshold(
            "Cash_Shortage_Proxy", indicators_full["Cash_Shortage_Proxy"], ">"
        )
        cds = pick_threshold(
            "Core_Deposit_Stability", indicators_full["Core_Deposit_Stability"], "<"
        )
        add_rule(
            rules,
            f"({csp['condition_warning']}) and ({cds['condition_warning']})",
            f"({csp['condition_critical']}) and ({cds['condition_critical']})",
            "Short-term liquidity strain paired with weak deposit stability.",
        )

    # Market: big duration gap AND negative FV remeasurements
    if has("Duration_Gap") and has("Fair_Value_Gains_Losses"):
        dg = pick_threshold(
            "Duration_Gap",
            indicators_full["Duration_Gap"],
            ">",
            expr="abs(Duration_Gap)",
        )
        fv = pick_threshold(
            "Fair_Value_Gains_Losses", indicators_full["Fair_Value_Gains_Losses"], "<"
        )
        add_rule(
            rules,
            f"({dg['condition_warning']}) and ({fv['condition_warning']})",
            f"({dg['condition_critical']}) and ({fv['condition_critical']})",
            "IRRBB exposure coupled with valuation losses.",
        )

    # Market/Counterparty: FX mismatch AND derivatives exposure both high
    if has("FX_Mismatch") and has("Derivatives_Exposure"):
        fx = pick_threshold("FX_Mismatch", indicators_full["FX_Mismatch"], ">")
        der = pick_threshold(
            "Derivatives_Exposure", indicators_full["Derivatives_Exposure"], ">"
        )
        add_rule(
            rules,
            f"({fx['condition_warning']}) and ({der['condition_warning']})",
            f"({fx['condition_critical']}) and ({der['condition_critical']})",
            "Elevated FX imbalance together with sizable derivatives exposure.",
        )

    # Earnings quality: high non-recurring share AND negative FV
    if has("Non_Recurring_Income_Ratio") and has("Fair_Value_Gains_Losses"):
        nri = pick_threshold(
            "Non_Recurring_Income_Ratio",
            indicators_full["Non_Recurring_Income_Ratio"],
            ">",
        )
        fv = pick_threshold(
            "Fair_Value_Gains_Losses", indicators_full["Fair_Value_Gains_Losses"], "<"
        )
        add_rule(
            rules,
            f"({nri['condition_warning']}) and ({fv['condition_warning']})",
            f"({nri['condition_critical']}) and ({fv['condition_critical']})",
            "Large non-recurring income share alongside negative FV signals weak earnings quality.",
        )

    # Funding mix: low core deposit mix AND low NSFR
    if has("Core_Deposit_Mix_Ratio") and has("Net_Stable_Funding_Ratio"):
        cdm = pick_threshold(
            "Core_Deposit_Mix_Ratio", indicators_full["Core_Deposit_Mix_Ratio"], "<"
        )
        nsfr = pick_threshold(
            "Net_Stable_Funding_Ratio", indicators_full["Net_Stable_Funding_Ratio"], "<"
        )
        add_rule(
            rules,
            f"({cdm['condition_warning']}) and ({nsfr['condition_warning']})",
            f"({cdm['condition_critical']}) and ({nsfr['condition_critical']})",
            "Weak core funding base combined with low NSFR.",
        )

    return rules


def build_stresstest_rules(bank_data: dict, output_dir: str, file: str) -> list:
    """
    Build stress-test rules based on bank data indicators and save to JSON.
    """
    rules = build_rules_from_bank_data(bank_data)

    os.makedirs(output_dir, exist_ok=True)

    output_path = f"{output_dir}/{file}_rules.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(rules, f, indent=4, ensure_ascii=False)

    return rules
