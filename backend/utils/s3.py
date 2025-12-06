import boto3
import os
from botocore.exceptions import ClientError
from config import Config
from datetime import timedelta


def get_s3_client():
    # create s3 client with aws credentials
    if Config.AWS_ACCESS_KEY_ID and Config.AWS_SECRET_ACCESS_KEY:
        client_kwargs = {
            'region_name': Config.S3_REGION,
            'aws_access_key_id': Config.AWS_ACCESS_KEY_ID,
            'aws_secret_access_key': Config.AWS_SECRET_ACCESS_KEY
        }
        # add session token if we have it
        if Config.AWS_SESSION_TOKEN:
            client_kwargs['aws_session_token'] = Config.AWS_SESSION_TOKEN
        s3 = boto3.client('s3', **client_kwargs)
    else:
        s3 = boto3.client('s3', region_name=Config.S3_REGION)

    return s3


def upload_file_to_s3(file, folder_path=''):
    # upload file to s3 bucket
    try:
        s3_client = get_s3_client()

        # get filename and create s3 key
        filename = file.filename
        if folder_path:
            s3_key = f"{folder_path}/{filename}"
        else:
            s3_key = filename

        # upload the file
        s3_client.upload_fileobj(
            file,
            Config.S3_BUCKET_NAME,
            s3_key,
            ExtraArgs={'ContentType': file.content_type}
        )

        # create url for the file
        file_url = f"https://{Config.S3_BUCKET_NAME}.s3.{Config.S3_REGION}.amazonaws.com/{s3_key}"

        return True, file_url

    except ClientError as error:
        return False, f"Error uploading file: {str(error)}"
    except Exception as error:
        return False, f"Unexpected error: {str(error)}"


def generate_presigned_url(s3_key, expiration=3600):
    # create a temporary url to download file
    try:
        s3_client = get_s3_client()

        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': Config.S3_BUCKET_NAME, 'Key': s3_key},
            ExpiresIn=expiration
        )

        return url

    except ClientError as error:
        print(f"Error generating presigned URL: {str(error)}")
        return None


def delete_file_from_s3(s3_key):
    # delete file from s3
    try:
        s3_client = get_s3_client()
        s3_client.delete_object(Bucket=Config.S3_BUCKET_NAME, Key=s3_key)
        return True, None
    except ClientError as error:
        return False, f"Error deleting file: {str(error)}"
