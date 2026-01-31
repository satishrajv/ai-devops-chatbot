"""
Streamlit UI for RAG Chatbot
Interactive chat interface with LangGraph backend
"""

import streamlit as st
import time
from datetime import datetime
from langgraph_chatbot import RAGChatbot

# Page configuration
st.set_page_config(
    page_title="DevOps Knowledge Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .user-message {
        background-color: #e3f2fd;
    }
    .assistant-message {
        background-color: #f5f5f5;
    }
    .source-card {
        background-color: #fff3e0;
        padding: 0.5rem;
        border-radius: 0.3rem;
        margin: 0.3rem 0;
        border-left: 3px solid #ff9800;
    }
    .metadata-badge {
        background-color: #e8f5e9;
        padding: 0.2rem 0.5rem;
        border-radius: 0.3rem;
        font-size: 0.8rem;
        margin: 0.2rem;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)


# ============================================
# INITIALIZE SESSION STATE
# ============================================

if 'chatbot' not in st.session_state:
    with st.spinner('🔄 Initializing RAG Chatbot...'):
        st.session_state.chatbot = RAGChatbot()

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'total_queries' not in st.session_state:
    st.session_state.total_queries = 0

if 'total_tokens' not in st.session_state:
    st.session_state.total_tokens = 0


# ============================================
# SIDEBAR
# ============================================

with st.sidebar:
    st.title("⚙️ Settings")

    # Settings
    st.subheader("Query Settings")
    top_k = st.slider("Top-K chunks", min_value=1, max_value=5, value=3, help="Number of chunks to retrieve")
    temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.3, step=0.1, help="LLM creativity (0=precise, 1=creative)")

    st.divider()

    # Statistics
    st.subheader("📊 Statistics")
    st.metric("Total Queries", st.session_state.total_queries)
    st.metric("Total Tokens Used", st.session_state.total_tokens)

    if st.session_state.messages:
        avg_tokens = st.session_state.total_tokens / st.session_state.total_queries if st.session_state.total_queries > 0 else 0
        st.metric("Avg Tokens/Query", f"{avg_tokens:.0f}")

    st.divider()

    # Actions
    st.subheader("🎯 Actions")

    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.total_queries = 0
        st.session_state.total_tokens = 0
        st.rerun()

    # Example questions
    st.divider()
    st.subheader("💡 Example Questions")

    example_questions = [
        "What causes OutOfMemoryError?",
        "How do I fix Jenkins build failures?",
        "What are symptoms of memory issues?",
        "How to prevent OOM errors?",
    ]

    for question in example_questions:
        if st.button(question, key=f"example_{question}", use_container_width=True):
            st.session_state.example_question = question
            st.rerun()


# ============================================
# MAIN CHAT INTERFACE
# ============================================

# Header
st.title("🤖 Jenkins DevOps Knowledge Assistant")
st.markdown("Ask questions about Jenkins errors, Docker issues, and CI/CD troubleshooting.")
st.divider()

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        # Show sources if available
        if "sources" in message and message["sources"]:
            with st.expander("📚 Sources", expanded=False):
                for source in message["sources"]:
                    st.markdown(f"""
                    <div class="source-card">
                        📄 <strong>{source['filename']}</strong><br>
                        Relevance: {source['relevance']:.0%}
                    </div>
                    """, unsafe_allow_html=True)

        # Show metadata if available
        if "metadata" in message and message["metadata"]:
            meta = message["metadata"]
            badges_html = f"""
            <div>
                <span class="metadata-badge">🎯 Chunks: {meta.get('chunks_used', 0)}</span>
                <span class="metadata-badge">🔢 Tokens: {meta.get('tokens_used', {}).get('total', 0)}</span>
                <span class="metadata-badge">📊 Confidence: {meta.get('confidence', 0):.0%}</span>
            </div>
            """
            st.markdown(badges_html, unsafe_allow_html=True)


# ============================================
# CHAT INPUT
# ============================================

# Check if example question was clicked
if 'example_question' in st.session_state:
    user_input = st.session_state.example_question
    del st.session_state.example_question
else:
    user_input = st.chat_input("Type your question here...")

if user_input:
    # Add user message to history
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)

    # Generate response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        sources_placeholder = st.empty()
        metadata_placeholder = st.empty()

        # Show thinking animation
        with st.spinner('🔍 Searching knowledge base...'):
            start_time = time.time()

            try:
                # Call LangGraph chatbot
                response = st.session_state.chatbot.ask(user_input)

                end_time = time.time()
                response_time = end_time - start_time

                # Display answer with typing effect
                answer = response['answer']
                displayed_text = ""

                for char in answer:
                    displayed_text += char
                    message_placeholder.markdown(displayed_text + "▌")
                    time.sleep(0.01)  # Typing effect

                message_placeholder.markdown(answer)

                # Display sources
                if response['sources']:
                    with sources_placeholder.expander("📚 Sources", expanded=True):
                        for source in response['sources']:
                            st.markdown(f"""
                            <div class="source-card">
                                📄 <strong>{source['filename']}</strong><br>
                                Relevance: {source['relevance']:.0%}
                            </div>
                            """, unsafe_allow_html=True)

                # Display metadata
                tokens_used = response.get('tokens_used', {}).get('total', 0)

                badges_html = f"""
                <div>
                    <span class="metadata-badge">🎯 Chunks: {response['chunks_used']}</span>
                    <span class="metadata-badge">🔢 Tokens: {tokens_used}</span>
                    <span class="metadata-badge">📊 Confidence: {response['confidence']:.0%}</span>
                    <span class="metadata-badge">⏱️ Time: {response_time:.2f}s</span>
                    {'<span class="metadata-badge">⚠️ Fallback</span>' if response['is_fallback'] else ''}
                </div>
                """
                metadata_placeholder.markdown(badges_html, unsafe_allow_html=True)

                # Update session state
                st.session_state.total_queries += 1
                st.session_state.total_tokens += tokens_used

                # Add assistant message to history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": response['sources'],
                    "metadata": {
                        'chunks_used': response['chunks_used'],
                        'tokens_used': response.get('tokens_used', {}),
                        'confidence': response['confidence'],
                        'response_time': response_time,
                        'is_fallback': response['is_fallback']
                    }
                })

            except Exception as e:
                error_message = f"❌ Error: {str(e)}"
                message_placeholder.error(error_message)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_message
                })


# ============================================
# FOOTER
# ============================================

st.divider()
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.8rem;">
    Powered by LangGraph + OpenAI + Weaviate |
    <a href="https://github.com/anthropics/claude-code" target="_blank">Built with Claude Code</a>
</div>
""", unsafe_allow_html=True)
