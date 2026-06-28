import os
import urllib.parse

import boto3

# Create Glue client
glue_client = boto3.client("glue")

# Read Glue Job name from environment variable
GLUE_JOB_NAME = os.environ["GLUE_JOB_NAME"]

BRONZE_PREFIX = "bronze/"
SILVER_PREFIX = "silver/"


def build_silver_output_path(bucket_name: str, object_key: str) -> str:
    """
    Build the Silver output directory from a Bronze object key, keeping the
    year/month partition structure.

    Example:
        bronze/year=2015/month=01/data.csv
        -> s3://<bucket>/silver/year=2015/month=01/
    """
    if not object_key.startswith(BRONZE_PREFIX):
        raise ValueError(
            f"Object key does not start with '{BRONZE_PREFIX}': {object_key}"
        )

    silver_key = object_key.replace(BRONZE_PREFIX, SILVER_PREFIX, 1)
    silver_directory = silver_key.rsplit("/", 1)[0]

    return f"s3://{bucket_name}/{silver_directory}/"


def lambda_handler(event, context):
    """
    Triggered by S3 ObjectCreated event.
    Starts the Bronze -> Silver Glue Job.
    """
    record = event["Records"][0]

    bucket_name = record["s3"]["bucket"]["name"]
    object_key = urllib.parse.unquote_plus(record["s3"]["object"]["key"])

    input_path = f"s3://{bucket_name}/{object_key}"
    output_path = build_silver_output_path(bucket_name, object_key)

    response = glue_client.start_job_run(
        JobName=GLUE_JOB_NAME,
        Arguments={
            "--INPUT_PATH": input_path,
            "--OUTPUT_PATH": output_path,
        },
    )

    return {
        "statusCode": 200,
        "jobRunId": response["JobRunId"],
        "inputPath": input_path,
        "outputPath": output_path,
    }
