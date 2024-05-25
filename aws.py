import boto3
import mcdiscord.config as config
import io
import logging
from botocore.exceptions import ClientError
import os


def upload_file(s3_client, file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True


def create_presigned_url(s3_client, bucket_name, object_name, expiration=3600):
    """Generate a presigned URL to share an S3 object

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """

    # Generate a presigned URL for the S3 object
    try:
        response = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket_name, "Key": object_name},
            ExpiresIn=expiration,
        )
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response


def create_presigned_url(s3_client, bucket_name, object_name, expiration=3600):
    """Generate a presigned URL to share an S3 object

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """

    # Generate a presigned URL for the S3 object
    try:
        response = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket_name, "Key": object_name},
            ExpiresIn=expiration,
        )
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response


def upload_and_get_url(s3_client, bucket_name, object_name, expiration=3600):
    """Upload a file to an S3 bucket and generate a presigned URL

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """

    # Upload the file
    if not upload_file(s3_client, object_name, bucket_name):
        return None

    # Generate a presigned URL
    return create_presigned_url(s3_client, bucket_name, object_name, expiration)


if __name__ == "__main__":
    s3_client = boto3.client(
        service_name="s3",
        endpoint_url=config.S3_URL,
        aws_access_key_id=config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
        region_name="auto",
    )
    url = upload_and_get_url(s3_client, config.BUCKET_NAME, "test.zip")
    print(url)
