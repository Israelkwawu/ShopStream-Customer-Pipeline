"""
ShopStream Customer Data Quality Pipeline
=========================================

Main pipeline entry point.

Orchestrates:
    1. Data Ingestion
    2. Data Cleaning
    3. Customer Deduplication
    4. Data Quality Validation
    5. EDA Report Generation
    6. Export Results

Run:
    python pipeline.py
"""

import logging

logging.basicConfig(level=logging.INFO)
from datetime import datetime

from config import CONFIG
from ingest import ingest_all_sources
from clean import clean_dataframe
from deduplicate import deduplicate_customers
from validate import run_quality_checks
from visualize import generate_eda_report
from export import export_results


logger = logging.getLogger(__name__)


def run_pipeline():
    """Execute the complete ShopStream customer data pipeline."""

    start_time = datetime.now()

    logger.info("=" * 60)
    logger.info("SHOPSTREAM CUSTOMER DATA QUALITY PIPELINE")
    logger.info(f"Run started: {start_time.isoformat()}")
    logger.info("=" * 60)

    # ------------------------------------------------------------------
    # Step 1: Data Ingestion
    # ------------------------------------------------------------------
    combined = ingest_all_sources()
    input_count = len(combined)

    # ------------------------------------------------------------------
    # Step 2: Data Cleaning
    # ------------------------------------------------------------------
    cleaned = clean_dataframe(combined)

    # ------------------------------------------------------------------
    # Step 3: Deduplication
    # ------------------------------------------------------------------
    deduped = deduplicate_customers(cleaned)

    # ------------------------------------------------------------------
    # Step 4: Data Quality Validation
    # ------------------------------------------------------------------
    logger.info("STEP 4: Quality Validation")
    quality_report = run_quality_checks(deduped)

    # ------------------------------------------------------------------
    # Step 5: Generate EDA Report
    # ------------------------------------------------------------------
    logger.info("STEP 5: Generating Visualizations")
    generate_eda_report(
        deduped,
        CONFIG["output_dir"],
    )

    # ------------------------------------------------------------------
    # Step 6: Export Results
    # ------------------------------------------------------------------
    logger.info("STEP 6: Exporting Results")
    export_results(
        deduped,
        quality_report,
        CONFIG["output_dir"],
    )

    # ------------------------------------------------------------------
    # Pipeline Summary
    # ------------------------------------------------------------------
    duration = (datetime.now() - start_time).total_seconds()

    logger.info("=" * 60)
    logger.info("PIPELINE COMPLETE")
    logger.info(f"Input records:           {input_count:,}")
    logger.info(f"Golden records:          {len(deduped):,}")
    logger.info(f"Duplicates removed:      {input_count - len(deduped):,}")
    logger.info(
        f"Quality checks passed:   "
        f"{(quality_report['status'] == 'PASS').sum()}/{len(quality_report)}"
    )
    logger.info(f"Execution time:          {duration:.2f} seconds")
    logger.info("=" * 60)


if __name__ == "__main__":
    run_pipeline()