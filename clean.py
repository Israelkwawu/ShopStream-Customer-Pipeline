import re

import numpy as np
import pandas as pd
import logging
from config import CONFIG, REGION_MAP


logger = logging.getLogger(__name__)

def standardize_emails(series: pd.Series) -> pd.Series:
    return (
        series
        .astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r"\s+", "", regex=True)  # Remove internal spaces
        .replace({"nan": np.nan, "none": np.nan, "": np.nan})
    )

def validate_emails(series: pd.Series) -> pd.Series:
    """Returns a boolean Series: True = valid email format."""
    return series.str.match(CONFIG["email_regex"], na=False)

def standardize_phone_numbers(series: pd.Series) -> pd.Series:
    """
    Normalize phone numbers: remove formatting, preserve + prefix.

    Examples:
        +1 (555) 123-4567  →  +15551234567
        555.123.4567       →  5551234567
        +44 20 7946 0958   →  +442079460958
        invalid-phone      →  NaN
    """
    def clean_phone(phone):
        if pd.isna(phone) or str(phone).strip() in ("", "nan", "None"):
            return np.nan
        phone = str(phone).strip()
        has_plus = phone.startswith("+")
        digits = re.sub(r"[^\d]", "", phone)
        if len(digits) < 7:         # Too short to be a real phone number
            return np.nan
        return f"+{digits}" if has_plus else digits

    return series.apply(clean_phone)


def standardize_names(series: pd.Series) -> pd.Series:
    return (
        series
        .astype(str)
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
        .str.title()
        .replace({"Nan": np.nan, "None": np.nan, "": np.nan})
    )

def standardize_regions(series: pd.Series) -> pd.Series:
    return (
        series
        .astype(str)
        .str.strip()
        .str.lower()
        .map(REGION_MAP)             # Unmapped values become NaN
    )

def standardize_opt_out(series: pd.Series) -> pd.Series:
    """Convert mixed opt_out representations to nullable boolean."""

    mapping = {
        1: True,
        0: False,
        "1": True,
        "0": False,
        True: True,
        False: False,
        "true": True,
        "false": False,
        "yes": True,
        "no": False,
        "y": True,
        "n": False,
    }

    return (
        series
        .astype(str)
        .str.strip()
        .str.lower()
        .replace({"nan": np.nan, "none": np.nan, "": np.nan})
        .map(mapping)
        .astype("boolean")
    )

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Apply all cleaning transformations to the unified DataFrame."""
    logger.info("STEP 2: Cleaning & Standardization")
    df = df.copy()

    df["email_raw"] = df["email"].copy()
    df["email"] = standardize_emails(df["email"])
    df["email_valid"] = validate_emails(df["email"])

    df["first_name"] = standardize_names(df["first_name"])
    df["last_name"] = standardize_names(df["last_name"])
    df["phone"] = standardize_phone_numbers(df["phone"])
    df["region"] = standardize_regions(df["region"])
    # df["registration_date"] = pd.to_datetime(df["registration_date"], errors="coerce")
    df["registration_date"] = pd.to_datetime(df["registration_date"], format="%Y-%m-%d", errors="coerce")
    df["opt_out"] = standardize_opt_out(df["opt_out"])

    invalid_emails = (~df["email_valid"]).sum()
    null_regions = df["region"].isna().sum()
    logger.info(f"  Invalid emails: {invalid_emails}")
    logger.info(f"  Null regions after standardization: {null_regions}")
    logger.info(f"  Records after cleaning: {len(df)}")
    return df
