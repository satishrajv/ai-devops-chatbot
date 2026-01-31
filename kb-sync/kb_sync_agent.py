"""
LangGraph Multi-Agent KB Sync System
Main orchestrator that coordinates all agents to sync S3 markdown files to Weaviate
"""

from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict, Any
import logging
from datetime import datetime

from agents.s3_fetcher import S3FetcherAgent
from agents.document_parser import DocumentParserAgent
from agents.embedder import EmbedderAgent
from agents.weaviate_uploader import WeaviateUploaderAgent
from agents.reporter import ReporterAgent
from utils.state_tracker import StateTracker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('kb_sync.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """State shared between all agents"""
    s3_files: List[Dict[str, Any]]  # Files from S3
    parsed_documents: List[Dict[str, Any]]  # Parsed markdown documents
    embedded_documents: List[Dict[str, Any]]  # Documents with embeddings
    upload_results: List[Dict[str, Any]]  # Upload status
    errors: List[str]  # Any errors encountered
    stats: Dict[str, int]  # Statistics
    run_id: str  # Unique run identifier


def s3_fetch_node(state: AgentState) -> AgentState:
    """Agent 1: Fetch markdown files from S3"""
    logger.info("[AGENT 1] S3 Fetcher - Starting...")

    try:
        agent = S3FetcherAgent()
        s3_files = agent.fetch_new_files()

        state["s3_files"] = s3_files
        state["stats"]["s3_files_found"] = len(s3_files)

        logger.info(f"[AGENT 1] Found {len(s3_files)} files to process")

    except Exception as e:
        error_msg = f"S3 Fetch Error: {str(e)}"
        logger.error(f"[AGENT 1] {error_msg}")
        state["errors"].append(error_msg)

    return state


def document_parse_node(state: AgentState) -> AgentState:
    """Agent 2: Parse markdown documents"""
    logger.info("[AGENT 2] Document Parser - Starting...")

    if not state.get("s3_files"):
        logger.info("[AGENT 2] No files to parse, skipping")
        return state

    try:
        agent = DocumentParserAgent()
        parsed_docs = []

        for s3_file in state["s3_files"]:
            try:
                parsed_doc = agent.parse_markdown(s3_file)
                parsed_docs.append(parsed_doc)
                logger.info(f"[AGENT 2] Parsed: {s3_file['file_name']}")
            except Exception as e:
                error_msg = f"Parse error for {s3_file['file_name']}: {str(e)}"
                logger.error(f"[AGENT 2] {error_msg}")
                state["errors"].append(error_msg)

        state["parsed_documents"] = parsed_docs
        state["stats"]["documents_parsed"] = len(parsed_docs)

        logger.info(f"[AGENT 2] Successfully parsed {len(parsed_docs)} documents")

    except Exception as e:
        error_msg = f"Document Parse Error: {str(e)}"
        logger.error(f"[AGENT 2] {error_msg}")
        state["errors"].append(error_msg)

    return state


def embedder_node(state: AgentState) -> AgentState:
    """Agent 3: Generate embeddings using OpenAI"""
    logger.info("[AGENT 3] Embedder - Starting...")

    if not state.get("parsed_documents"):
        logger.info("[AGENT 3] No documents to embed, skipping")
        return state

    try:
        agent = EmbedderAgent()
        embedded_docs = []

        for parsed_doc in state["parsed_documents"]:
            try:
                embedded_doc = agent.generate_embeddings(parsed_doc)
                embedded_docs.append(embedded_doc)
                logger.info(f"[AGENT 3] Embedded: {parsed_doc['file_name']}")
            except Exception as e:
                error_msg = f"Embedding error for {parsed_doc['file_name']}: {str(e)}"
                logger.error(f"[AGENT 3] {error_msg}")
                state["errors"].append(error_msg)

        state["embedded_documents"] = embedded_docs
        state["stats"]["documents_embedded"] = len(embedded_docs)

        logger.info(f"[AGENT 3] Successfully embedded {len(embedded_docs)} documents")

    except Exception as e:
        error_msg = f"Embedder Error: {str(e)}"
        logger.error(f"[AGENT 3] {error_msg}")
        state["errors"].append(error_msg)

    return state


def weaviate_upload_node(state: AgentState) -> AgentState:
    """Agent 4: Upload documents to Weaviate"""
    logger.info("[AGENT 4] Weaviate Uploader - Starting...")

    if not state.get("embedded_documents"):
        logger.info("[AGENT 4] No documents to upload, skipping")
        return state

    try:
        agent = WeaviateUploaderAgent()
        upload_results = []

        for embedded_doc in state["embedded_documents"]:
            try:
                result = agent.upload_document(embedded_doc)
                upload_results.append(result)
                logger.info(f"[AGENT 4] Uploaded: {embedded_doc['file_name']} - {result['status']}")
            except Exception as e:
                error_msg = f"Upload error for {embedded_doc['file_name']}: {str(e)}"
                logger.error(f"[AGENT 4] {error_msg}")
                state["errors"].append(error_msg)

        state["upload_results"] = upload_results
        state["stats"]["documents_uploaded"] = len([r for r in upload_results if r["status"] == "success"])

        logger.info(f"[AGENT 4] Successfully uploaded {state['stats']['documents_uploaded']} documents")

    except Exception as e:
        error_msg = f"Weaviate Upload Error: {str(e)}"
        logger.error(f"[AGENT 4] {error_msg}")
        state["errors"].append(error_msg)

    return state


def reporter_node(state: AgentState) -> AgentState:
    """Agent 5: Generate final report"""
    logger.info("[AGENT 5] Reporter - Starting...")

    try:
        agent = ReporterAgent()
        report = agent.generate_report(state)

        logger.info("\n" + "="*60)
        logger.info("KB SYNC REPORT")
        logger.info("="*60)
        logger.info(report)
        logger.info("="*60 + "\n")

    except Exception as e:
        error_msg = f"Reporter Error: {str(e)}"
        logger.error(f"[AGENT 5] {error_msg}")
        state["errors"].append(error_msg)

    return state


def build_graph() -> StateGraph:
    """Build the LangGraph workflow"""

    workflow = StateGraph(AgentState)

    # Add nodes for each agent
    workflow.add_node("s3_fetcher", s3_fetch_node)
    workflow.add_node("document_parser", document_parse_node)
    workflow.add_node("embedder", embedder_node)
    workflow.add_node("weaviate_uploader", weaviate_upload_node)
    workflow.add_node("reporter", reporter_node)

    # Define the flow
    workflow.set_entry_point("s3_fetcher")
    workflow.add_edge("s3_fetcher", "document_parser")
    workflow.add_edge("document_parser", "embedder")
    workflow.add_edge("embedder", "weaviate_uploader")
    workflow.add_edge("weaviate_uploader", "reporter")
    workflow.add_edge("reporter", END)

    return workflow.compile()


def run_sync():
    """Main entry point for KB sync"""
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    logger.info("="*60)
    logger.info(f"KB SYNC STARTED - Run ID: {run_id}")
    logger.info("="*60)

    # Initialize state
    initial_state: AgentState = {
        "s3_files": [],
        "parsed_documents": [],
        "embedded_documents": [],
        "upload_results": [],
        "errors": [],
        "stats": {
            "s3_files_found": 0,
            "documents_parsed": 0,
            "documents_embedded": 0,
            "documents_uploaded": 0
        },
        "run_id": run_id
    }

    try:
        # Build and run the graph
        app = build_graph()
        final_state = app.invoke(initial_state)

        logger.info("="*60)
        logger.info("KB SYNC COMPLETED SUCCESSFULLY")
        logger.info("="*60)

        return final_state

    except Exception as e:
        logger.error(f"KB Sync failed: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    run_sync()
