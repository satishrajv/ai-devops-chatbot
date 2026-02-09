"""
LangGraph Multi-Agent RAG Chatbot
Orchestrates query processing, retrieval, and answer generation
"""

import os
import logging
from typing import TypedDict, List, Dict, Literal
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END

from agents.query_processor import QueryProcessorAgent
from agents.rag_retriever import RAGRetrieverAgent
from agents.answer_generator import AnswerGeneratorAgent
import config

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================
# STATE DEFINITION
# ============================================

class ChatbotState(TypedDict):
    """State passed between agents"""
    # Input
    user_question: str

    # Agent 1 outputs
    processed_query: str
    query_embedding: List[float]

    # Agent 2 outputs
    retrieved_chunks: List[Dict]
    total_relevant: int

    # Agent 3 outputs
    final_answer: str
    sources: List[Dict]
    chunks_used: int
    tokens_used: Dict

    # Metadata
    is_fallback: bool
    confidence_score: float


# ============================================
# AGENT NODES
# ============================================

def query_processor_node(state: ChatbotState) -> ChatbotState:
    """Agent 1: Process and embed user query"""
    logger.info("="*60)
    logger.info("[NODE] Query Processor")
    logger.info("="*60)

    try:
        # Initialize agent
        agent = QueryProcessorAgent(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            embedding_model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
        )

        # Process query
        result = agent.process_query(state['user_question'])

        # Update state
        state['processed_query'] = result['processed_query']
        state['query_embedding'] = result['query_embedding']

        logger.info(f"Processed query: {result['processed_query']}")

    except Exception as e:
        logger.error(f"Query processor failed: {str(e)}")
        raise

    return state


def rag_retriever_node(state: ChatbotState) -> ChatbotState:
    """Agent 2: Retrieve relevant chunks from Weaviate"""
    logger.info("="*60)
    logger.info("[NODE] RAG Retriever")
    logger.info("="*60)

    try:
        # Initialize agent
        agent = RAGRetrieverAgent(
            weaviate_url=os.getenv("WEAVIATE_URL"),
            weaviate_api_key=os.getenv("WEAVIATE_API_KEY"),
            collection_name=os.getenv("WEAVIATE_COLLECTION_NAME", "JenkinsKnowledgeBase")
        )

        # Retrieve chunks (using config values)
        result = agent.retrieve(
            query_embedding=state['query_embedding'],
            top_k=config.TOP_K_CHUNKS,
            distance_threshold=config.DISTANCE_THRESHOLD
        )

        # Update state
        state['retrieved_chunks'] = result['retrieved_chunks']
        state['total_relevant'] = result['total_relevant']

        logger.info(f"Retrieved {result['total_relevant']} relevant chunks")

    except Exception as e:
        logger.error(f"RAG retriever failed: {str(e)}")
        raise

    return state


def answer_generator_node(state: ChatbotState) -> ChatbotState:
    """Agent 3: Generate answer with LLM"""
    logger.info("="*60)
    logger.info("[NODE] Answer Generator")
    logger.info("="*60)

    try:
        # Initialize agent (using config values)
        agent = AnswerGeneratorAgent(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            model=config.LLM_MODEL
        )

        # Generate answer (using config values)
        result = agent.generate_answer(
            user_question=state['user_question'],
            retrieved_chunks=state['retrieved_chunks'],
            temperature=config.TEMPERATURE
        )

        # Update state
        state['final_answer'] = result['final_answer']
        state['sources'] = result['sources']
        state['chunks_used'] = result['chunks_used']
        state['tokens_used'] = result.get('tokens_used', {})
        state['is_fallback'] = False
        state['confidence_score'] = 0.8  # High confidence with chunks

        logger.info(f"Generated answer: {len(result['final_answer'])} characters")

    except Exception as e:
        logger.error(f"Answer generator failed: {str(e)}")
        raise

    return state


def fallback_node(state: ChatbotState) -> ChatbotState:
    """Fallback: Generate response when no chunks found"""
    logger.info("="*60)
    logger.info("[NODE] Fallback Response")
    logger.info("="*60)

    try:
        # Initialize agent
        agent = AnswerGeneratorAgent(
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )

        # Generate fallback
        result = agent.generate_fallback(state['user_question'])

        # Update state
        state['final_answer'] = result['final_answer']
        state['sources'] = []
        state['chunks_used'] = 0
        state['is_fallback'] = True
        state['confidence_score'] = 0.2  # Low confidence - no context

        logger.warning("No relevant chunks found - using fallback response")

    except Exception as e:
        logger.error(f"Fallback failed: {str(e)}")
        raise

    return state


