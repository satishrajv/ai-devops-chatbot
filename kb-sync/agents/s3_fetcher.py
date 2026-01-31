"""
Agent 1: S3 Fetcher
Downloads markdown files from S3 bucket and checks for changes
"""

import boto3
from typing import List, Dict, Any
import logging
from config.settings import settings
from utils.state_tracker import StateTracker

logger = logging.getLogger(__name__)


class S3FetcherAgent:
    """Agent responsible for fetching markdown files from S3"""

    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.bucket_name = settings.S3_KB_BUCKET
        self.state_tracker = StateTracker()

    def fetch_new_files(self) -> List[Dict[str, Any]]:
        """
        Fetch all markdown files from S3 that are new or modified
        Returns list of file metadata
        """
        logger.info(f"Fetching files from S3 bucket: {self.bucket_name}")

        try:
            # List all objects in the bucket
            response = self.s3_client.list_objects_v2(Bucket=self.bucket_name)

            if 'Contents' not in response:
                logger.info("No files found in S3 bucket")
                return []

            new_or_modified_files = []

            for obj in response['Contents']:
                key = obj['Key']

                # Only process markdown files
                if not key.endswith('.md'):
                    logger.debug(f"Skipping non-markdown file: {key}")
                    continue

                etag = obj['ETag'].strip('"')
                last_modified = obj['LastModified']

                # Check if file is new or modified
                if self.state_tracker.is_file_changed(key, etag):
                    logger.info(f"File changed: {key} (ETag: {etag})")

                    # Download file content
                    file_obj = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
                    content = file_obj['Body'].read().decode('utf-8')

                    new_or_modified_files.append({
                        'file_name': key,
                        's3_key': key,
                        'etag': etag,
                        'last_modified': last_modified.isoformat(),
                        'content': content,
                        'size_bytes': obj['Size']
                    })
                else:
                    logger.debug(f"File unchanged: {key}")

            logger.info(f"Found {len(new_or_modified_files)} new/modified files")
            return new_or_modified_files

        except Exception as e:
            logger.error(f"Error fetching files from S3: {str(e)}", exc_info=True)
            raise

    def get_file_content(self, s3_key: str) -> str:
        """Download specific file content from S3"""
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=s3_key)
            return response['Body'].read().decode('utf-8')
        except Exception as e:
            logger.error(f"Error downloading file {s3_key}: {str(e)}")
            raise
