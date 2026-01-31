"""
Agent 1: Query Processor
Cleans and embeds user questions
"""

import logging
from typing import Dict, List
from openai import OpenAI

logger = logging.getLogger(__name__)


class QueryProcessorAgent:
    """Processes user queries and generates embeddings"""

    def __init__(self, openai_api_key: str, embedding_model: str):
        self.client = OpenAI(api_key=openai_api_key)
        self.embedding_model = embedding_model

    def process_query(self, user_question: str) -> Dict:
        """
        Process user question and generate embedding

        Args:
            user_question: Raw user input

        Returns:
            Dict with processed_query and query_embedding
        """
        logger.info(f"[Query Processor] Processing question: {user_question}")

        try:
            # Clean and normalize query
            processed_query = self._clean_query(user_question)
            logger.debug(f"Cleaned query: {processed_query}")

            # Generate embedding
            embedding = self._generate_embedding(processed_query)
            logger.info(f"Generated {len(embedding)}-dimensional embedding")

            return {
                'processed_query': processed_query,
                'query_embedding': embedding,
                'original_question': user_question
            }

        except Exception as e:
            logger.error(f"Error processing query: {str(e)}", exc_info=True)
            raise

    def _clean_query(self, query: str) -> str:
        """Clean and normalize user query"""
        # Remove extra whitespace
        cleaned = ' '.join(query.split())

        # Ensure it ends with a question mark if it's a question
        if cleaned and not cleaned.endswith('?') and any(
            cleaned.lower().startswith(q) for q in ['what', 'how', 'why', 'when', 'where', 'who']
        ):
            cleaned += '?'

        return cleaned

    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding using OpenAI"""
        response = self.client.embeddings.create(
            model=self.embedding_model,
            input=text
        )
        return response.data[0].embedding
