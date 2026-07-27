import pandas as pd
import pytest
from pathlib import Path

from export import export_results


@pytest.fixture
def sample_data():
    """
    Create sample golden customer dataset and quality report.
    """

    customers = pd.DataFrame({
        "customer_id": [1, 2],
        "email": [
            "john@example.com",
            "jane@example.com"
        ],
        "first_name": [
            "John",
            "Jane"
        ],
        "source": [
            "crm",
            "website"
        ]
    })

    quality_report = pd.DataFrame({
        "check": [
            "missing_email",
            "duplicate_email"
        ],
        "passed": [
            True,
            True
        ],
        "count": [
            0,
            0
        ]
    })

    return customers, quality_report


def test_export_creates_output_directory(tmp_path, sample_data):
    """
    Verify output directory is created.
    """

    df, report = sample_data

    output_dir = tmp_path / "results"

    export_results(
        df,
        report,
        output_dir
    )

    assert output_dir.exists()
    assert output_dir.is_dir()


def test_export_creates_parquet_file(tmp_path, sample_data):
    """
    Verify parquet output exists and contains correct data.
    """

    df, report = sample_data

    output_dir = tmp_path / "results"

    export_results(
        df,
        report,
        output_dir
    )

    parquet_file = output_dir / "golden_customers.parquet"

    assert parquet_file.exists()

    loaded_df = pd.read_parquet(
        parquet_file
    )

    pd.testing.assert_frame_equal(
        loaded_df,
        df
    )


def test_export_creates_csv_file(tmp_path, sample_data):
    """
    Verify CSV export.
    """

    df, report = sample_data

    output_dir = tmp_path / "results"

    export_results(
        df,
        report,
        output_dir
    )

    csv_file = output_dir / "golden_customers.csv"

    assert csv_file.exists()

    loaded_df = pd.read_csv(
        csv_file,
        encoding="utf-8-sig"
    )

    pd.testing.assert_frame_equal(
        loaded_df,
        df
    )


def test_export_creates_quality_report(tmp_path, sample_data):
    """
    Verify quality report export.
    """

    df, report = sample_data

    output_dir = tmp_path / "results"

    export_results(
        df,
        report,
        output_dir
    )

    report_file = output_dir / "quality_report.csv"

    assert report_file.exists()

    loaded_report = pd.read_csv(
        report_file
    )

    pd.testing.assert_frame_equal(
        loaded_report,
        report
    )


def test_export_handles_existing_directory(tmp_path, sample_data):
    """
    Export should work when directory already exists.
    """

    df, report = sample_data

    output_dir = tmp_path / "results"

    output_dir.mkdir()

    export_results(
        df,
        report,
        output_dir
    )

    assert (
        output_dir / "golden_customers.parquet"
    ).exists()


def test_export_empty_dataframe(tmp_path):
    """
    Verify export works with empty datasets.
    """

    df = pd.DataFrame()

    report = pd.DataFrame()

    output_dir = tmp_path / "empty_results"

    export_results(
        df,
        report,
        output_dir
    )

    assert (
        output_dir / "golden_customers.csv"
    ).exists()

    assert (
        output_dir / "quality_report.csv"
    ).exists()
    
    