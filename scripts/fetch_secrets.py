#!/usr/bin/env python3
"""
Fetch credentials from AWS Secrets Manager
This script is run inside the Docker container to fetch secrets at runtime
"""
import boto3
import json
import os
import sys
from botocore.exceptions import ClientError

def get_secret(secret_name: str, region_name: str = "us-east-1") -> dict:
    """
    Retrieve secret from AWS Secrets Manager

    Args:
        secret_name: Name of the secret in AWS Secrets Manager
        region_name: AWS region where secret is stored

    Returns:
        Dictionary containing the secret values
    """
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        print(f"❌ Error retrieving secret '{secret_name}': {e}", file=sys.stderr)
        raise e
    else:
        # Secrets Manager returns the secret as a string
        # Parse it as JSON
        secret = json.loads(get_secret_value_response['SecretString'])
        return secret


def export_secrets_to_env(secret_name: str = "ai-devops-platform/credentials"):
    """
    Fetch secrets and export them as environment variables
    Prints export commands that can be sourced in bash
    """
    try:
        secrets = get_secret(secret_name)

        # Print export statements
        for key, value in secrets.items():
            # Sanitize the value (escape quotes and special chars)
            safe_value = value.replace('"', '\\"').replace('$', '\\$').replace('`', '\\`')
            print(f'export {key}="{safe_value}"')

        return 0
    except Exception as e:
        print(f"❌ Failed to fetch secrets: {e}", file=sys.stderr)
        return 1


def validate_required_secrets(secrets: dict) -> bool:
    """
    Validate that all required secrets are present
    """
    required_keys = [
        'OPENAI_API_KEY',
        'WEAVIATE_URL',
        'WEAVIATE_API_KEY',
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY',
        'JENKINS_USER',
        'JENKINS_TOKEN'
    ]

    missing = [key for key in required_keys if key not in secrets]

    if missing:
        print(f"❌ Missing required secrets: {', '.join(missing)}", file=sys.stderr)
        return False

    return True


if __name__ == "__main__":
    # Get secret name from environment or use default
    secret_name = os.getenv("SECRET_NAME", "ai-devops-platform/credentials")
    region = os.getenv("AWS_REGION", "us-east-1")

    # Fetch and export secrets
    exit_code = export_secrets_to_env(secret_name)
    sys.exit(exit_code)
