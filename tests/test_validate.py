import pandas as pd
import pytest

from validate import (
    DataQualityValidator,
    run_quality_checks,
)


@pytest.fixture
def valid_customer_df():
    """
    Customer dataset that should pass all checks.
    """

    return pd.DataFrame({
        "email": [
            "john@example.com",
            "jane@example.com",
            "mike@example.com"
        ],
        "first_name": [
            "John",
            "Jane",
            "Mike"
        ],
        "region": [
            "US",
            "EU",
            "APAC"
        ],
        "registration_date": pd.to_datetime([
            "2022-01-01",
            "2023-05-10",
            "2024-02-15"
        ])
    })


@pytest.fixture
def invalid_customer_df():
    """
    Customer dataset with quality problems.
    """

    return pd.DataFrame({
        "email": [
            "john@example.com",
            "john@example.com",
            "invalid-email",
            None
        ],
        "first_name": [
            "John",
            None,
            "Mike",
            "Sarah"
        ],
        "region": [
            "US",
            "INVALID",
            "EU",
            None
        ],
        "registration_date": pd.to_datetime([
            "2022-01-01",
            "2000-01-01",
            "2024-01-01",
            "2035-01-01"
        ])
    })


def test_validator_initialization(valid_customer_df):
    """
    Validator should initialize correctly.
    """

    validator = DataQualityValidator(
        valid_customer_df
    )

    assert validator.df.equals(valid_customer_df)
    assert validator.threshold == 0.95
    assert validator.n == 3
    assert validator.results == []


def test_record_pass_status(valid_customer_df):

    validator = DataQualityValidator(
        valid_customer_df
    )

    result = validator._record(
        "TEST",
        "Test check",
        failed=0,
        total=3
    )

    assert result["pass_rate"] == 1.0
    assert result["status"] == "PASS"
    assert result["passed"] == 3
    assert result["failed"] == 0


def test_record_fail_status():

    validator = DataQualityValidator(
        pd.DataFrame(),
        threshold=0.95
    )

    result = validator._record(
        "TEST",
        "Test failure",
        failed=2,
        total=10
    )

    assert result["pass_rate"] == 0.8
    assert result["status"] == "FAIL"


def test_check_not_null_pass(valid_customer_df):

    validator = DataQualityValidator(
        valid_customer_df
    )

    result = validator.check_not_null(
        "email",
        "Email required"
    )

    assert result["failed"] == 0
    assert result["status"] == "PASS"


def test_check_not_null_fail(invalid_customer_df):

    validator = DataQualityValidator(
        invalid_customer_df
    )

    result = validator.check_not_null(
        "email",
        "Email required"
    )

    assert result["failed"] == 1
    assert result["status"] == "FAIL"


def test_check_unique_pass(valid_customer_df):

    validator = DataQualityValidator(
        valid_customer_df
    )

    result = validator.check_unique(
        "email",
        "Emails unique"
    )

    assert result["failed"] == 0
    assert result["status"] == "PASS"


def test_check_unique_fail(invalid_customer_df):

    validator = DataQualityValidator(
        invalid_customer_df
    )

    result = validator.check_unique(
        "email",
        "Emails unique"
    )

    assert result["failed"] == 1
    assert result["status"] == "FAIL"


def test_check_regex_pass(valid_customer_df):

    validator = DataQualityValidator(
        valid_customer_df
    )

    result = validator.check_regex(
        "email",
        r"^[\w\.-]+@[\w\.-]+\.\w+$",
        "Valid email"
    )

    assert result["failed"] == 0
    assert result["status"] == "PASS"


def test_check_regex_fail(invalid_customer_df):

    validator = DataQualityValidator(
        invalid_customer_df
    )

    result = validator.check_regex(
        "email",
        r"^[\w\.-]+@[\w\.-]+\.\w+$",
        "Valid email"
    )

    assert result["failed"] == 1
    assert result["status"] == "FAIL"


def test_check_values_in_set_pass(valid_customer_df):

    validator = DataQualityValidator(
        valid_customer_df
    )

    result = validator.check_values_in_set(
        "region",
        ["US", "EU", "APAC"],
        "Valid region"
    )

    assert result["failed"] == 0


def test_check_values_in_set_fail(invalid_customer_df):

    validator = DataQualityValidator(
        invalid_customer_df
    )

    result = validator.check_values_in_set(
        "region",
        ["US", "EU", "APAC"],
        "Valid region"
    )

    assert result["failed"] == 1
    assert result["status"] == "FAIL"


def test_check_date_range_pass(valid_customer_df):

    validator = DataQualityValidator(
        valid_customer_df
    )

    result = validator.check_date_range(
        "registration_date",
        "2010-01-01",
        "2025-01-01",
        "Valid date"
    )

    assert result["failed"] == 0
    assert result["status"] == "PASS"


def test_check_date_range_fail(invalid_customer_df):

    validator = DataQualityValidator(
        invalid_customer_df
    )

    result = validator.check_date_range(
        "registration_date",
        "2010-01-01",
        "2025-01-01",
        "Valid date"
    )

    assert result["failed"] == 2
    assert result["status"] == "FAIL"


def test_generate_report(valid_customer_df):

    validator = DataQualityValidator(
        valid_customer_df
    )

    validator.check_not_null(
        "email",
        "Email required"
    )

    report = validator.generate_report()

    assert isinstance(report, pd.DataFrame)

    assert len(report) == 1

    assert "check" in report.columns
    assert "status" in report.columns


def test_run_quality_checks_pass(valid_customer_df):

    report = run_quality_checks(
        valid_customer_df
    )

    assert isinstance(report, pd.DataFrame)

    assert (report["status"] == "PASS").all()


def test_run_quality_checks_fail(invalid_customer_df):

    report = run_quality_checks(
        invalid_customer_df
    )

    assert isinstance(report, pd.DataFrame)

    assert (report["status"] == "FAIL").any()
    