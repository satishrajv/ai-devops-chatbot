"""
Production RAG System - Query Engine

Retrieves relevant knowledge base chunks and generates answers using LLM.
Features:
- Semantic search in Weaviate vector database
- OpenAI GPT-4o-mini for answer generation
- Multi-level logging (all/info/error log files)
- Distance-based relevance scoring
- Token usage tracking
- Production-ready error handling
"""

import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
import weaviate
from weaviate.classes.init import Auth

# ============================================
# LOGGING CONFIGURATION - Production Grade
# ============================================

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Generate timestamp for log files
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

# Define log file paths
log_all = f"logs/rag_query_{timestamp}_all.log"
log_error = f"logs/rag_query_{timestamp}_error.log"
log_info = f"logs/rag_query_{timestamp}_info.log"

# Configure logging with multiple handlers
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Capture everything

# Formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Handler 1: ALL logs (DEBUG and above) - Complete audit trail
handler_all = logging.FileHandler(log_all)
handler_all.setLevel(logging.DEBUG)
handler_all.setFormatter(formatter)
logger.addHandler(handler_all)

# Handler 2: INFO logs only - Important operations
handler_info = logging.FileHandler(log_info)
handler_info.setLevel(logging.INFO)
handler_info.setFormatter(formatter)
logger.addHandler(handler_info)

# Handler 3: ERROR and WARNING logs only - Issues only
handler_error = logging.FileHandler(log_error)
handler_error.setLevel(logging.WARNING)
handler_error.setFormatter(formatter)
logger.addHandler(handler_error)

# Handler 4: Console - INFO and above only
handler_console = logging.StreamHandler()
handler_console.setLevel(logging.INFO)
handler_console.setFormatter(formatter)
logger.addHandler(handler_console)

# Log startup
logger.info("="*60)
logger.info("RAG Query System Started")
logger.info(f"All logs: {log_all}")
logger.info(f"Info logs: {log_info}")
logger.info(f"Error logs: {log_error}")
logger.info("="*60)

# ============================================
# CONFIGURATION - Load from .env file
# ============================================

load_dotenv()

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Weaviate
WEAVIATE_URL = os.getenv("WEAVIATE_URL")
WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY")
COLLECTION_NAME = os.getenv("WEAVIATE_COLLECTION_NAME", "JenkinsKB")


# ============================================
# STEP 2: RETRIEVAL (ONLINE) - QUERY PHASE
# ============================================

def step5_query_embedding(user_question):
    """
    Convert user question to embedding
    """
    logger.info("[STEP 5] Generate Query Embedding")
    logger.info("="*60)
    logger.info(f"Question: {user_question}")

    try:
        client = OpenAI(api_key=OPENAI_API_KEY)

        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=user_question
        )

        embedding = response.data[0].embedding

        logger.info(f"Generated {len(embedding)}-dimensional embedding")
        logger.debug(f"Embedding preview: {embedding[:5]}...")
        return embedding

    except Exception as e:
        logger.error(f"Error generating query embedding: {str(e)}", exc_info=True)
        raise


def step6_vector_search(query_embedding, top_k=3):
    """
    Search Weaviate for similar chunks
    """
    logger.info("[STEP 6] Vector Search in Weaviate")
    logger.info("="*60)
    logger.info(f"Searching for top {top_k} most relevant chunks")

    try:
        # Connect to Weaviate
        logger.info(f"Connecting to Weaviate cluster: {WEAVIATE_URL}")
        client = weaviate.connect_to_weaviate_cloud(
            cluster_url=WEAVIATE_URL,
            auth_credentials=Auth.api_key(WEAVIATE_API_KEY),
            skip_init_checks=True
        )
        logger.info("Successfully connected to Weaviate")

        # Get collection
        collection = client.collections.get(COLLECTION_NAME)
        logger.debug(f"Accessing collection: {COLLECTION_NAME}")

        # Search by vector similarity
        results = collection.query.near_vector(
            near_vector=query_embedding,
            limit=top_k,
            return_metadata=['distance']
        )

        logger.info(f"Found {len(results.objects)} relevant chunks")

        retrieved_chunks = []
        for i, obj in enumerate(results.objects):
            logger.info(f"Result {i+1}:")
            logger.info(f"  File: {obj.properties['filename']}")
            logger.info(f"  Chunk ID: {obj.properties['chunk_id']}")
            logger.info(f"  Distance: {obj.metadata.distance:.4f}")
            logger.debug(f"  Text preview: {obj.properties['text'][:100]}...")

            retrieved_chunks.append({
                'filename': obj.properties['filename'],
                'chunk_id': obj.properties['chunk_id'],
                'text': obj.properties['text'],
                'distance': obj.metadata.distance
            })

        client.close()
        logger.info("Weaviate connection closed")
        return retrieved_chunks

    except Exception as e:
        logger.error(f"Error during vector search: {str(e)}", exc_info=True)
        raise


