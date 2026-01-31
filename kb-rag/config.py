"""
Configuration file for RAG Chatbot
All chatbot settings are centralized here
"""

# ============================================
# RAG Retrieval Settings
# ============================================

# Number of document chunks to retrieve from Weaviate
TOP_K_CHUNKS = 3

# Distance threshold for filtering relevant chunks
# Lower = more similar (0.0 = identical)
# Higher = less similar
# Chunks with distance > threshold are filtered out
DISTANCE_THRESHOLD = 0.7

# ============================================
# LLM Generation Settings
# ============================================

# Temperature for answer generation (0.0 - 1.0)
# 0.0 = deterministic, precise answers
# 1.0 = creative, varied answers
TEMPERATURE = 0.3

# OpenAI model to use for answer generation
LLM_MODEL = "gpt-4o-mini"

# ============================================
# Logging Settings
# ============================================

# Enable detailed logging for debugging
DEBUG_MODE = False
