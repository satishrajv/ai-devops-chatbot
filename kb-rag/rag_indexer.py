"""
Production RAG System - Jenkins Knowledge Base Indexer

Indexes markdown documents from S3 into Weaviate vector database.
Features:
- LangChain semantic chunking (intelligent splits based on meaning)
- OpenAI embeddings (text-embedding-3-small, 1536 dimensions)
- Multi-level logging (all/info/error log files)
- Comprehensive error handling with stack traces
- Production-ready monitoring and alerting
"""

import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
import weaviate
from weaviate.classes.init import Auth
from weaviate.classes.config import Configure, Property, DataType
import boto3

# LangChain imports for semantic chunking
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai.embeddings import OpenAIEmbeddings

# ============================================
# LOGGING CONFIGURATION - Production Grade
# ============================================

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Generate timestamp for log files
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

# Define log file paths
log_all = f"logs/rag_indexing_{timestamp}_all.log"
log_error = f"logs/rag_indexing_{timestamp}_error.log"
log_info = f"logs/rag_indexing_{timestamp}_info.log"

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
logger.info("RAG Indexing System Started")
logger.info(f"All logs: {log_all}")
logger.info(f"Info logs: {log_info}")
logger.info(f"Error logs: {log_error}")
logger.info("="*60)

# ============================================
# CONFIGURATION - Load from .env file
# ============================================

load_dotenv()

# AWS S3
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_BUCKET = os.getenv("S3_KB_BUCKET")

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

# Weaviate
WEAVIATE_URL = os.getenv("WEAVIATE_URL")
WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY")
COLLECTION_NAME = os.getenv("WEAVIATE_COLLECTION_NAME", "JenkinsKB")


# ============================================
# STEP 1: INDEXING (OFFLINE) - AUGMENTATION
# ============================================

def step1_document_loading():
    """
    Load documents from S3
    Returns: List of document contents
    """
    logger.info("[STEP 1] Document Loading from S3")
    logger.info("="*60)

    try:
        # Connect to S3
        s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY,
            region_name=AWS_REGION
        )
        logger.info(f"Connected to S3 - Region: {AWS_REGION}, Bucket: {S3_BUCKET}")

        # List all .md files
        response = s3_client.list_objects_v2(Bucket=S3_BUCKET)

        documents = []

        if 'Contents' in response:
            for obj in response['Contents']:
                if obj['Key'].endswith('.md'):
                    logger.info(f"Loading document: {obj['Key']} (Size: {obj['Size']} bytes)")

                    # Download file
                    file_obj = s3_client.get_object(Bucket=S3_BUCKET, Key=obj['Key'])
                    content = file_obj['Body'].read().decode('utf-8')

                    documents.append({
                        'filename': obj['Key'],
                        'content': content
                    })
                    logger.debug(f"Document content length: {len(content)} characters")

        logger.info(f"Total documents loaded: {len(documents)}")
        return documents

    except Exception as e:
        logger.error(f"Error loading documents from S3: {str(e)}", exc_info=True)
        raise


def step2_chunking(documents, method="semantic"):
    """
    Split documents into smaller chunks using LangChain

    Methods:
    - semantic: SemanticChunker (splits based on meaning)
    - recursive: RecursiveCharacterTextSplitter (splits by characters smartly)

    Returns: List of chunks
    """
    logger.info("[STEP 2] Chunking Documents (LangChain)")
    logger.info("="*60)
    logger.info(f"Chunking method: {method}")

    chunks = []

    try:
        if method == "semantic":
            # Semantic chunking - splits based on meaning/embeddings
            logger.info("Initializing SemanticChunker (semantic similarity-based)")

            embeddings = OpenAIEmbeddings(
                model=EMBEDDING_MODEL,
                openai_api_key=OPENAI_API_KEY
            )

            text_splitter = SemanticChunker(
                embeddings=embeddings,
                breakpoint_threshold_type="percentile"
            )
            logger.debug("SemanticChunker configured with percentile breakpoint")

        else:
            # Recursive chunking - smart character-based splitting
            logger.info("Initializing RecursiveCharacterTextSplitter (character-based)")

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                separators=["\n\n", "\n", ". ", " ", ""],
                length_function=len,
            )
            logger.debug("RecursiveCharacterTextSplitter configured: chunk_size=1000, overlap=200")

        for doc in documents:
            content = doc['content']
            filename = doc['filename']

            logger.info(f"Chunking document: {filename} ({len(content)} chars)")

            # Split using LangChain
            doc_chunks = text_splitter.split_text(content)

            for i, chunk_text in enumerate(doc_chunks):
                chunks.append({
                    'filename': filename,
                    'chunk_id': len(chunks),
                    'text': chunk_text
                })

            logger.info(f"Created {len(doc_chunks)} chunks from {filename}")
            logger.debug(f"Chunk sizes: {[len(c) for c in doc_chunks]}")

        logger.info(f"Total chunks created: {len(chunks)}")
        return chunks

    except Exception as e:
        logger.error(f"Error during chunking: {str(e)}", exc_info=True)
        raise


