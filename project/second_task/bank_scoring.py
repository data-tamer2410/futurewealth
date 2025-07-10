import logging
import json
import os
import pandas as pd

os.makedirs("project/logs", exist_ok=True)
os.makedirs("output", exist_ok=True)

logging.basicConfig(
    filename=f"project/logs/scoring.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
)

SCORING_RULES_PATH = "project/data/scoring_rules.json"


def scoring(bank_data: dict) -> None | pd.DataFrame:
    """
    Evaluates bank data according to predefined scoring rules and produces a scorecard outlining results for each indicator.

    The function applies a set of scoring rules to bank data, which includes processing indicators and determining their
    classification, score, and confidence level based on thresholds and specified scoring logic. Data not matching expected
    indicators results in warnings. The total score is calculated by aggregating individual indicator scores and returned
    within the scorecard.

    Arguments:
        bank_data (dict): Dictionary containing the bank indicators and their corresponding values.

    Returns:
        None or pd.DataFrame: A DataFrame containing the scoring results for each indicator, including classification, score,
        confidence, and a total score. Returns None if scoring rules could not be loaded.
    """

    logging.info("Bank scoring...")

    try:
        logging.info(f"Loading scoring rules from {SCORING_RULES_PATH}")
        with open(SCORING_RULES_PATH, "r", encoding="utf-8") as f:
            scoring_rules = json.load(f)
    except Exception:
        logging.error("Error loading scoring rules", exc_info=True)
        return None

    logging.info("Scoring rules loaded.")

    scorecard = pd.DataFrame(
        columns=["Indicator", "Value", "Score", "Confidence", "Class"]
    )
    total_score = 0
    for indicator, rules in scoring_rules.items():
        logging.info(f"Processing scoring for indicator: {indicator}")

        indicator_value = bank_data.get(indicator)
        if not indicator_value:
            logging.warning(f"Indicator {indicator} not found in bank data.")
            continue

        threshold_low, threshold_high = rules["thresholds"]
        score_low, score_medium, score_high = rules["scores"]
        penalty = 10
        score = None
        confidence = None
        cls = None
        if indicator_value < threshold_low:
            cls = "Critical"
            score = score_low

            # Calculate confidence based on how far the indicator is below the low threshold
            confidence = 1 - indicator_value / threshold_low
            confidence = round(confidence, 2)

        elif threshold_low <= indicator_value < threshold_high:
            cls = "Warning"
            score = score_medium

            # Calculate confidence based on the midpoint of the thresholds
            mid_point = (threshold_low + threshold_high) / 2
            half_range = (threshold_high - threshold_low) / 2
            confidence = 1 - abs(indicator_value - mid_point) / half_range
            confidence = round(confidence, 2)

            # Apply penalty if the indicator is close to the low or high threshold
            if indicator_value < mid_point:
                score -= penalty

        elif indicator_value >= threshold_high:
            cls = "Good"
            score = score_high

            # Calculate confidence based on how close the indicator is to the high threshold
            confidence = min(indicator_value / (threshold_high * 2), 1)
            confidence = round(confidence, 2)

            # Apply penalty if the indicator is significantly below the high threshold
            if indicator_value < threshold_high * 1.5:
                score -= penalty

        total_score += score
        scorecard.loc[scorecard.shape[0]] = [
            indicator,
            indicator_value,
            score,
            confidence,
            cls,
        ]

    scorecard["Total Score"] = total_score
    logging.info("Scoring completed.")
    return scorecard


def scorecard_to_json(scorecard: pd.DataFrame, output_path: str) -> None:
    """Saves the scorecard DataFrame to a JSON file."""
    logging.info(f"Saving scorecard to {output_path}")

    data = {}
    for _, row in scorecard.iterrows():
        indicator = row["Indicator"]
        data[indicator] = {
            "value": (float(row["Value"])),
            "score": (float(row["Score"])),
            "confidence": (float(row["Confidence"])),
            "class": row["Class"],
        }

    data["Total Score"] = float(scorecard["Total Score"].iloc[0])

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception:
        logging.error("Error saving scorecard", exc_info=True)

    logging.info("Scorecard saved successfully.")


def bank_indicators_table_to_dict(table: pd.DataFrame) -> dict:
    """Converts a DataFrame containing bank indicators into a dictionary."""
    logging.info("Converting bank indicators table to dictionary...")

    bank_data = {}
    for _, row in table.iterrows():
        indicator = row["Indicator"]
        value = row["Value"]
        bank_data[indicator] = value

    return bank_data


if __name__ == "__main__":
    from project.first_task.parser import Parser

    file_name = "project/data/input.txt"
    indicator_aliases = {
        "CET1 Ratio": ["CET1", "CET1 Capital Ratio"],
        "Tier 1 Ratio": ["Tier 1"],
        "Total Capital Ratio": [],
        "Liquidity Coverage Ratio": ["LCR"],
        "Net Stable Funding Ratio": ["NSFR"],
        "Risk-Weighted Assets": ["RWA"],
    }

    parser = Parser()
    parser.read_file(file_name)
    year = parser.extract_year()
    df = parser.extract_indicators(indicator_aliases, year)

    test_bank_data = bank_indicators_table_to_dict(df)
    test_bank_name = "Test Bank"

    with open("project/data/bank_indicators.json", "r", encoding="utf-8") as f:
        bank_data = json.load(f)

    bank_data[test_bank_name] = test_bank_data
    for bank_name, indicators in bank_data.items():
        scorecard = scoring(indicators)
        if scorecard is not None:
            scorecard.to_csv(f"output/{bank_name}_scorecard.csv", index=False)
            scorecard_to_json(scorecard, f"output/{bank_name}_scorecard.json")
