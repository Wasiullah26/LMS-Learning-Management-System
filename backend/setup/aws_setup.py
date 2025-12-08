import boto3
import os
import sys
from botocore.exceptions import ClientError
from datetime import datetime
from dotenv import load_dotenv

import pathlib

env_path = pathlib.Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_SESSION_TOKEN = os.getenv("AWS_SESSION_TOKEN")

DYNAMODB_TABLES = {
    "users": {
        "TableName": "lms-users",
        "KeySchema": [{"AttributeName": "userId", "KeyType": "HASH"}],
        "AttributeDefinitions": [{"AttributeName": "userId", "AttributeType": "S"}],
        "BillingMode": "PAY_PER_REQUEST",
    },
    "courses": {
        "TableName": "lms-courses",
        "KeySchema": [{"AttributeName": "courseId", "KeyType": "HASH"}],
        "AttributeDefinitions": [{"AttributeName": "courseId", "AttributeType": "S"}],
        "BillingMode": "PAY_PER_REQUEST",
    },
    "modules": {
        "TableName": "lms-modules",
        "KeySchema": [
            {"AttributeName": "moduleId", "KeyType": "HASH"},
            {"AttributeName": "courseId", "KeyType": "RANGE"},
        ],
        "AttributeDefinitions": [
            {"AttributeName": "moduleId", "AttributeType": "S"},
            {"AttributeName": "courseId", "AttributeType": "S"},
        ],
        "BillingMode": "PAY_PER_REQUEST",
    },
    "enrollments": {
        "TableName": "lms-enrollments",
        "KeySchema": [
            {"AttributeName": "enrollmentId", "KeyType": "HASH"},
            {"AttributeName": "studentId", "KeyType": "RANGE"},
        ],
        "AttributeDefinitions": [
            {"AttributeName": "enrollmentId", "AttributeType": "S"},
            {"AttributeName": "studentId", "AttributeType": "S"},
        ],
        "BillingMode": "PAY_PER_REQUEST",
    },
    "progress": {
        "TableName": "lms-progress",
        "KeySchema": [
            {"AttributeName": "progressId", "KeyType": "HASH"},
            {"AttributeName": "studentId", "KeyType": "RANGE"},
        ],
        "AttributeDefinitions": [
            {"AttributeName": "progressId", "AttributeType": "S"},
            {"AttributeName": "studentId", "AttributeType": "S"},
        ],
        "BillingMode": "PAY_PER_REQUEST",
    },
    "specializations": {
        "TableName": "lms-specializations",
        "KeySchema": [{"AttributeName": "specializationId", "KeyType": "HASH"}],
        "AttributeDefinitions": [{"AttributeName": "specializationId", "AttributeType": "S"}],
        "BillingMode": "PAY_PER_REQUEST",
    },
}

S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "lms-course-materials")


def create_dynamodb_client():
    try:
        if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
            client_kwargs = {
                "region_name": AWS_REGION,
                "aws_access_key_id": AWS_ACCESS_KEY_ID,
                "aws_secret_access_key": AWS_SECRET_ACCESS_KEY,
            }
            if AWS_SESSION_TOKEN:
                client_kwargs["aws_session_token"] = AWS_SESSION_TOKEN
            dynamodb = boto3.client("dynamodb", **client_kwargs)
        else:
            dynamodb = boto3.client("dynamodb", region_name=AWS_REGION)
        return dynamodb
    except Exception as error:
        print(f"Error creating DynamoDB client: {str(error)}")
        sys.exit(1)


def create_s3_client():
    try:
        if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
            client_kwargs = {
                "region_name": AWS_REGION,
                "aws_access_key_id": AWS_ACCESS_KEY_ID,
                "aws_secret_access_key": AWS_SECRET_ACCESS_KEY,
            }
            if AWS_SESSION_TOKEN:
                client_kwargs["aws_session_token"] = AWS_SESSION_TOKEN
            s3 = boto3.client("s3", **client_kwargs)
        else:
            s3 = boto3.client("s3", region_name=AWS_REGION)
        return s3
    except Exception as error:
        print(f"Error creating S3 client: {str(error)}")
        sys.exit(1)


def table_exists(dynamodb, table_name):
    try:
        dynamodb.describe_table(TableName=table_name)
        return True
    except ClientError as error:
        if error.response["Error"]["Code"] == "ResourceNotFoundException":
            return False
        else:
            raise


