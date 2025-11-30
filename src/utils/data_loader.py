import pandas as pd
import os
import yaml
from datetime import datetime, timedelta

def load_config(path: str = "config/config.yaml") -> dict:
    """
    Loads YAML configuration file.

    Why this exists:
    - Centralizes all settings (thresholds, paths, flags)
    - Makes your entire pipeline configurable
    """

    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_dataset(config: dict) -> pd.DataFrame:
    """
    Loads data based on the config:
    - sample dataset for quick dev
    - full dataset for final run

    Why this exists:
    - Standardizes how data is loaded
    - Prevents mistakes like loading wrong files
    """

    if config["data"]["use_sample_data"]:
        path = config["data"]["sample_path"]
    else:
        path = config["data"]["full_path"]

    if not os.path.exists(path):
        raise FileNotFoundError(f"Dataset not found at: {path}")

    return pd.read_csv(path)


def filter_last_n_days(df: pd.DataFrame, days: int) -> pd.DataFrame:
    """
    Filters dataframe to keep only rows within the last N days.

    Why this exists:
    - Most FB ad analysis compares recent vs previous performance
    """

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    cutoff = datetime.now() - timedelta(days=days)
    return df[df["date"] >= cutoff]


def safe_div(a, b):
    """Avoids division errors like dividing by zero."""
    if b in (0, None) or pd.isna(b):
        return 0
    return a / b