def step7_generate_answer(user_question, retrieved_chunks):
    """
    Use OpenAI to generate answer based on retrieved context
    """
    logger.info("[STEP 7] Generate Answer with LLM")
    logger.info("="*60)

    try:
        # Build context from retrieved chunks
        context = "\n\n---\n\n".join([
            f"[Document: {chunk['filename']}]\n{chunk['text']}"
            for chunk in retrieved_chunks
        ])

        logger.info(f"Building context from {len(retrieved_chunks)} chunks")
        logger.debug(f"Context length: {len(context)} characters")

        # Create prompt
        prompt = f"""You are a DevOps assistant helping with Jenkins errors.

Use the following documentation to answer the user's question:

{context}

User Question: {user_question}

Provide a clear, concise answer based on the documentation above. If the answer is not in the documentation, say so.

Answer:"""

        logger.debug(f"Prompt length: {len(prompt)} characters")

        # Call OpenAI
        logger.info("Calling OpenAI GPT-4o-mini for answer generation")
        client = OpenAI(api_key=OPENAI_API_KEY)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful DevOps assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        answer = response.choices[0].message.content

        logger.info(f"Generated answer: {len(answer)} characters")
        logger.debug(f"Tokens used - Prompt: {response.usage.prompt_tokens}, Completion: {response.usage.completion_tokens}")

        return answer

    except Exception as e:
        logger.error(f"Error generating answer: {str(e)}", exc_info=True)
        raise


# ============================================
# MAIN QUERY EXECUTION
# ============================================

def query_rag(user_question, top_k=3):
    """
    Complete RAG query pipeline
    """
    start_time = datetime.now()

    logger.info("="*60)
    logger.info("RAG QUERY PIPELINE - RETRIEVAL PHASE")
    logger.info("="*60)

    try:
        # Step 5: Convert question to embedding
        query_embedding = step5_query_embedding(user_question)

        # Step 6: Search for similar chunks
        retrieved_chunks = step6_vector_search(query_embedding, top_k=top_k)

        # Step 7: Generate answer
        answer = step7_generate_answer(user_question, retrieved_chunks)

        # Calculate duration
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Final output
        logger.info("="*60)
        logger.info("FINAL ANSWER")
        logger.info("="*60)
        logger.info(f"\n{answer}\n")

        logger.info("="*60)
        logger.info("SOURCES")
        logger.info("="*60)
        for chunk in retrieved_chunks:
            logger.info(f"  - {chunk['filename']} (chunk {chunk['chunk_id']}, distance: {chunk['distance']:.4f})")

        logger.info("="*60)
        logger.info("QUERY SUMMARY")
        logger.info("="*60)
        logger.info(f"  - Question: {user_question}")
        logger.info(f"  - Chunks retrieved: {len(retrieved_chunks)}")
        logger.info(f"  - Answer length: {len(answer)} characters")
        logger.info(f"  - Duration: {duration:.2f} seconds")
        logger.info(f"  - All logs: {log_all}")
        logger.info(f"  - Info logs: {log_info}")
        logger.info(f"  - Error logs: {log_error}")
        logger.info("="*60)

        return answer

    except Exception as e:
        logger.error("="*60)
        logger.error("QUERY FAILED!")
        logger.error("="*60)
        logger.error(f"Error: {str(e)}", exc_info=True)
        logger.error(f"Check error log for details: {log_error}")
        logger.error(f"Check all logs for full trace: {log_all}")
        raise


# ============================================
# EXAMPLE QUERIES
# ============================================

if __name__ == "__main__":
    try:
        # Example questions
        questions = [
            "What causes OutOfMemoryError in Docker containers?",
            "How do I fix Jenkins build failures?",
            "What are the symptoms of memory issues?"
        ]

        print("\nChoose a question to ask:")
        for i, q in enumerate(questions, 1):
            print(f"{i}. {q}")
        print(f"{len(questions) + 1}. Custom question")

        choice = input("\nEnter choice (1-4): ").strip()

        if choice.isdigit():
            choice = int(choice)
            if 1 <= choice <= len(questions):
                question = questions[choice - 1]
            else:
                question = input("\nEnter your question: ")
        else:
            question = input("\nEnter your question: ")

        logger.info(f"User selected question: {question}")

        # Run query
        query_rag(question, top_k=3)

    except Exception as e:
        logger.critical(f"Fatal error in query pipeline: {str(e)}")
        exit(1)
