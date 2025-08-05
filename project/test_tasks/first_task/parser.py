import re
import pandas as pd
import logging
import os
from typing import List, Dict, Optional

os.makedirs("project/logs", exist_ok=True)
os.makedirs("output", exist_ok=True)

logging.basicConfig(
    filename=f"project/logs/parser.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
)


class Parser:
    """
    Defines the `Parser` class which provides functionality to read, parse,
    and extract financial indicators from textual input data.

    This class is designed for processing financial report data, with methods to read file contents,
    extract specific financial indicators, and identify relevant years.
    """

    def __init__(self):
        logging.info("Parser initialized")
        self.input_txt = None

    def read_file(self, file_name: str) -> None:
        """
        Reads the content of a given file and stores it as a stripped string.

        :param file_name: The name or path of the file to be read
        :type file_name: str
        :raises Exception: If an error occurs during the file reading process
        :return: None
        """
        logging.info(f"Reading file {file_name}")

        try:
            with open(file_name, "r") as f:
                self.input_txt = f.read().strip()

            logging.info(f"File {file_name} read successfully")
        except Exception:
            logging.error(f"Error reading file {file_name}", exc_info=True)

    def extract_indicators(
        self, indicators: Dict[str, List[str]], year: Optional[int] = None
    ) -> pd.DataFrame | None:
        """
        Extracts multiple financial indicators with their values and units from raw text.

        Args:
            indicators (Dict[str, List[str]]): Dictionary where keys are canonical indicator names,
                values are lists of possible aliases to look for in the text.
                Example: {"CET1 Ratio": ["CET1", "CET1 Capital Ratio"], ...}
            year (Optional[int]): Optional year to associate with all extracted indicators.

        Returns:
            pd.DataFrame: DataFrame with columns: ['Indicator', 'Value', 'Unit', 'Year'].
                          'Year' is filled with given year or None if not provided.
        """

        if not self.input_txt:
            logging.error("No input text provided")
            return None

        logging.info("Extracting indicators...")

        # Regex pattern template to extract a numeric value and optional unit after an indicator name
        # Matches optional prefixes, spaces, the indicator name (or alias), then a number and optional unit
        pattern_template = (
            r"(?:{aliases})"  # Match one of the aliases
            r"[^0-9\-+,.]*"  # Non-numeric chars between name and number
            r"([-+]?\d+(?:\.\d+)?)"  # Capture number (int or float)
            r"\s*"  # Optional whitespace
            r"(%|CHF\s*bn|billion|million)?"  # Optional units: %, CHF bn, billion, million
        )

        records = []

        # Prepare a joined pattern for each indicator with its aliases escaped and joined by |
        try:
            for canonical_name, aliases in indicators.items():
                aliases_pattern = "|".join(
                    re.escape(alias) for alias in [canonical_name] + aliases
                )
                pattern = pattern_template.format(aliases=aliases_pattern)

                match = re.search(pattern, self.input_txt, flags=re.IGNORECASE)
                if match:
                    value_str = match.group(1)
                    unit_raw = match.group(2) or ""
                    value = float(value_str)

                    # Normalize units to consistent representation
                    unit = unit_raw.strip().lower()
                    if unit in ["billion", "million"]:
                        # Convert textual units to abbreviation
                        if unit == "billion":
                            unit = "bn"
                        elif unit == "million":
                            unit = "mn"

                    records.append(
                        {
                            "Indicator": canonical_name,
                            "Value": value,
                            "Unit": unit.upper() if unit else "",
                            "Year": year,
                        }
                    )

            logging.info(f"Extracted {len(records)} indicators")

            return pd.DataFrame(records)

        except Exception:
            logging.error("Error extracting indicators", exc_info=True)
            return None

    def extract_year(self) -> int | None:
        logging.info("Extracting year...")
        pattern = r"(?:FY[\s\-:]?|year(?:-end)?|as of|in)[\s\-:]*(20\d{2})"
        match = re.search(pattern, self.input_txt, flags=re.IGNORECASE)
        if match:
            logging.info(f"Year extracted: {match.group(1)}")
            return int(match.group(1))
        logging.warning("Year not found")
        return None


if __name__ == "__main__":
    file_name = "data/input.txt"
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

    if df is not None:
        df.to_csv("output/output.csv", index=False)
