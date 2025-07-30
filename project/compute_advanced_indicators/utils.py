import pandas as pd
import json


def cols_exist_and_not_na(df: pd.DataFrame, cols: list[str]) -> bool:
    """Helper function to check if all columns exist and are not all NaN"""
    return all(col in df.columns and not df[col].isna().all() for col in cols)


def save_json(data: dict, filename: str):
    """Save the computed indicators to a JSON file."""

    for key, item in data["indicators"].items():
        if pd.isna(item):
            data["indicators"][key] = None

    with open(filename, "w") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def read_bank_data(file_path: str) -> pd.DataFrame:
    """Read bank data from a CSV or Excel file."""
    if file_path.endswith(".csv"):
        return pd.read_csv(file_path)
    elif file_path.endswith(".xlsx"):
        return pd.read_excel(file_path)
    else:
        raise ValueError("Unsupported file format. Please provide a CSV or Excel file.")


def save_bank_indicators_to_table(
    indicators: list[dict],
    output_file: str,
):
    """Save the computed indicators to a table format (CSV or Excel)."""

    flattened_data = []
    for indicator in indicators:
        row = {}

        row.update(indicator["meta"])
        row.update(indicator["indicators"])
        row.update({f"{k}_quality": i for k, i in indicator["quality"].items()})
        flattened_data.append(row)

    df = pd.DataFrame(flattened_data)

    if output_file.endswith(".csv"):
        df.to_csv(output_file, index=False)
    elif output_file.endswith(".xlsx"):
        df.to_excel(output_file, index=False)
    else:
        raise ValueError(
            "Unsupported output file format. Please provide a CSV or Excel file."
        )
