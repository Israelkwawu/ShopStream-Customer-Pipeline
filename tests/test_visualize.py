from pathlib import Path

import pandas as pd
import pytest
from PIL import Image
from visualize import generate_eda_report
import matplotlib
matplotlib.use("Agg")

@pytest.fixture
def sample_customer_df():
    """
    Customer dataframe with all visualization fields.
    """

    return pd.DataFrame({
        "email": [
            "john@test.com",
            "jane@test.com",
            "mike@test.com"
        ],
        "first_name": [
            "John",
            "Jane",
            "Mike"
        ],
        "last_name": [
            "Smith",
            "Brown",
            "Jones"
        ],
        "phone": [
            "123",
            "456",
            None
        ],
        "region": [
            "US",
            "EU",
            "APAC"
        ],
        "registration_date": pd.to_datetime([
            "2024-01-01",
            "2024-02-01",
            "2024-03-01"
        ]),
        "source": [
            "crm",
            "website",
            "erp"
        ],
        "email_valid": [
            True,
            True,
            False
        ],
        "opt_out": [
            0,
            1,
            0
        ]
    })


def test_generate_eda_report_creates_png(
    tmp_path,
    sample_customer_df
):
    """
    Verify EDA report image is created.
    """

    generate_eda_report(
        sample_customer_df,
        tmp_path
    )

    output_file = (
        tmp_path /
        "customer_quality_report.png"
    )

    assert output_file.exists()

    assert output_file.is_file()



def test_generated_report_is_valid_image(
    tmp_path,
    sample_customer_df
):
    """
    Verify generated file is a valid PNG.
    """

    generate_eda_report(
        sample_customer_df,
        tmp_path
    )

    output_file = (
        tmp_path /
        "customer_quality_report.png"
    )

    image = Image.open(output_file)

    assert image.format == "PNG"

    assert image.size[0] > 0
    assert image.size[1] > 0



def test_generate_report_with_sources_column(
    tmp_path,
    sample_customer_df
):
    """
    Verify visualization handles merged sources.
    """

    df = sample_customer_df.copy()

    df["sources"] = [
        "crm,website",
        "erp",
        "crm,erp"
    ]

    generate_eda_report(
        df,
        tmp_path
    )

    assert (
        tmp_path /
        "customer_quality_report.png"
    ).exists()



def test_generate_report_without_optional_columns(
    tmp_path
):
    """
    Verify optional fields do not break generation.
    """

    df = pd.DataFrame({
        "email": [
            "test@example.com"
        ],
        "first_name": [
            "Test"
        ],
        "last_name": [
            "User"
        ],
        "phone": [
            "123456"
        ],
        "region": [
            "US"
        ],
        "registration_date": pd.to_datetime(
            ["2024-01-01"]
        ),
        "source": [
            "crm"
        ]
    })

    generate_eda_report(
        df,
        tmp_path
    )

    assert (
        tmp_path /
        "customer_quality_report.png"
    ).exists()



def test_generate_report_creates_output_directory(
    sample_customer_df,
    tmp_path
):
    """
    Verify function works when output directory exists.
    """

    output_dir = tmp_path / "reports"

    output_dir.mkdir()

    generate_eda_report(
        sample_customer_df,
        output_dir
    )

    assert (
        output_dir /
        "customer_quality_report.png"
    ).exists()
    
