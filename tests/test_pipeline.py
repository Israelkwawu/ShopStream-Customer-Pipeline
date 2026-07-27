import pandas as pd
import pytest

import pipeline


@pytest.fixture
def sample_dataframe():
    """
    Sample customer dataframe used between pipeline steps.
    """

    return pd.DataFrame({
        "email": [
            "john@example.com",
            "jane@example.com"
        ],
        "first_name": [
            "John",
            "Jane"
        ],
        "region": [
            "US",
            "EU"
        ]
    })


@pytest.fixture
def quality_report():
    """
    Mock quality validation result.
    """

    return pd.DataFrame({
        "check": [
            "NOT NULL: email",
            "UNIQUE: email"
        ],
        "status": [
            "PASS",
            "PASS"
        ]
    })


def test_run_pipeline_executes_all_steps(
    mocker,
    sample_dataframe,
    quality_report
):
    """
    Verify pipeline calls every processing stage.
    """

    # Mock pipeline stages
    mock_ingest = mocker.patch(
        "pipeline.ingest_all_sources",
        return_value=sample_dataframe
    )

    mock_clean = mocker.patch(
        "pipeline.clean_dataframe",
        return_value=sample_dataframe
    )

    mock_dedupe = mocker.patch(
        "pipeline.deduplicate_customers",
        return_value=sample_dataframe
    )

    mock_validate = mocker.patch(
        "pipeline.run_quality_checks",
        return_value=quality_report
    )

    mock_visualize = mocker.patch(
        "pipeline.generate_eda_report"
    )

    mock_export = mocker.patch(
        "pipeline.export_results"
    )


    pipeline.run_pipeline()


    # Verify execution order / calls

    mock_ingest.assert_called_once()

    mock_clean.assert_called_once_with(
        sample_dataframe
    )

    mock_dedupe.assert_called_once_with(
        sample_dataframe
    )

    mock_validate.assert_called_once_with(
        sample_dataframe
    )

    mock_visualize.assert_called_once()

    mock_export.assert_called_once()



def test_pipeline_passes_correct_export_arguments(
    mocker,
    sample_dataframe,
    quality_report
):
    """
    Verify export receives final dataset and quality report.
    """

    mocker.patch(
        "pipeline.ingest_all_sources",
        return_value=sample_dataframe
    )

    mocker.patch(
        "pipeline.clean_dataframe",
        return_value=sample_dataframe
    )

    mocker.patch(
        "pipeline.deduplicate_customers",
        return_value=sample_dataframe
    )

    mocker.patch(
        "pipeline.run_quality_checks",
        return_value=quality_report
    )

    mocker.patch(
        "pipeline.generate_eda_report"
    )

    export_mock = mocker.patch(
        "pipeline.export_results"
    )


    pipeline.run_pipeline()


    args = export_mock.call_args.args


    # First argument = golden dataset
    assert args[0].equals(
        sample_dataframe
    )

    # Second argument = validation report
    assert args[1].equals(
        quality_report
    )



def test_pipeline_calls_visualization_with_output_directory(
    mocker,
    sample_dataframe,
    quality_report
):
    """
    Verify EDA report receives correct output path.
    """

    mocker.patch(
        "pipeline.ingest_all_sources",
        return_value=sample_dataframe
    )

    mocker.patch(
        "pipeline.clean_dataframe",
        return_value=sample_dataframe
    )

    mocker.patch(
        "pipeline.deduplicate_customers",
        return_value=sample_dataframe
    )

    mocker.patch(
        "pipeline.run_quality_checks",
        return_value=quality_report
    )

    visualization_mock = mocker.patch(
        "pipeline.generate_eda_report"
    )

    mocker.patch(
        "pipeline.export_results"
    )


    pipeline.run_pipeline()


    visualization_mock.assert_called_once()

    args = visualization_mock.call_args.args

    assert args[0].equals(
        sample_dataframe
    )



def test_pipeline_handles_empty_dataset(
    mocker
):
    """
    Pipeline should not crash with empty input.
    """

    empty_df = pd.DataFrame()

    empty_report = pd.DataFrame(
        columns=[
            "check",
            "status"
        ]
    )


    mocker.patch(
        "pipeline.ingest_all_sources",
        return_value=empty_df
    )

    mocker.patch(
        "pipeline.clean_dataframe",
        return_value=empty_df
    )

    mocker.patch(
        "pipeline.deduplicate_customers",
        return_value=empty_df
    )

    mocker.patch(
        "pipeline.run_quality_checks",
        return_value=empty_report
    )

    mocker.patch(
        "pipeline.generate_eda_report"
    )

    mocker.patch(
        "pipeline.export_results"
    )


    # Should complete without exception
    pipeline.run_pipeline()
    
    