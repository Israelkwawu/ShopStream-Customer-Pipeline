import numpy as np
import pandas as pd

from clean import (
    standardize_emails,
    validate_emails,
    standardize_phone_numbers,
    standardize_names,
    standardize_regions,
    standardize_opt_out,
    clean_dataframe,
)


def test_standardize_emails():
    emails = pd.Series([
        " TEST@EMAIL.COM ",
        "John @gmail.com",
        "",
        None,
    ])

    result = standardize_emails(emails)

    assert result.iloc[0] == "test@email.com"
    assert result.iloc[1] == "john@gmail.com"
    assert pd.isna(result.iloc[2])
    assert pd.isna(result.iloc[3])


def test_validate_emails():
    emails = pd.Series([
        "user@gmail.com",
        "invalid",
        "abc@",
        np.nan,
    ])

    result = validate_emails(emails)

    assert result.tolist() == [
        True,
        False,
        False,
        False
    ]


def test_standardize_phone_numbers():
    phones = pd.Series([
        "+1 (555) 123-4567",
        "555.123.4567",
        "123",
        "",
        None,
    ])

    result = standardize_phone_numbers(phones)

    assert result.iloc[0] == "+15551234567"
    assert result.iloc[1] == "5551234567"
    assert pd.isna(result.iloc[2])
    assert pd.isna(result.iloc[3])
    assert pd.isna(result.iloc[4])


def test_standardize_names():
    names = pd.Series([
        "  john   doe ",
        "MARY",
        "",
        None,
    ])

    result = standardize_names(names)

    assert result.iloc[0] == "John Doe"
    assert result.iloc[1] == "Mary"
    assert pd.isna(result.iloc[2])
    assert pd.isna(result.iloc[3])


def test_standardize_regions():

    regions = pd.Series([
        "usa",
        "Europe",
        "Asia Pacific",
        "unknown",
    ])

    result = standardize_regions(regions)

    assert result.iloc[0] == "US"
    assert result.iloc[1] == "EU"
    assert result.iloc[2] == "APAC"
    assert pd.isna(result.iloc[3])


def test_standardize_opt_out():

    values = pd.Series([
        "YES",
        "0",
        "false",
        "",
        None,
    ])

    result = standardize_opt_out(values)

    assert bool(result.iloc[0]) is True
    assert bool(result.iloc[1]) is False
    assert bool(result.iloc[2]) is False
    assert pd.isna(result.iloc[3])
    assert pd.isna(result.iloc[4])


def test_clean_dataframe():

    df = pd.DataFrame({
        "email": [" TEST@EMAIL.COM "],
        "first_name": [" john "],
        "last_name": [" DOE "],
        "phone": ["+1 (555) 123-4567"],
        "region": ["usa"],
        "registration_date": ["2026-01-01"],
        "opt_out": ["yes"],
        "source": ["crm"],
    })

    cleaned = clean_dataframe(df)

    assert cleaned.loc[0, "email"] == "test@email.com"
    assert bool(cleaned.loc[0, "email_valid"]) is True
    assert cleaned.loc[0, "first_name"] == "John"
    assert cleaned.loc[0, "last_name"] == "Doe"
    assert cleaned.loc[0, "phone"] == "+15551234567"
    assert cleaned.loc[0, "region"] == "US"
    assert bool(cleaned.loc[0, "opt_out"]) is True
    assert pd.notna(cleaned.loc[0, "registration_date"])
    
    