def step3_embedding_generation(chunks):
    """
    Generate embeddings for each chunk using OpenAI
    Returns: Chunks with embeddings
    """
    logger.info("[STEP 3] Embedding Generation")
    logger.info("="*60)
    logger.info(f"Generating embeddings for {len(chunks)} chunks using {EMBEDDING_MODEL}")

    try:
        client = OpenAI(api_key=OPENAI_API_KEY)

        for i, chunk in enumerate(chunks):
            if (i + 1) % 10 == 0 or i == 0:
                logger.info(f"Embedding progress: {i+1}/{len(chunks)} chunks")

            # Generate embedding
            response = client.embeddings.create(
                model=EMBEDDING_MODEL,
                input=chunk['text'][:8000]  # Truncate if too long
            )

            chunk['embedding'] = response.data[0].embedding
            logger.debug(f"Chunk {i+1}: embedding dimension = {len(chunk['embedding'])}")

        logger.info(f"Total embeddings generated: {len(chunks)}")
        return chunks

    except Exception as e:
        logger.error(f"Error generating embeddings: {str(e)}", exc_info=True)
        raise


def step4_vector_database_storage(chunks):
    """
    Store chunks with embeddings in Weaviate
    """
    logger.info("[STEP 4] Vector Database Storage")
    logger.info("="*60)

    try:
        # Connect to Weaviate
        logger.info(f"Connecting to Weaviate cluster: {WEAVIATE_URL}")
        client = weaviate.connect_to_weaviate_cloud(
            cluster_url=WEAVIATE_URL,
            auth_credentials=Auth.api_key(WEAVIATE_API_KEY),
            skip_init_checks=True
        )
        logger.info("Successfully connected to Weaviate")

        # Check if collection exists, delete if it does (fresh start)
        try:
            existing = client.collections.list_all()
            if COLLECTION_NAME in existing:
                logger.warning(f"Collection '{COLLECTION_NAME}' already exists - deleting for fresh start")
                client.collections.delete(COLLECTION_NAME)
                logger.info(f"Deleted existing collection: {COLLECTION_NAME}")
        except Exception as e:
            logger.debug(f"No existing collection to delete: {str(e)}")

        # Create collection
        logger.info(f"Creating new collection: {COLLECTION_NAME}")
        client.collections.create(
            name=COLLECTION_NAME,
            vectorizer_config=Configure.Vectorizer.none(),  # We provide embeddings
            properties=[
                Property(name="filename", data_type=DataType.TEXT),
                Property(name="chunk_id", data_type=DataType.INT),
                Property(name="text", data_type=DataType.TEXT)
            ]
        )
        logger.info("Collection schema created successfully")
        logger.debug(f"Properties: filename (TEXT), chunk_id (INT), text (TEXT)")

        # Get collection
        collection = client.collections.get(COLLECTION_NAME)

        # Insert chunks
        logger.info(f"Inserting {len(chunks)} chunks into Weaviate")
        successful_inserts = 0

        for i, chunk in enumerate(chunks):
            if (i + 1) % 10 == 0 or i == 0:
                logger.info(f"Insert progress: {i+1}/{len(chunks)} chunks")

            try:
                collection.data.insert(
                    properties={
                        "filename": chunk['filename'],
                        "chunk_id": chunk['chunk_id'],
                        "text": chunk['text']
                    },
                    vector=chunk['embedding']
                )
                successful_inserts += 1
                logger.debug(f"Inserted chunk {i+1}: {chunk['filename']} (chunk_id: {chunk['chunk_id']})")

            except Exception as e:
                logger.error(f"Failed to insert chunk {i+1}: {str(e)}")

        logger.info(f"Successfully stored {successful_inserts}/{len(chunks)} chunks in Weaviate")

        client.close()
        logger.info("Weaviate connection closed")
        return True

    except Exception as e:
        logger.error(f"Error during vector database storage: {str(e)}", exc_info=True)
        raise


# ============================================
# MAIN EXECUTION
# ============================================

def run_indexing():
    """
    Run the complete indexing pipeline
    """
    start_time = datetime.now()
    logger.info("="*60)
    logger.info("RAG INDEXING PIPELINE - AUGMENTATION PHASE")
    logger.info("="*60)

    try:
        # Step 1: Load documents from S3
        documents = step1_document_loading()

        if not documents:
            logger.warning("No documents found in S3 bucket!")
            logger.info("="*60)
            logger.info("INDEXING ABORTED - No documents to process")
            logger.info("="*60)
            return

        # Step 2: Chunk documents (choose method: "semantic" or "recursive")
        chunks = step2_chunking(documents, method="semantic")

        # Step 3: Generate embeddings
        chunks_with_embeddings = step3_embedding_generation(chunks)

        # Step 4: Store in Weaviate
        step4_vector_database_storage(chunks_with_embeddings)

        # Calculate duration
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Final summary
        logger.info("="*60)
        logger.info("INDEXING COMPLETE!")
        logger.info("="*60)
        logger.info("Summary:")
        logger.info(f"  - Documents loaded: {len(documents)}")
        logger.info(f"  - Chunks created: {len(chunks)}")
        logger.info(f"  - Embeddings generated: {len(chunks)}")
        logger.info(f"  - Stored in Weaviate collection: {COLLECTION_NAME}")
        logger.info(f"  - Total duration: {duration:.2f} seconds")
        logger.info(f"  - All logs: {log_all}")
        logger.info(f"  - Info logs: {log_info}")
        logger.info(f"  - Error logs: {log_error}")
        logger.info("="*60)

    except Exception as e:
        logger.error("="*60)
        logger.error("INDEXING FAILED!")
        logger.error("="*60)
        logger.error(f"Error: {str(e)}", exc_info=True)
        logger.error(f"Check error log for details: {log_error}")
        logger.error(f"Check all logs for full trace: {log_all}")
        raise


if __name__ == "__main__":
    try:
        run_indexing()
    except Exception as e:
        logger.critical(f"Fatal error in indexing pipeline: {str(e)}")
        exit(1)
