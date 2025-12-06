"""
S3 utilities for file upload and download
"""

import boto3
import os
from botocore.exceptions import ClientError
from config import Config
from datetime import timedelta


def get_s3_client():
    """
    Create and return S3 client
    
    Returns:
        boto3 S3 client
    """
    if Config.AWS_ACCESS_KEY_ID and Config.AWS_SECRET_ACCESS_KEY:
        client_kwargs = {
            'region_name': Config.S3_REGION,
            'aws_access_key_id': Config.AWS_ACCESS_KEY_ID,
            'aws_secret_access_key': Config.AWS_SECRET_ACCESS_KEY
        }
        # Add session token if provided (required for temporary credentials)
        if Config.AWS_SESSION_TOKEN:
            client_kwargs['aws_session_token'] = Config.AWS_SESSION_TOKEN
        s3 = boto3.client('s3', **client_kwargs)
    else:
        s3 = boto3.client('s3', region_name=Config.S3_REGION)
    
    return s3


def upload_file_to_s3(file, folder_path=''):
    """
    Upload file to S3 bucket
    
    Args:
        file: File object (from Flask request.files)
        folder_path: Optional folder path within bucket
    
    Returns:
        Tuple (success, file_url or error_message)
    """
    try:
        s3_client = get_s3_client()
        
        # Generate unique filename
        filename = file.filename
        if folder_path:
            s3_key = f"{folder_path}/{filename}"
        else:
            s3_key = filename
        
        # Upload file
        s3_client.upload_fileobj(
            file,
            Config.S3_BUCKET_NAME,
            s3_key,
            ExtraArgs={'ContentType': file.content_type}
        )
        
        # Generate file URL
        file_url = f"https://{Config.S3_BUCKET_NAME}.s3.{Config.S3_REGION}.amazonaws.com/{s3_key}"
        
        return True, file_url
    
    except ClientError as e:
        return False, f"Error uploading file: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"


def generate_presigned_url(s3_key, expiration=3600):
    """
    Generate pre-signed URL for file download
    
    Args:
        s3_key: S3 object key (path to file)
        expiration: URL expiration time in seconds (default 1 hour)
    
    Returns:
        Pre-signed URL or None if error
    """
    try:
        s3_client = get_s3_client()
        
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': Config.S3_BUCKET_NAME, 'Key': s3_key},
            ExpiresIn=expiration
        )
        
        return url
    
    except ClientError as e:
        print(f"Error generating presigned URL: {str(e)}")
        return None


def delete_file_from_s3(s3_key):
    """
    Delete file from S3 bucket
    
    Args:
        s3_key: S3 object key (path to file)
    
    Returns:
        Tuple (success, error_message)
    """
    try:
        s3_client = get_s3_client()
        s3_client.delete_object(Bucket=Config.S3_BUCKET_NAME, Key=s3_key)
        return True, None
    except ClientError as e:
        return False, f"Error deleting file: {str(e)}"

