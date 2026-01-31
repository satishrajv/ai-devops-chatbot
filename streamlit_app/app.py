"""
AI DevOps Platform - Streamlit Dashboard
Trigger and monitor Jenkins jobs via API
"""

import streamlit as st
import requests
from requests.auth import HTTPBasicAuth
import time
import os
import sys

# Add kb-rag directory to Python path for chatbot imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'kb-rag'))

# Page configuration
st.set_page_config(
    page_title="AI DevOps Platform",
    page_icon="🚀",
    layout="wide"
)

# Jenkins configuration - load from environment variables
jenkins_url = os.getenv("JENKINS_URL", "http://localhost:8080")
jenkins_user = os.getenv("JENKINS_USER")
jenkins_token = os.getenv("JENKINS_TOKEN")

# Validate required credentials
if not jenkins_user or not jenkins_token:
    st.error("⚠️ Jenkins credentials not configured. Please set JENKINS_URL, JENKINS_USER, and JENKINS_TOKEN environment variables.")
    st.stop()

# Main content
st.title("🚀 AI DevOps Platform")
st.markdown("### Trigger and Monitor Jenkins CI/CD Pipelines")

# Store credentials in session state
if jenkins_user and jenkins_token:
    st.session_state['auth'] = HTTPBasicAuth(jenkins_user, jenkins_token)
else:
    st.session_state['auth'] = None


def get_jenkins_crumb():
    """Get Jenkins CSRF crumb for API calls"""
    try:
        response = requests.get(
            f"{jenkins_url}/crumbIssuer/api/json",
            auth=st.session_state['auth'],
            timeout=10
        )
        if response.status_code == 200:
            crumb_data = response.json()
            return {crumb_data['crumbRequestField']: crumb_data['crumb']}
    except Exception:
        pass
    return {}


def trigger_job(job_name, parameters=None):
    """Trigger a Jenkins job"""
    if not st.session_state['auth']:
        return {"error": "Please configure Jenkins credentials in the sidebar"}

    try:
        crumb = get_jenkins_crumb()

        if parameters:
            url = f"{jenkins_url}/job/{job_name}/buildWithParameters"
            response = requests.post(
                url,
                auth=st.session_state['auth'],
                headers=crumb,
                data=parameters,
                timeout=30
            )
        else:
            url = f"{jenkins_url}/job/{job_name}/build"
            response = requests.post(
                url,
                auth=st.session_state['auth'],
                headers=crumb,
                timeout=30
            )

        if response.status_code in [200, 201, 202]:
            return {"success": True, "message": f"Job '{job_name}' triggered successfully!"}
        else:
            return {"error": f"Failed to trigger job. Status: {response.status_code}"}

    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to Jenkins. Check the URL and ensure Jenkins is running."}
    except Exception as e:
        return {"error": f"Error: {str(e)}"}


