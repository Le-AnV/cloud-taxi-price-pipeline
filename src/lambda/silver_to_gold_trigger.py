import os
import urllib.parse

import boto3

# Create Glue client
glue_client = boto3.client("glue")

# Read Glue Job name from environment variable
GLUE_JOB_NAME = os.environ["GLUE_JOB_NAME"]

SILVER_PREFIX = "silver/"
GOLD_PREFIX = "gold/"


def lambda_handler(event, context):
    """
    Triggered by S3 ObjectCreated event.
    Starts the Silver -> Gold Glue Job.
    """
    record = event["Records"][0]

    bucket_name = record["s3"]["bucket"]["name"]
    object_key = urllib.parse.unquote_plus(record["s3"]["object"]["key"])

    # Example:
    # silver/yellow_tripdata/year=2016/month=01/part-00000.parquet
    input_path = f"s3://{bucket_name}/{object_key}"

    response = glue_client.start_job_run(
        JobName=GLUE_JOB_NAME,
        Arguments={
            "--INPUT_PATH": input_path,
        },
    )

    return {
        "statusCode": 200,
        "jobRunId": response["JobRunId"],
        "inputPath": input_path,
    }
