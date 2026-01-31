"""
Agent 4: Weaviate Uploader
Uploads documents with embeddings to Weaviate
"""

import weaviate
from weaviate.classes.init import Auth
from weaviate.classes.config import Configure, Property, DataType
from typing import Dict, Any
import logging
from config.settings import settings
from utils.state_tracker import StateTracker

logger = logging.getLogger(__name__)


class WeaviateUploaderAgent:
    """Agent responsible for uploading documents to Weaviate"""

    def __init__(self):
        self.client = None
        self.collection_name = settings.WEAVIATE_COLLECTION_NAME
        self.state_tracker = StateTracker()
        self._connect()
        self._ensure_schema()

    def _connect(self):
        """Connect to Weaviate cluster"""
        try:
            logger.info(f"Connecting to Weaviate: {settings.WEAVIATE_URL}")

            self.client = weaviate.connect_to_weaviate_cloud(
                cluster_url=settings.WEAVIATE_URL,
                auth_credentials=Auth.api_key(settings.WEAVIATE_API_KEY),
                skip_init_checks=True
            )

            logger.info("Successfully connected to Weaviate")

        except Exception as e:
            logger.error(f"Failed to connect to Weaviate: {str(e)}", exc_info=True)
            raise

    def _ensure_schema(self):
        """Create collection schema if it doesn't exist"""
        try:
            # Check if collection exists
            collections = self.client.collections.list_all()

            if self.collection_name in collections:
                logger.info(f"Collection '{self.collection_name}' already exists")
                return

            logger.info(f"Creating collection: {self.collection_name}")

            # Create collection with schema
            self.client.collections.create(
                name=self.collection_name,
                description="Jenkins error knowledge base documents",
                vectorizer_config=Configure.Vectorizer.none(),  # We provide embeddings
                properties=[
                    Property(
                        name="file_name",
                        data_type=DataType.TEXT,
                        description="Name of the markdown file"
                    ),
                    Property(
                        name="s3_key",
                        data_type=DataType.TEXT,
                        description="S3 object key"
                    ),
                    Property(
                        name="title",
                        data_type=DataType.TEXT,
                        description="Document title"
                    ),
                    Property(
                        name="error_id",
                        data_type=DataType.TEXT,
                        description="Error identifier (e.g., ERROR-001)"
                    ),
                    Property(
                        name="error_name",
                        data_type=DataType.TEXT,
                        description="Human-readable error name"
                    ),
                    Property(
                        name="category",
                        data_type=DataType.TEXT,
                        description="Error category"
                    ),
                    Property(
                        name="severity",
                        data_type=DataType.TEXT,
                        description="Error severity level"
                    ),
                    Property(
                        name="quick_summary",
                        data_type=DataType.TEXT,
                        description="Quick summary of the issue"
                    ),
                    Property(
                        name="symptoms",
                        data_type=DataType.TEXT,
                        description="Observable symptoms"
                    ),
                    Property(
                        name="error_messages",
                        data_type=DataType.TEXT,
                        description="Actual error messages"
                    ),
                    Property(
                        name="root_cause",
                        data_type=DataType.TEXT,
                        description="Root cause analysis"
                    ),
                    Property(
                        name="resolution_steps",
                        data_type=DataType.TEXT,
                        description="How to fix the issue"
                    ),
                    Property(
                        name="prevention",
                        data_type=DataType.TEXT,
                        description="Prevention strategies"
                    ),
                    Property(
                        name="tags",
                        data_type=DataType.TEXT_ARRAY,
                        description="Searchable tags"
                    ),
                    Property(
                        name="raw_content",
                        data_type=DataType.TEXT,
                        description="Full markdown content"
                    ),
                    Property(
                        name="last_modified",
                        data_type=DataType.TEXT,
                        description="Last modification timestamp"
                    ),
                    Property(
                        name="etag",
                        data_type=DataType.TEXT,
                        description="S3 ETag for change tracking"
                    )
                ]
            )

            logger.info(f"Successfully created collection: {self.collection_name}")

        except Exception as e:
            logger.error(f"Error ensuring schema: {str(e)}", exc_info=True)
            raise

    def upload_document(self, embedded_doc: Dict[str, Any]) -> Dict[str, str]:
        """
        Upload a single document to Weaviate
        Returns upload status
        """
        file_name = embedded_doc['file_name']
        logger.info(f"Uploading document to Weaviate: {file_name}")

        try:
            collection = self.client.collections.get(self.collection_name)

            # Prepare properties
            sections = embedded_doc.get('sections', {})

            properties = {
                "file_name": embedded_doc.get('file_name', ''),
                "s3_key": embedded_doc.get('s3_key', ''),
                "title": embedded_doc.get('title', ''),
                "error_id": embedded_doc.get('error_id', ''),
                "error_name": embedded_doc.get('error_name', ''),
                "category": embedded_doc.get('category', ''),
                "severity": embedded_doc.get('severity', ''),
                "quick_summary": embedded_doc.get('quick_summary', ''),
                "symptoms": sections.get('symptoms', ''),
                "error_messages": sections.get('error_messages', ''),
                "root_cause": sections.get('root_cause', ''),
                "resolution_steps": sections.get('resolution_steps', ''),
                "prevention": sections.get('prevention', ''),
                "tags": embedded_doc.get('tags', []),
                "raw_content": embedded_doc.get('raw_content', ''),
                "last_modified": embedded_doc.get('last_modified', ''),
                "etag": embedded_doc.get('etag', '')
            }

            # Get embedding vector
            vector = embedded_doc.get('embedding')
            if not vector:
                raise ValueError(f"No embedding found for {file_name}")

            # Check if document already exists (by s3_key)
            existing = collection.query.fetch_objects(
                filters={
                    "path": ["s3_key"],
                    "operator": "Equal",
                    "valueText": properties["s3_key"]
                },
                limit=1
            )

            if existing.objects:
                # Update existing document
                doc_id = existing.objects[0].uuid
                collection.data.update(
                    uuid=doc_id,
                    properties=properties,
                    vector=vector
                )
                logger.info(f"Updated existing document: {file_name} (UUID: {doc_id})")
                status = "updated"
            else:
                # Insert new document
                doc_id = collection.data.insert(
                    properties=properties,
                    vector=vector
                )
                logger.info(f"Inserted new document: {file_name} (UUID: {doc_id})")
                status = "inserted"

            # Update state tracker
            self.state_tracker.update_file_state(
                s3_key=embedded_doc['s3_key'],
                etag=embedded_doc['etag'],
                weaviate_uuid=str(doc_id)
            )

            return {
                "status": "success",
                "action": status,
                "file_name": file_name,
                "uuid": str(doc_id)
            }

        except Exception as e:
            logger.error(f"Error uploading document {file_name}: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "action": "failed",
                "file_name": file_name,
                "error": str(e)
            }

    def close(self):
        """Close Weaviate connection"""
        if self.client:
            self.client.close()
            logger.info("Closed Weaviate connection")

    def __del__(self):
        """Cleanup on deletion"""
        self.close()