def get_job_status(job_name):
    """Get the status of the last build"""
    if not st.session_state['auth']:
        return None

    try:
        response = requests.get(
            f"{jenkins_url}/job/{job_name}/lastBuild/api/json",
            auth=st.session_state['auth'],
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return None


def get_all_jobs():
    """Get list of all Jenkins jobs"""
    if not st.session_state['auth']:
        return []

    try:
        response = requests.get(
            f"{jenkins_url}/api/json?tree=jobs[name,color,url]",
            auth=st.session_state['auth'],
            timeout=10
        )
        if response.status_code == 200:
            return response.json().get('jobs', [])
    except Exception:
        pass
    return []


def get_build_log(job_name, build_number):
    """Get console output/logs from a specific build"""
    if not st.session_state['auth']:
        return None

    try:
        response = requests.get(
            f"{jenkins_url}/job/{job_name}/{build_number}/consoleText",
            auth=st.session_state['auth'],
            timeout=10
        )
        if response.status_code == 200:
            return response.text
    except Exception:
        pass
    return None


def get_queue_info():
    """Get information about queued builds"""
    if not st.session_state['auth']:
        return []

    try:
        response = requests.get(
            f"{jenkins_url}/queue/api/json",
            auth=st.session_state['auth'],
            timeout=10
        )
        if response.status_code == 200:
            return response.json().get('items', [])
    except Exception:
        pass
    return []


# Initialize chatbot in session state
if 'chatbot' not in st.session_state:
    try:
        from langgraph_chatbot import RAGChatbot
        with st.spinner('🔄 Initializing Knowledge Assistant...'):
            st.session_state.chatbot = RAGChatbot()
        st.session_state.chatbot_error = None
    except Exception as e:
        st.session_state.chatbot = None
        st.session_state.chatbot_error = str(e)

if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []

if 'total_queries' not in st.session_state:
    st.session_state.total_queries = 0

if 'total_tokens' not in st.session_state:
    st.session_state.total_tokens = 0

# Tab layout
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎯 Trigger Jobs", "📊 Job Status", "📋 All Jobs", "📝 Build Logs", "🤖 Knowledge Assistant"])

with tab1:
    st.subheader("Trigger a Jenkins Job")

    col1, col2 = st.columns(2)

    with col1:
        job_name = st.text_input(
            "Job Name",
            value="ai-devops-pipeline",
            help="Name of the Jenkins job to trigger"
        )

        use_parameters = st.checkbox("Include Parameters")

        parameters = {}
        if use_parameters:
            st.markdown("**Job Parameters:**")
            param_branch = st.text_input("BRANCH", value="main")
            param_env = st.selectbox("ENVIRONMENT", ["development", "staging", "production"])
            parameters = {"BRANCH": param_branch, "ENVIRONMENT": param_env}

    with col2:
        st.markdown("**Actions:**")
        if st.button("🚀 Trigger Build", type="primary", use_container_width=True):
            with st.spinner("Triggering job..."):
                result = trigger_job(job_name, parameters if use_parameters else None)

                if "success" in result:
                    st.success(result["message"])
                else:
                    st.error(result.get("error", "Unknown error"))

with tab2:
    st.subheader("Check Job Status")

    status_job_name = st.text_input(
        "Job Name for Status",
        value="ai-devops-pipeline",
        key="status_job"
    )

    if st.button("🔄 Refresh Status"):
        with st.spinner("Fetching status..."):
            status = get_job_status(status_job_name)

            if status:
                col1, col2, col3 = st.columns(3)

                with col1:
                    result = status.get('result', 'IN PROGRESS')
                    if result == 'SUCCESS':
                        st.success(f"Result: {result}")
                    elif result == 'FAILURE':
                        st.error(f"Result: {result}")
                    else:
                        st.info(f"Result: {result or 'IN PROGRESS'}")

                with col2:
                    st.metric("Build Number", f"#{status.get('number', 'N/A')}")

                with col3:
                    duration = status.get('duration', 0)
                    st.metric("Duration", f"{duration // 1000}s")

                st.markdown(f"**Build URL:** [{status.get('url', 'N/A')}]({status.get('url', '#')})")
            else:
                st.warning("Could not fetch job status. Check credentials and job name.")

with tab3:
    st.subheader("All Jenkins Jobs")

    if st.button("🔄 Load Jobs"):
        with st.spinner("Loading jobs..."):
            jobs = get_all_jobs()

            if jobs:
                for job in jobs:
                    color = job.get('color', 'notbuilt')
                    icon = "🟢" if color == "blue" else "🔴" if color == "red" else "🟡" if "anime" in color else "⚪"

                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"{icon} **{job.get('name', 'Unknown')}**")
                    with col2:
                        if st.button("Trigger", key=f"trigger_{job.get('name')}"):
                            result = trigger_job(job.get('name'))
                            if "success" in result:
                                st.success("Triggered!")
                            else:
                                st.error("Failed")
            else:
                st.info("No jobs found or unable to connect to Jenkins.")

