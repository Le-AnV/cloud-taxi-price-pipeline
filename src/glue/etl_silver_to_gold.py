import os
import sys
from typing import List, Tuple
from urllib.parse import urlparse

import boto3
from botocore.exceptions import ClientError
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.errors.exceptions.base import AnalysisException
from awsglue.utils import getResolvedOptions  # type: ignore

"""ETL job: Silver -> Gold

This module reads silver parquet data and populates gold dimension and fact
tables in S3. The file intentionally preserves the original job logic; only
comments and docstrings were cleaned up for clarity.
"""


def get_job_args():
    """Parse and return job arguments from Glue/CLI.

    Expected options:
    - INPUT_PATH: S3 path to the silver parquet files to process.
    """
    return getResolvedOptions(
        args=sys.argv,
        options=["INPUT_PATH"],
    )


spark = SparkSession.builder.appName("silver_to_gold_etl").getOrCreate()


def split_s3_path(path: str) -> Tuple[str, str]:
    """Split an S3 URI into bucket and key prefix."""

    parsed = urlparse(path)

    if parsed.scheme != "s3" or not parsed.netloc:
        raise ValueError(f"Expected an s3:// path, got: {path}")

    return parsed.netloc, parsed.path.lstrip("/")


def path_exists(path: str) -> bool:
    """Return True when the target path has at least one object."""

    if not path.startswith("s3://"):
        return os.path.exists(path)

    bucket_name, prefix = split_s3_path(path)
    s3_client = boto3.client("s3")

    try:
        response = s3_client.list_objects_v2(
            Bucket=bucket_name,
            Prefix=prefix,
            MaxKeys=1,
        )
    except ClientError as error:
        error_code = error.response.get("Error", {}).get("Code")
        if error_code in {"NoSuchBucket", "404"}:
            return False
        raise

    return response.get("KeyCount", 0) > 0


def read_existing_parquet(spark_session: SparkSession, path: str):
    """Read an existing Parquet dataset if the path is present."""

    if not path_exists(path):
        return None

    try:
        return spark_session.read.parquet(path)
    except AnalysisException as error:
        if "Path does not exist" in str(error):
            return None
        raise


def update_dimension(
    new_dim_df: DataFrame,
    bucket_name: str,
    prefix: str,
    business_key_columns: List[str],
) -> None:
    """Write or merge a dimension table to the gold location.

    Behavior:
    - If the gold path does not exist, write `new_dim_df` as-is.
    - If the gold path exists, union the existing and new rows, remove
      duplicates, then overwrite the gold path.
    """

    gold_path = f"s3://{bucket_name}/{prefix}"

    existing_dim_df = read_existing_parquet(spark, gold_path)

    if existing_dim_df is None:
        updated_dim_df = new_dim_df.dropDuplicates(business_key_columns)
    else:
        updated_dim_df = existing_dim_df.unionByName(other=new_dim_df).dropDuplicates(
            business_key_columns
        )

    updated_dim_df.write.mode("overwrite").parquet(gold_path)


def update_fact(
    new_fact_df: DataFrame,
    bucket_name: str,
    prefix: str,
) -> None:
    """Append a fact table batch to the gold location."""

    gold_path = f"s3://{bucket_name}/{prefix}"

    if not path_exists(gold_path):
        new_fact_df.write.mode("append").partitionBy("year", "month").parquet(
            gold_path,
        )
        return

    new_fact_df.write.mode("append").partitionBy("year", "month").parquet(
        gold_path,
    )


def create_dim_date(silver_df: DataFrame) -> DataFrame:
    """Create date dimension from silver `pickup_datetime`.

    Columns produced: full_date, date_key (YYYYMMDD int), year, month, day,
    weekday, quarter, is_weekend.
    """
    dim_date = (
        silver_df.select(F.to_date("pickup_datetime").alias("full_date"))
        .distinct()
        .withColumn("date_key", F.date_format("full_date", "yyyyMMdd").cast("int"))
        .withColumn("year", F.year("full_date"))
        .withColumn("month", F.month("full_date"))
        .withColumn("day", F.dayofmonth("full_date"))
        .withColumn("weekday", F.dayofweek("full_date"))
        .withColumn("quarter", F.quarter("full_date"))
        .withColumn("is_weekend", F.dayofweek("full_date").isin([1, 7]))
    )
    return dim_date


def create_dim_vendor(silver_df: DataFrame) -> DataFrame:
    """Create vendor dimension mapping `vendor_id` to a human-friendly name."""
    dim_vendor = (
        silver_df.select("vendor_id")
        .distinct()
        .withColumn(
            "vendor_name",
            F.when(F.col("vendor_id") == 1, "Creative Mobile Technologies")
            .when(F.col("vendor_id") == 2, "VeriFone Inc")
            .otherwise("Unknown"),
        )
    )
    return dim_vendor


