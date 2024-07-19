import os

import pandas as pd
import streamlit as st

from chat_utils import get_retriever_from_documents

openai_api_key = os.getenv("OPENAI_API_KEY")


def set_sidebar_width():
    """
    Inject custom CSS to set the width of the sidebar.
    """
    st.markdown(
        """
        <style>
        section[data-testid="stSidebar"] {
        width: 400px !important; # Set the width to your             desired value
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def configure_gpt_model():
    """
    Render a dropdown to select the GPT model version.
    """
    if "gpt_version" not in st.session_state:
        st.session_state.gpt_version = "4o"

    st.selectbox(
            label="Choose LLM provider",
            options=("4o","4o-mini"),
            key="gpt_version"
        )


def save_changes(general_agent_system_message,validation_agent_system_message,personal_agent_system_message):
    """
    Render a button to save changes and update the GPT model version.
    """
    if "general_agent_system_message" not in st.session_state:
        st.session_state.general_agent_system_message = general_agent_system_message

    if "validation_agent_system_message" not in st.session_state:
        st.session_state.validation_agent_system_message = validation_agent_system_message

    if "personal_agent_system_message" not in st.session_state:
        st.session_state.personal_agent_system_message = personal_agent_system_message

    st.session_state.general_agent_system_message = general_agent_system_message
    st.session_state.personal_agent_system_message = personal_agent_system_message

    col1, col2 = st.columns(2)

    with col1:
        configure_gpt_model()

    with col2:
        vert_space = '<div style="padding: 14px 10px;"></div>'
        st.markdown(vert_space, unsafe_allow_html=True)
        if st.button("Save Changes"):
            st.session_state.general_agent_system_message = general_agent_system_message
            st.session_state.validation_agent_system_message = validation_agent_system_message

            st.success("Changes saved!")


def configure_sidebar():
    """
    Render the sidebar with agent configuration options.
    """
    with st.sidebar:
        st.header("Agent Configuration")
        st.divider()

        st.subheader("General Agent")
        general_agent_system_message = st.text_area(
            "System message", "Define general agent behavior here.")

        uploaded_files = st.file_uploader("Upload Files",
                                          accept_multiple_files=True,
                                          type=["txt"],
                                          key="general_agent")
        if uploaded_files:
            for uploaded_file in uploaded_files:

                documents = [uploaded_file.read().decode()]

                retriever = get_retriever_from_documents(documents)

                if "retriever" not in st.session_state:
                    st.session_state.retriever = retriever

        st.divider()

        st.subheader("Validation Agent")
        validation_agent_system_message=st.text_area("System message", "Define validation behavior here.")
        uploaded_files = st.file_uploader("Upload Files",
                                          accept_multiple_files=True,
                                          key="validation_agent")
        if uploaded_files:
            for uploaded_file in uploaded_files:
                st.write("Filename is:", uploaded_file.name)
                user_data = pd.read_csv(uploaded_file)

                st.session_state.user_data = user_data
                

        st.divider()

        st.subheader("Personal Concierge Agent")
        personal_agent_system_message= st.text_area("System message", "Define personal agent behavior here.")
        uploaded_files = st.file_uploader("Upload Files",
                                          accept_multiple_files=True,
                                          key="personal_agent")
        if uploaded_files:
            for uploaded_file in uploaded_files:
                st.write("Filename:", uploaded_file.name)
                if uploaded_file.type == "text/csv":
                    user_transactional_data= pd.read_csv(uploaded_file)
                    st.session_state.user_transactional_data = user_transactional_data
                
                if uploaded_file.type == "text/plain":
                    text_documents = [uploaded_file.read().decode()]
                    personal_agent_retriever = get_retriever_from_documents(text_documents)
                    if "personal_agent_retriever":
                        st.session_state.personal_agent_retriever= personal_agent_retriever

        st.divider()

        save_changes(general_agent_system_message,validation_agent_system_message,personal_agent_system_message)
