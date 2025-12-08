import boto3
from botocore.exceptions import ClientError
from config import Config


def get_s3_client():
    if Config.AWS_ACCESS_KEY_ID and Config.AWS_SECRET_ACCESS_KEY:
        client_kwargs = {
            "region_name": Config.S3_REGION,
            "aws_access_key_id": Config.AWS_ACCESS_KEY_ID,
            "aws_secret_access_key": Config.AWS_SECRET_ACCESS_KEY,
        }
        if Config.AWS_SESSION_TOKEN:
            client_kwargs["aws_session_token"] = Config.AWS_SESSION_TOKEN
        s3 = boto3.client("s3", **client_kwargs)
    else:
        s3 = boto3.client("s3", region_name=Config.S3_REGION)

    return s3


def upload_file_to_s3(file, folder_path=""):
    try:
        s3_client = get_s3_client()

        filename = file.filename
        if folder_path:
            s3_key = f"{folder_path}/{filename}"
        else:
            s3_key = filename

        s3_client.upload_fileobj(file, Config.S3_BUCKET_NAME, s3_key, ExtraArgs={"ContentType": file.content_type})

        file_url = f"https://{Config.S3_BUCKET_NAME}.s3.{Config.S3_REGION}.amazonaws.com/{s3_key}"

        return True, file_url

    except ClientError as error:
        return False, f"Error uploading file: {str(error)}"
    except Exception as error:
        return False, f"Unexpected error: {str(error)}"


def generate_presigned_url(s3_key, expiration=3600):
    try:
        s3_client = get_s3_client()

        url = s3_client.generate_presigned_url(
            "get_object", Params={"Bucket": Config.S3_BUCKET_NAME, "Key": s3_key}, ExpiresIn=expiration
        )

        return url

    except ClientError as error:
        print(f"Error generating presigned URL: {str(error)}")
        return None


def delete_file_from_s3(s3_key):
    try:
        s3_client = get_s3_client()
        s3_client.delete_object(Bucket=Config.S3_BUCKET_NAME, Key=s3_key)
        return True, None
    except ClientError as error:
        return False, f"Error deleting file: {str(error)}"
