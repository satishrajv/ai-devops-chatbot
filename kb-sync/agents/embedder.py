"""
Agent 3: Embedder
Generates vector embeddings using OpenAI
"""

from openai import OpenAI
from typing import Dict, Any, List
import logging
from config.settings import settings

logger = logging.getLogger(__name__)


class EmbedderAgent:
    """Agent responsible for generating embeddings"""

    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_EMBEDDING_MODEL
        self.embedding_dimension = settings.EMBEDDING_DIMENSION

    def generate_embeddings(self, parsed_doc: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate vector embeddings for the document
        Returns document with embeddings added
        """
        file_name = parsed_doc['file_name']
        logger.info(f"Generating embeddings for: {file_name}")

        try:
            # Get the text to embed
            text_to_embed = parsed_doc.get('embedding_text', parsed_doc.get('raw_content', ''))

            if not text_to_embed:
                raise ValueError(f"No text to embed for {file_name}")

            # Truncate if too long (OpenAI limit is ~8000 tokens, ~32000 chars)
            max_chars = 30000
            if len(text_to_embed) > max_chars:
                logger.warning(f"Text too long ({len(text_to_embed)} chars), truncating to {max_chars}")
                text_to_embed = text_to_embed[:max_chars]

            # Generate embedding
            response = self.client.embeddings.create(
                model=self.model,
                input=text_to_embed
            )

            embedding = response.data[0].embedding

            # Verify dimension
            if len(embedding) != self.embedding_dimension:
                raise ValueError(f"Expected {self.embedding_dimension} dimensions, got {len(embedding)}")

            # Add embedding to document
            embedded_doc = parsed_doc.copy()
            embedded_doc['embedding'] = embedding
            embedded_doc['embedding_model'] = self.model
            embedded_doc['embedding_dimension'] = len(embedding)

            logger.info(f"Successfully generated {len(embedding)}-dimensional embedding for: {file_name}")

            return embedded_doc

        except Exception as e:
            logger.error(f"Error generating embeddings for {file_name}: {str(e)}", exc_info=True)
            raise

    def generate_batch_embeddings(self, parsed_docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate embeddings for multiple documents in batch
        More efficient for large numbers of documents
        """
        logger.info(f"Generating batch embeddings for {len(parsed_docs)} documents")

        try:
            texts = []
            for doc in parsed_docs:
                text = doc.get('embedding_text', doc.get('raw_content', ''))
                if len(text) > 30000:
                    text = text[:30000]
                texts.append(text)

            # Batch API call
            response = self.client.embeddings.create(
                model=self.model,
                input=texts
            )

            embedded_docs = []
            for i, doc in enumerate(parsed_docs):
                embedded_doc = doc.copy()
                embedded_doc['embedding'] = response.data[i].embedding
                embedded_doc['embedding_model'] = self.model
                embedded_doc['embedding_dimension'] = len(response.data[i].embedding)
                embedded_docs.append(embedded_doc)

            logger.info(f"Successfully generated batch embeddings for {len(embedded_docs)} documents")

            return embedded_docs

        except Exception as e:
            logger.error(f"Error generating batch embeddings: {str(e)}", exc_info=True)
            raise
