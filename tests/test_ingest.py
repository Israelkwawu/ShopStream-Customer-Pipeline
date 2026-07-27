import json
from pathlib import Path

import pandas as pd
import pytest

from ingest import (
    generate_synthetic_data,
    ingest_website_csv,
    ingest_crm_json,
    ingest_crm_api,
    ingest_erp_fixed_width,
    align_schema,
    ingest_all_sources,
)


@pytest.fixture
def temp_input_dir(tmp_path, monkeypatch):
    """
    Override CONFIG input_dir to temporary folder.
    """
    import ingest

    monkeypatch.setitem(
        ingest.CONFIG,
        "input_dir",
        tmp_path
    )

    generate_synthetic_data()

    return tmp_path


def test_generate_synthetic_data_creates_files(temp_input_dir):
    """
    Verify synthetic data generation creates all source files.
    """

    assert (temp_input_dir / "website_customers.csv").exists()
    assert (temp_input_dir / "crm_export.json").exists()
    assert (temp_input_dir / "erp_customers.txt").exists()


def test_ingest_website_csv(temp_input_dir):
    """
    Website CSV should:
    - load correctly
    - normalize columns
    - remove test accounts
    - add source column
    """

    filepath = temp_input_dir / "website_customers.csv"

    df = ingest_website_csv(filepath)

    assert isinstance(df, pd.DataFrame)

    assert "email" in df.columns
    assert "first_name" in df.columns
    assert "last_name" in df.columns

    assert "source" in df.columns
    assert df["source"].unique().tolist() == ["website"]

    # test accounts should be removed
    assert not df["email"].str.contains(
        "@test.shopstream.com",
        na=False
    ).any()


def test_ingest_crm_json(temp_input_dir):

    filepath = temp_input_dir / "crm_export.json"

    df = ingest_crm_json(filepath)

    assert isinstance(df, pd.DataFrame)

    assert len(df) > 0

    assert "email" in df.columns
    assert "first_name" in df.columns
    assert "last_name" in df.columns

    assert "source" in df.columns
    assert (df["source"] == "crm").all()


def test_ingest_erp_fixed_width(temp_input_dir):

    filepath = temp_input_dir / "erp_customers.txt"

    df = ingest_erp_fixed_width(filepath)

    assert isinstance(df, pd.DataFrame)

    assert len(df) > 0

    expected_columns = [
        "customer_id",
        "email",
        "phone",
        "first_name",
        "last_name",
        "region",
        "source",
    ]

    for col in expected_columns:
        assert col in df.columns

    assert (df["source"] == "erp").all()


def test_align_schema():

    df = pd.DataFrame({
        "email": ["test@example.com"],
        "extra_column": ["remove"]
    })

    from config import STANDARD_SCHEMA

    result = align_schema(
        df,
        "test"
    )

    # All standard fields exist
    for col in STANDARD_SCHEMA:
        assert col in result.columns

    # Extra fields removed
    assert "extra_column" not in result.columns


def test_ingest_all_sources(temp_input_dir):

    df = ingest_all_sources()

    assert isinstance(df, pd.DataFrame)

    assert len(df) > 0

    assert "source" in df.columns

    sources = set(df["source"].dropna())

    assert sources == {
        "website",
        "crm",
        "erp"
    }


def test_ingest_crm_api(mocker):

    mock_response_1 = mocker.Mock()

    mock_response_1.json.return_value = {
        "customers": [
            {
                "email": "john@test.com",
                "name": "John"
            }
        ],
        "total_pages": 1
    }

    mock_response_1.raise_for_status.return_value = None


    mocker.patch(
        "requests.get",
        return_value=mock_response_1
    )


    df = ingest_crm_api(
        "https://fake-api.com",
        "secret"
    )


    assert len(df) == 1

    assert df.iloc[0]["email"] == "john@test.com"

    assert df.iloc[0]["source"] == "crm"