with tab4:
    st.subheader("Build Logs")

    col1, col2 = st.columns(2)
    with col1:
        log_job_name = st.text_input(
            "Job Name",
            value="ai-devops-pipeline",
            key="log_job"
        )
    with col2:
        log_build_number = st.text_input(
            "Build Number",
            value="lastBuild",
            help="Enter build number or use 'lastBuild', 'lastSuccessfulBuild', 'lastFailedBuild'"
        )

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📥 Fetch Logs", type="primary", use_container_width=True):
            with st.spinner("Fetching build logs..."):
                logs = get_build_log(log_job_name, log_build_number)

                if logs:
                    st.success(f"Logs retrieved for {log_job_name} #{log_build_number}")
                    st.code(logs, language="text", line_numbers=False)
                else:
                    st.error("Could not fetch logs. Check job name, build number, and credentials.")

    with col2:
        if st.button("🔄 Auto-refresh", use_container_width=True):
            st.session_state['auto_refresh'] = not st.session_state.get('auto_refresh', False)

    with col3:
        if st.button("📊 Queue Status", use_container_width=True):
            queue_items = get_queue_info()
            if queue_items:
                st.info(f"Builds in queue: {len(queue_items)}")
                for item in queue_items:
                    st.write(f"- {item.get('task', {}).get('name', 'Unknown')}")
            else:
                st.success("No builds in queue")

    if st.session_state.get('auto_refresh', False):
        st.info("Auto-refresh enabled. Logs will update every 5 seconds.")
        time.sleep(5)
        st.rerun()