def create_dynamodb_table(dynamodb, table_config, silent=False):
    table_name = table_config["TableName"]

    if table_exists(dynamodb, table_name):
        if not silent:
            print(f"✓ Table '{table_name}' already exists")
        return True

    try:
        if not silent:
            print(f"Creating table '{table_name}'...")
        dynamodb.create_table(**table_config)

        waiter = dynamodb.get_waiter("table_exists")
        waiter.wait(TableName=table_name)

        if not silent:
            print(f"✓ Successfully created table '{table_name}'")
        return True
    except ClientError as error:
        error_code = error.response["Error"]["Code"]
        if error_code == "ResourceInUseException":
            if not silent:
                print(f"✓ Table '{table_name}' already exists")
            return True
        else:
            if not silent:
                print(f"✗ Error creating table '{table_name}': {str(error)}")
            return False


def bucket_exists(s3, bucket_name):
    try:
        s3.head_bucket(Bucket=bucket_name)
        return True
    except ClientError as error:
        error_code = error.response["Error"]["Code"]
        if error_code == "404":
            return False
        else:
            raise


def create_s3_bucket(s3, bucket_name, silent=False):
    if bucket_exists(s3, bucket_name):
        if not silent:
            print(f"✓ Bucket '{bucket_name}' already exists")
        return True

    try:
        if not silent:
            print(f"Creating S3 bucket '{bucket_name}'...")

        if AWS_REGION == "us-east-1":
            s3.create_bucket(Bucket=bucket_name)
        else:
            s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={"LocationConstraint": AWS_REGION})

        if not silent:
            print(f"✓ Successfully created bucket '{bucket_name}'")

        cors_configuration = {
            "CORSRules": [
                {
                    "AllowedHeaders": ["*"],
                    "AllowedMethods": ["GET", "PUT", "POST", "DELETE", "HEAD"],
                    "AllowedOrigins": ["*"],
                    "ExposeHeaders": ["ETag"],
                    "MaxAgeSeconds": 3000,
                }
            ]
        }
        s3.put_bucket_cors(Bucket=bucket_name, CORSConfiguration=cors_configuration)
        if not silent:
            print(f"✓ Configured CORS for bucket '{bucket_name}'")

        return True
    except ClientError as error:
        error_code = error.response["Error"]["Code"]
        if error_code == "BucketAlreadyExists":
            if not silent:
                print(f"✓ Bucket '{bucket_name}' already exists")
            return True
        elif error_code == "BucketAlreadyOwnedByYou":
            if not silent:
                print(f"✓ Bucket '{bucket_name}' already exists and is owned by you")
            return True
        else:
            if not silent:
                print(f"✗ Error creating bucket '{bucket_name}': {str(error)}")
            return False


def setup_aws_resources(silent=False):
    try:
        if not silent:
            print("Checking AWS resources...")

        dynamodb = create_dynamodb_client()
        s3 = create_s3_client()

        tables_created = 0
        for table_config in DYNAMODB_TABLES.values():
            if create_dynamodb_table(dynamodb, table_config, silent=silent):
                tables_created += 1

        bucket_created = create_s3_bucket(s3, S3_BUCKET_NAME, silent=silent)

        if tables_created == len(DYNAMODB_TABLES) and bucket_created:
            if not silent:
                print("✓ All AWS resources are ready")
            return True, "All resources ready"
        else:
            return False, "Some resources failed to create"

    except Exception as error:
        error_msg = f"Error setting up AWS resources: {str(error)}"
        if not silent:
            print(f"⚠ {error_msg}")
        return False, error_msg


def main():
    print("=" * 60)
    print("AWS Infrastructure Setup for LMS Application")
    print("=" * 60)
    print(f"Region: {AWS_REGION}")
    print(f"S3 Bucket: {S3_BUCKET_NAME}")
    print("=" * 60)
    print()

    if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
        print("Warning: AWS credentials not found in environment variables.")
        print("Using default credential chain (IAM role, etc.)")
        print()

    dynamodb = create_dynamodb_client()
    s3 = create_s3_client()

    print("Creating DynamoDB tables...")
    print("-" * 60)
    tables_created = 0
    for table_config in DYNAMODB_TABLES.values():
        if create_dynamodb_table(dynamodb, table_config, silent=False):
            tables_created += 1
        print()

    print("Creating S3 bucket...")
    print("-" * 60)
    bucket_created = create_s3_bucket(s3, S3_BUCKET_NAME, silent=False)
    print()

    print("=" * 60)
    print("Setup Summary")
    print("=" * 60)
    print(f"DynamoDB Tables: {tables_created}/{len(DYNAMODB_TABLES)} created/verified")
    print(f"S3 Bucket: {'Created/Verified' if bucket_created else 'Failed'}")
    print("=" * 60)

    if tables_created == len(DYNAMODB_TABLES) and bucket_created:
        print("\n✓ All resources created successfully!")
        print("\nNext steps:")
        print("1. Set up your Flask application")
        print("2. Configure environment variables")
        print("3. Start developing your LMS features")
    else:
        print("\n⚠ Some resources may not have been created. Please check the errors above.")


if __name__ == "__main__":
    main()
