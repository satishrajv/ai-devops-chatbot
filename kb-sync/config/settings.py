"""
Configuration Settings
Loads configuration from environment variables
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)


class Settings:
    """Application settings"""

    # AWS Configuration
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
    S3_KB_BUCKET = os.getenv('S3_KB_BUCKET', 'jenkins-kb')

    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_EMBEDDING_MODEL = os.getenv('OPENAI_EMBEDDING_MODEL', 'text-embedding-3-small')
    EMBEDDING_DIMENSION = int(os.getenv('EMBEDDING_DIMENSION', '1536'))

    # Weaviate Configuration
    WEAVIATE_URL = os.getenv('WEAVIATE_URL')
    WEAVIATE_API_KEY = os.getenv('WEAVIATE_API_KEY')
    WEAVIATE_COLLECTION_NAME = os.getenv('WEAVIATE_COLLECTION_NAME', 'JenkinsKnowledgeBase')

    # State Tracking
    STATE_DB_PATH = os.getenv('STATE_DB_PATH', 'kb_sync_state.db')

    def validate(self):
        """Validate required settings"""
        required = [
            'AWS_ACCESS_KEY_ID',
            'AWS_SECRET_ACCESS_KEY',
            'OPENAI_API_KEY',
            'WEAVIATE_URL',
            'WEAVIATE_API_KEY'
        ]

        missing = []
        for key in required:
            if not getattr(self, key):
                missing.append(key)

        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")


# Global settings instance
settings = Settings()