with tab5:
    st.subheader("🤖 Jenkins Knowledge Assistant")
    st.markdown("Ask questions about Jenkins errors, Docker issues, and CI/CD troubleshooting.")

    # Check if chatbot initialized successfully
    if st.session_state.chatbot_error:
        st.error(f"❌ Chatbot initialization failed: {st.session_state.chatbot_error}")
        st.info("Make sure the RAG system is properly configured. Check `kb-rag/.env` file.")
    elif not st.session_state.chatbot:
        st.warning("⚠️ Chatbot not initialized. Please refresh the page.")
    else:
        # Sidebar statistics (in expander to save space)
        with st.expander("📊 Chatbot Statistics", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Queries", st.session_state.total_queries)
            with col2:
                st.metric("Total Tokens Used", st.session_state.total_tokens)

            if st.session_state.chat_messages:
                avg_tokens = st.session_state.total_tokens / st.session_state.total_queries if st.session_state.total_queries > 0 else 0
                st.metric("Avg Tokens/Query", f"{avg_tokens:.0f}")

        # Example questions
        st.markdown("**💡 Try asking:**")
        example_cols = st.columns(2)
        with example_cols[0]:
            if st.button("What causes OutOfMemoryError?", use_container_width=True):
                st.session_state.example_question = "What causes OutOfMemoryError?"
                st.rerun()
            if st.button("How to prevent OOM errors?", use_container_width=True):
                st.session_state.example_question = "How to prevent OOM errors?"
                st.rerun()
        with example_cols[1]:
            if st.button("How do I fix Jenkins build failures?", use_container_width=True):
                st.session_state.example_question = "How do I fix Jenkins build failures?"
                st.rerun()
            if st.button("What are symptoms of memory issues?", use_container_width=True):
                st.session_state.example_question = "What are symptoms of memory issues?"
                st.rerun()

        st.divider()

        # Display chat history
        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

                # Show sources if available
                if "sources" in message and message["sources"]:
                    with st.expander("📚 Sources", expanded=False):
                        for source in message["sources"]:
                            st.markdown(f"""
                            <div style="background-color: #fff3e0; padding: 0.5rem; border-radius: 0.3rem; margin: 0.3rem 0; border-left: 3px solid #ff9800;">
                                📄 <strong>{source['filename']}</strong><br>
                                Relevance: {source['relevance']:.0%}
                            </div>
                            """, unsafe_allow_html=True)

                # Show metadata if available
                if "metadata" in message and message["metadata"]:
                    meta = message["metadata"]
                    st.markdown(f"""
                    <div>
                        <span style="background-color: #e8f5e9; padding: 0.2rem 0.5rem; border-radius: 0.3rem; font-size: 0.8rem; margin: 0.2rem;">
                            🎯 Chunks: {meta.get('chunks_used', 0)}
                        </span>
                        <span style="background-color: #e8f5e9; padding: 0.2rem 0.5rem; border-radius: 0.3rem; font-size: 0.8rem; margin: 0.2rem;">
                            🔢 Tokens: {meta.get('tokens_used', {}).get('total', 0)}
                        </span>
                        <span style="background-color: #e8f5e9; padding: 0.2rem 0.5rem; border-radius: 0.3rem; font-size: 0.8rem; margin: 0.2rem;">
                            📊 Confidence: {meta.get('confidence', 0):.0%}
                        </span>
                        {'<span style="background-color: #fff3e0; padding: 0.2rem 0.5rem; border-radius: 0.3rem; font-size: 0.8rem; margin: 0.2rem;">⚠️ Fallback</span>' if meta.get('is_fallback') else ''}
                    </div>
                    """, unsafe_allow_html=True)

        # Chat input
        user_input = None

        # Check if example question was clicked
        if 'example_question' in st.session_state:
            user_input = st.session_state.example_question
            del st.session_state.example_question
        else:
            user_input = st.chat_input("Type your question here...")

        if user_input:
            # Add user message to history
            st.session_state.chat_messages.append({
                "role": "user",
                "content": user_input
            })

            # Display user message
            with st.chat_message("user"):
                st.markdown(user_input)

            # Generate response
            with st.chat_message("assistant"):
                message_placeholder = st.empty()

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
                            with st.expander("📚 Sources", expanded=True):
                                for source in response['sources']:
                                    st.markdown(f"""
                                    <div style="background-color: #fff3e0; padding: 0.5rem; border-radius: 0.3rem; margin: 0.3rem 0; border-left: 3px solid #ff9800;">
                                        📄 <strong>{source['filename']}</strong><br>
                                        Relevance: {source['relevance']:.0%}
                                    </div>
                                    """, unsafe_allow_html=True)

                        # Display metadata
                        tokens_used = response.get('tokens_used', {}).get('total', 0)

                        st.markdown(f"""
                        <div>
                            <span style="background-color: #e8f5e9; padding: 0.2rem 0.5rem; border-radius: 0.3rem; font-size: 0.8rem; margin: 0.2rem;">
                                🎯 Chunks: {response['chunks_used']}
                            </span>
                            <span style="background-color: #e8f5e9; padding: 0.2rem 0.5rem; border-radius: 0.3rem; font-size: 0.8rem; margin: 0.2rem;">
                                🔢 Tokens: {tokens_used}
                            </span>
                            <span style="background-color: #e8f5e9; padding: 0.2rem 0.5rem; border-radius: 0.3rem; font-size: 0.8rem; margin: 0.2rem;">
                                📊 Confidence: {response['confidence']:.0%}
                            </span>
                            <span style="background-color: #e8f5e9; padding: 0.2rem 0.5rem; border-radius: 0.3rem; font-size: 0.8rem; margin: 0.2rem;">
                                ⏱️ Time: {response_time:.2f}s
                            </span>
                            {'<span style="background-color: #fff3e0; padding: 0.2rem 0.5rem; border-radius: 0.3rem; font-size: 0.8rem; margin: 0.2rem;">⚠️ Fallback</span>' if response['is_fallback'] else ''}
                        </div>
                        """, unsafe_allow_html=True)

                        # Update session state
                        st.session_state.total_queries += 1
                        st.session_state.total_tokens += tokens_used

                        # Add assistant message to history
                        st.session_state.chat_messages.append({
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
                        st.session_state.chat_messages.append({
                            "role": "assistant",
                            "content": error_message
                        })

        # Clear chat button
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.chat_messages = []
            st.session_state.total_queries = 0
            st.session_state.total_tokens = 0
            st.rerun()

# Footer
st.markdown("---")
st.markdown(
    "**AI DevOps Platform - UI** | "
    "[GitHub](https://github.com/satishrajv/AI-DevOps-chatbot) | "
    "Built with Streamlit"
)
