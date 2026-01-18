"""
AI DevOps Platform - Streamlit Dashboard
Trigger and monitor Jenkins jobs via API
"""

import streamlit as st
import requests
from requests.auth import HTTPBasicAuth
import time
import os

# Page configuration
st.set_page_config(
    page_title="AI DevOps Platform",
    page_icon="🚀",
    layout="wide"
)

# Jenkins configuration - hardcoded credentials
jenkins_url = "http://35.174.138.165:8080"
jenkins_user = "admin"
jenkins_token = "0b94639151854a66bf03c6467e5a7101"

# Main content
st.title("🚀 AI DevOps Platform")
st.markdown("### Trigger and Monitor Jenkins CI/CD Pipelines - 5 minutes")

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


# Tab layout
tab1, tab2, tab3, tab4 = st.tabs(["🎯 Trigger Jobs", "📊 Job Status", "📋 All Jobs", "📝 Build Logs"])

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

# Footer
st.markdown("---")
st.markdown(
    "**AI DevOps Platform - UI** | "
    "[GitHub](https://github.com/satishrajv/AI-DevOps-chatbot) | "
    "Built with Streamlit"
)
