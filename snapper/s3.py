import logging
import os
from pathlib import Path

import boto3
from botocore.exceptions import ClientError


class S3:
    _instance = None

    def __init__(self, aws_access_key_id, aws_secret_access_key, aws_bucker_name):
        self.aws_bucket_name = aws_bucker_name

        try:
            self.s3_client = boto3.client('s3', aws_access_key_id=aws_access_key_id,
                                          aws_secret_access_key=aws_secret_access_key)
            S3._instance = self
        except ClientError as e:
            logging.error(e.response['Error']['Message'])

    @staticmethod
    def get_instance():
        return S3._instance

    def upload_dir(self, source_dir, dest_dir):
        if self is None:
            logging.error("Storage is not initialized")
            return

        try:
            for root, dirs, files in os.walk(source_dir):
                for filename in files:
                    local_path = Path(root) / filename
                    relative_path = local_path.relative_to(source_dir)
                    s3_path = Path(dest_dir) / relative_path

                    with open(local_path, 'rb') as file_to_upload:
                        self.s3_client.put_object(Bucket=self.aws_bucket_name, Key=str(s3_path),
                                                  Body=file_to_upload.read())
        except ClientError as e:
            logging.error(e.response['Error']['Message'])