# ============================================
# DECISION FUNCTIONS
# ============================================

def should_generate_answer(state: ChatbotState) -> Literal["generate", "fallback"]:
    """
    Decide whether to generate answer or use fallback

    Returns:
        "generate" if chunks found, "fallback" otherwise
    """
    has_chunks = state.get('total_relevant', 0) > 0

    if has_chunks:
        logger.info(f"Decision: GENERATE (found {state['total_relevant']} chunks)")
        return "generate"
    else:
        logger.info("Decision: FALLBACK (no relevant chunks)")
        return "fallback"


# ============================================
# BUILD LANGGRAPH WORKFLOW
# ============================================

def build_chatbot_graph() -> StateGraph:
    """Build and compile the LangGraph workflow"""

    # Create graph
    workflow = StateGraph(ChatbotState)

    # Add nodes (agents)
    workflow.add_node("query_processor", query_processor_node)
    workflow.add_node("rag_retriever", rag_retriever_node)
    workflow.add_node("answer_generator", answer_generator_node)
    workflow.add_node("fallback", fallback_node)

    # Define flow
    workflow.set_entry_point("query_processor")
    workflow.add_edge("query_processor", "rag_retriever")

    # Conditional routing after retrieval
    workflow.add_conditional_edges(
        "rag_retriever",
        should_generate_answer,
        {
            "generate": "answer_generator",
            "fallback": "fallback"
        }
    )

    # Both paths end here
    workflow.add_edge("answer_generator", END)
    workflow.add_edge("fallback", END)

    # Compile
    return workflow.compile()


# ============================================
# CHATBOT INTERFACE
# ============================================

class RAGChatbot:
    """Main chatbot interface using LangGraph"""

    def __init__(self):
        self.graph = build_chatbot_graph()
        logger.info("RAG Chatbot initialized with LangGraph workflow")

    def ask(self, question: str) -> Dict:
        """
        Ask a question to the chatbot

        Args:
            question: User's question

        Returns:
            Dict with answer, sources, and metadata
        """
        logger.info("="*60)
        logger.info(f"USER QUESTION: {question}")
        logger.info("="*60)

        # Initialize state
        initial_state: ChatbotState = {
            'user_question': question,
            'processed_query': '',
            'query_embedding': [],
            'retrieved_chunks': [],
            'total_relevant': 0,
            'final_answer': '',
            'sources': [],
            'chunks_used': 0,
            'tokens_used': {},
            'is_fallback': False,
            'confidence_score': 0.0
        }

        # Run through LangGraph workflow
        final_state = self.graph.invoke(initial_state)

        # Extract response
        response = {
            'answer': final_state['final_answer'],
            'sources': final_state['sources'],
            'chunks_used': final_state['chunks_used'],
            'is_fallback': final_state['is_fallback'],
            'confidence': final_state['confidence_score'],
            'tokens_used': final_state.get('tokens_used', {})
        }

        logger.info("="*60)
        logger.info("CHATBOT RESPONSE READY")
        logger.info("="*60)

        return response


# ============================================
# CLI TESTING
# ============================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  RAG CHATBOT - LangGraph Multi-Agent System")
    print("="*60 + "\n")

    # Initialize chatbot
    chatbot = RAGChatbot()

    # Test questions
    test_questions = [
        "What causes OutOfMemoryError in Docker containers?",
        "How do I fix Jenkins build failures?",
        "What is quantum computing?"  # Should trigger fallback
    ]

    for i, question in enumerate(test_questions, 1):
        print(f"\n{'='*60}")
        print(f"TEST {i}: {question}")
        print('='*60)

        response = chatbot.ask(question)

        print(f"\nANSWER:\n{response['answer']}")
        print(f"\nSOURCES:")
        for source in response['sources']:
            print(f"  - {source['filename']} (relevance: {source['relevance']:.2f})")

        print(f"\nMETADATA:")
        print(f"  - Chunks used: {response['chunks_used']}")
        print(f"  - Fallback: {response['is_fallback']}")
        print(f"  - Confidence: {response['confidence']:.2f}")

        input("\nPress Enter for next question...")
