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

# Sidebar configuration
st.sidebar.title("Jenkins Configuration")

jenkins_url = st.sidebar.text_input(
    "Jenkins URL",
    value=os.getenv("JENKINS_URL", "http://localhost:8080"),
    help="Base URL of your Jenkins server"
)

jenkins_user = st.sidebar.text_input(
    "Jenkins Username",
    value=os.getenv("JENKINS_USER", ""),
    help="Jenkins username for API authentication"
)

jenkins_token = st.sidebar.text_input(
    "Jenkins API Token",
    type="password",
    value=os.getenv("JENKINS_TOKEN", ""),
    help="Jenkins API token (generate from User > Configure > API Token)"
)

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


# Tab layout
tab1, tab2, tab3 = st.tabs(["🎯 Trigger Jobs", "📊 Job Status", "📋 All Jobs"])

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

# Footer
st.markdown("---")
st.markdown(
    "**AI DevOps Platform** | "
    "[GitHub](https://github.com/satishrajv/AI-DevOps-chatbot) | "
    "Built with Streamlit"
)
