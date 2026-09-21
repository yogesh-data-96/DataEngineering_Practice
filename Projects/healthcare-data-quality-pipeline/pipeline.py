"""
Healthcare Encounter Data Quality Pipeline

Demonstrates:
- CSV ingestion
- Schema validation
- Data transformation
- Business-rule validation
- Rejected-record handling
- Data quality metrics

All sample data is synthetic.
"""

from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = {
    "encounter_id",
    "patient_id",
    "encounter_date",
    "department",
    "charge_amount",
}


def load_data(path: str | Path) -> pd.DataFrame:
    """Load encounter data and validate the required schema."""
    df = pd.read_csv(path)

    missing_columns = REQUIRED_COLUMNS - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    return df


def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize data types and create derived fields."""
    result = df.copy()

    result["encounter_date"] = pd.to_datetime(
        result["encounter_date"],
        errors="coerce",
    )

    result["charge_amount"] = pd.to_numeric(
        result["charge_amount"],
        errors="coerce",
    )

    result["department"] = (
        result["department"]
        .astype("string")
        .str.strip()
    )

    result["is_high_value"] = result["charge_amount"].ge(10000)

    return result


def validate_data(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Validate business rules and separate valid/rejected records.
    """

    result = df.copy()

    reasons = pd.Series(
        "",
        index=result.index,
        dtype="string",
    )

    validation_rules = [
        (
            result["encounter_id"].isna(),
            "missing_encounter_id",
        ),
        (
            result["patient_id"].isna(),
            "missing_patient_id",
        ),
        (
            result["encounter_date"].isna(),
            "invalid_encounter_date",
        ),
        (
            result["department"].isna()
            | result["department"].eq(""),
            "missing_department",
        ),
        (
            result["charge_amount"].isna()
            | result["charge_amount"].lt(0),
            "invalid_charge_amount",
        ),
    ]

    for condition, reason in validation_rules:
        reasons = reasons.mask(
            condition & reasons.eq(""),
            reason,
        )

    result["validation_status"] = reasons.mask(
        reasons.eq(""),
        "valid",
    )

    valid_records = result[
        result["validation_status"].eq("valid")
    ].copy()

    rejected_records = result[
        ~result["validation_status"].eq("valid")
    ].copy()

    return valid_records, rejected_records


def build_quality_summary(
    source: pd.DataFrame,
    valid: pd.DataFrame,
    rejected: pd.DataFrame,
) -> dict[str, int | float]:
    """Build an audit-friendly data quality summary."""

    total_records = len(source)

    quality_rate = (
        (len(valid) / total_records) * 100
        if total_records
        else 0.0
    )

    return {
        "total_records": total_records,
        "valid_records": len(valid),
        "rejected_records": len(rejected),
        "quality_rate_pct": round(quality_rate, 2),
    }


def run_pipeline(
    input_path: str,
    output_dir: str = "output",
) -> dict[str, int | float]:
    """Run the complete data quality pipeline."""

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    source = load_data(input_path)

    transformed = transform_data(source)

    valid_records, rejected_records = validate_data(
        transformed
    )

    valid_records.to_csv(
        output / "valid_encounters.csv",
        index=False,
    )

    rejected_records.to_csv(
        output / "rejected_encounters.csv",
        index=False,
    )

    summary = build_quality_summary(
        transformed,
        valid_records,
        rejected_records,
    )

    pd.DataFrame([summary]).to_json(
        output / "quality_summary.json",
        orient="records",
        indent=2,
    )

    return summary


if __name__ == "__main__":
    report = run_pipeline(
        "data/encounters.csv"
    )

    print("Pipeline completed successfully.")
    print(report)
