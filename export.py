from pathlib import Path
import logging
import pandas as pd

logger = logging.getLogger(__name__)


def export_results(df: pd.DataFrame,
                   quality_report: pd.DataFrame,
                   output_dir: Path) -> None:
    """
    Export the pipeline outputs.

    Args:
        df: Final golden customer dataset.
        quality_report: Data quality report.
        output_dir: Directory to save outputs.
    """

    output_dir.mkdir(parents=True, exist_ok=True)

    # Export Parquet
    parquet_path = output_dir / "golden_customers.parquet"
    df.to_parquet(
        parquet_path,
        index=False,
        engine="pyarrow",
        compression="gzip",
    )
    logger.info(f"Parquet export: {parquet_path}")

    # Export CSV
    csv_path = output_dir / "golden_customers.csv"
    df.to_csv(
        csv_path,
        index=False,
        encoding="utf-8-sig",
    )
    logger.info(f"CSV export: {csv_path}")

    # Export quality report
    report_path = output_dir / "quality_report.csv"
    quality_report.to_csv(
        report_path,
        index=False,
    )
    logger.info(f"Quality report: {report_path}")