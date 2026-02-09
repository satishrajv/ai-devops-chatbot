"""
Agent 2: RAG Retriever
Searches Weaviate for relevant document chunks
"""

import logging
from typing import List, Dict
import weaviate
from weaviate.classes.init import Auth

logger = logging.getLogger(__name__)


class RAGRetrieverAgent:
    """Retrieves relevant chunks from Weaviate vector database"""

    def __init__(self, weaviate_url: str, weaviate_api_key: str, collection_name: str):
        self.weaviate_url = weaviate_url
        self.weaviate_api_key = weaviate_api_key
        self.collection_name = collection_name

    def retrieve(self, query_embedding: List[float], top_k: int = 3, distance_threshold: float = 0.7) -> Dict:
        """
        Retrieve relevant chunks from Weaviate

        Args:
            query_embedding: Vector embedding of the query
            top_k: Number of chunks to retrieve
            distance_threshold: Maximum distance (lower = more similar)

        Returns:
            Dict with retrieved_chunks and metadata
        """
        logger.info(f"[RAG Retriever] Searching for top {top_k} chunks")

        client = None
        try:
            # Connect to Weaviate
            client = weaviate.connect_to_weaviate_cloud(
                cluster_url=self.weaviate_url,
                auth_credentials=Auth.api_key(self.weaviate_api_key),
                skip_init_checks=True
            )

            logger.debug(f"Connected to Weaviate: {self.weaviate_url}")

            # Get collection
            collection = client.collections.get(self.collection_name)

            # Search by vector similarity
            results = collection.query.near_vector(
                near_vector=query_embedding,
                limit=top_k,
                return_metadata=['distance']
            )

            # Process results
            retrieved_chunks = []
            for i, obj in enumerate(results.objects):
                distance = obj.metadata.distance

                # Filter by distance threshold
                if distance <= distance_threshold:
                    chunk = {
                        'filename': obj.properties['filename'],
                        'chunk_id': obj.properties['chunk_id'],
                        'text': obj.properties['text'],
                        'distance': distance,
                        'rank': i + 1
                    }
                    retrieved_chunks.append(chunk)

                    logger.debug(f"Chunk {i+1}: {obj.properties['filename']} (distance: {distance:.4f})")

            logger.info(f"Retrieved {len(retrieved_chunks)} chunks (threshold: {distance_threshold})")

            return {
                'retrieved_chunks': retrieved_chunks,
                'total_searched': len(results.objects),
                'total_relevant': len(retrieved_chunks)
            }

        except Exception as e:
            logger.error(f"Error retrieving from Weaviate: {str(e)}", exc_info=True)
            raise
        finally:
            if client:
                client.close()
