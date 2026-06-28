from pyspark.sql import SparkSession
import pyspark.sql.functions as F
from pyspark.sql.types import IntegerType, DoubleType, TimestampType

import os
import sys
from awsglue.utils import getResolvedOptions  # type: ignore


def get_job_args():
    """Get Glue job arguments."""

    return getResolvedOptions(
        args=sys.argv,
        options=["INPUT_PATH", "OUTPUT_PATH"],
    )


def create_spark_session():
    """Create Spark session."""

    return SparkSession.builder.appName("bronze_to_silver_trip_data").getOrCreate()


def read_input_data(spark, input_path):
    """Read Bronze input data based on the file extension."""

    input_file = os.path.basename(input_path).lower()

    if input_file.endswith(".parquet"):
        return spark.read.parquet(path=input_path)

    if input_file.endswith(".csv"):
        return spark.read.csv(
            path=input_path,
            header=True,
        )

    raise ValueError(
        f"Unsupported Bronze input format for path: {input_path}",
    )


def clean_data(df):
    """Clean and standardize raw trip data."""

    # Drop null, drop duplicates
    df_clean = df.dropna().dropDuplicates()

    # Data type casting
    df_clean = (
        df_clean
        # Vendor information
        .withColumn(
            "vendor_id",
            F.col("VendorID").cast(IntegerType()),
        )
        # Pickup and dropoff timestamps
        .withColumn(
            "pickup_datetime",
            F.col("tpep_pickup_datetime").cast(TimestampType()),
        )
        .withColumn(
            "dropoff_datetime",
            F.col("tpep_dropoff_datetime").cast(TimestampType()),
        )
        # Trip details
        .withColumn(
            "passenger_count",
            F.col("passenger_count").cast(IntegerType()),
        )
        .withColumn(
            "trip_distance_miles",
            F.col("trip_distance").cast(DoubleType()),
        )
        .withColumn(
            "rate_code_id",
            F.col("RateCodeID").cast(IntegerType()),
        )
        .withColumn(
            "store_and_fwd_flag",
            F.col("store_and_fwd_flag"),
        )
        # Pickup and dropoff coordinates
        .withColumn(
            "pickup_longitude",
            F.col("pickup_longitude").cast(DoubleType()),
        )
        .withColumn(
            "pickup_latitude",
            F.col("pickup_latitude").cast(DoubleType()),
        )
        .withColumn(
            "dropoff_longitude",
            F.col("dropoff_longitude").cast(DoubleType()),
        )
        .withColumn(
            "dropoff_latitude",
            F.col("dropoff_latitude").cast(DoubleType()),
        )
        # Payment information
        .withColumn(
            "payment_type",
            F.col("payment_type").cast(IntegerType()),
        )
        # Fare and charges
        .withColumn(
            "fare_amount",
            F.col("fare_amount").cast(DoubleType()),
        )
        .withColumn(
            "extra_amount",
            F.col("extra").cast(DoubleType()),
        )
        .withColumn(
            "mta_tax_amount",
            F.col("mta_tax").cast(DoubleType()),
        )
        .withColumn(
            "tip_amount",
            F.col("tip_amount").cast(DoubleType()),
        )
        .withColumn(
            "tolls_amount",
            F.col("tolls_amount").cast(DoubleType()),
        )
        .withColumn(
            "improvement_surcharge",
            F.col("improvement_surcharge").cast(DoubleType()),
        )
        .withColumn(
            "total_amount",
            F.col("total_amount").cast(DoubleType()),
        )
        # Remove original columns after renaming
        .drop(
            "VendorID",
            "tpep_pickup_datetime",
            "tpep_dropoff_datetime",
            "trip_distance",
            "extra",
            "mta_tax",
            "RateCodeID",
        )
    )

    return df_clean


def write_output_data(df, output_path):
    """Write cleaned data to Silver layer in Parquet format."""

    (df.coalesce(1).write.mode("overwrite").parquet(path=output_path))


def main():
    args = get_job_args()

    spark = create_spark_session()

    df = read_input_data(
        spark=spark,
        input_path=args["INPUT_PATH"],
    )

    df_clean = clean_data(df=df)

    write_output_data(
        df=df_clean,
        output_path=args["OUTPUT_PATH"],
    )

    spark.stop()


if __name__ == "__main__":
    main()