def create_dim_payment(silver_df: DataFrame) -> DataFrame:
    """Create payment dimension mapping `payment_type` to a readable name."""
    dim_payment = (
        silver_df.select("payment_type")
        .distinct()
        .withColumn(
            "payment_name",
            F.when(F.col("payment_type") == 1, "Credit Card")
            .when(F.col("payment_type") == 2, "Cash")
            .when(F.col("payment_type") == 3, "No Charge")
            .when(F.col("payment_type") == 4, "Dispute")
            .when(F.col("payment_type") == 5, "Unknown")
            .when(F.col("payment_type") == 6, "Voided Trip")
            .otherwise("Other"),
        )
    )
    return dim_payment


def create_dim_rate_code(silver_df: DataFrame) -> DataFrame:
    """Create rate code dimension mapping `rate_code_id` to a readable name."""
    dim_rate_code = (
        silver_df.select("rate_code_id")
        .distinct()
        .withColumn(
            "rate_code_name",
            F.when(F.col("rate_code_id") == 1, "Standard Rate")
            .when(F.col("rate_code_id") == 2, "JFK")
            .when(F.col("rate_code_id") == 3, "Newark")
            .when(F.col("rate_code_id") == 4, "Nassau or Westchester")
            .when(F.col("rate_code_id") == 5, "Negotiated Fare")
            .when(F.col("rate_code_id") == 6, "Group Ride")
            .otherwise("Other"),
        )
    )
    return dim_rate_code


def create_fact_trips(silver_df: DataFrame) -> DataFrame:
    """Build the fact_trips table with surrogate key and engineered features.

    The `trip_id` surrogate key is a SHA-256 hash of several identifying
    fields. Additional columns include `duration_minutes`, `fare_per_mile`,
    `tip_percentage`, `pickup_hour` and a boolean `is_rush_hour`.
    """
    fact_trips = (
        silver_df
        # Surrogate key
        .withColumn(
            "trip_id",
            F.sha2(
                F.concat_ws(
                    "|",
                    F.col("vendor_id").cast("string"),
                    F.col("pickup_datetime").cast("string"),
                    F.col("dropoff_datetime").cast("string"),
                    F.col("fare_amount").cast("string"),
                    F.col("trip_distance_miles").cast("string"),
                ),
                256,
            ),
        )
        # Foreign key -> dim_date
        .withColumn(
            "date_key",
            F.date_format(F.to_date("pickup_datetime"), "yyyyMMdd").cast("int"),
        )
        # Feature engineering
        .withColumn(
            "duration_minutes",
            (F.unix_timestamp("dropoff_datetime") - F.unix_timestamp("pickup_datetime"))
            / 60,
        )
        .withColumn(
            "fare_per_mile",
            F.when(
                F.col("trip_distance_miles") > 0,
                F.col("fare_amount") / F.col("trip_distance_miles"),
            ),
        )
        .withColumn(
            "tip_percentage",
            F.when(
                F.col("fare_amount") > 0,
                F.col("tip_amount") / F.col("fare_amount") * 100,
            ),
        )
        .withColumn("pickup_hour", F.hour("pickup_datetime"))
        .withColumn(
            "is_rush_hour",
            (F.col("pickup_hour").between(7, 9) | F.col("pickup_hour").between(16, 19)),
        )
        .withColumn("year", F.year("pickup_datetime"))
        .withColumn("month", F.month("pickup_datetime"))
        .select(
            "trip_id",
            "date_key",
            "vendor_id",
            "payment_type",
            "rate_code_id",
            "passenger_count",
            "trip_distance_miles",
            "fare_amount",
            "extra_amount",
            "mta_tax_amount",
            "tip_amount",
            "tolls_amount",
            "improvement_surcharge",
            "total_amount",
            "pickup_datetime",
            "dropoff_datetime",
            "pickup_hour",
            "duration_minutes",
            "fare_per_mile",
            "tip_percentage",
            "is_rush_hour",
            "pickup_longitude",
            "pickup_latitude",
            "dropoff_longitude",
            "dropoff_latitude",
            "year",
            "month",
        )
    )
    return fact_trips


def main() -> None:
    """Read silver data and update the gold layer."""

    args = get_job_args()
    input_path = args["INPUT_PATH"]

    silver_df = spark.read.parquet(input_path)

    update_dimension(
        new_dim_df=create_dim_date(silver_df),
        bucket_name="nyc-yellow-taxi-data-lake",
        prefix="gold/dim_date/",
        business_key_columns=["date_key"],
    )

    update_dimension(
        new_dim_df=create_dim_vendor(silver_df),
        bucket_name="nyc-yellow-taxi-data-lake",
        prefix="gold/dim_vendor/",
        business_key_columns=["vendor_id"],
    )

    update_dimension(
        new_dim_df=create_dim_payment(silver_df),
        bucket_name="nyc-yellow-taxi-data-lake",
        prefix="gold/dim_payment/",
        business_key_columns=["payment_type"],
    )

    update_dimension(
        new_dim_df=create_dim_rate_code(silver_df),
        bucket_name="nyc-yellow-taxi-data-lake",
        prefix="gold/dim_rate_code/",
        business_key_columns=["rate_code_id"],
    )

    update_fact(
        new_fact_df=create_fact_trips(silver_df),
        bucket_name="nyc-yellow-taxi-data-lake",
        prefix="gold/fact_trips/",
    )


if __name__ == "__main__":
    main()
