import streamlit as st

def main():
    st.title("AI Bot")

    # Inject custom CSS to set the width of the sidebar
    st.markdown(
        """
        <style>
            section[data-testid="stSidebar"] {
                width: 500px !important; # Set the width to your desired value
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
    # Sidebar configuration
    with st.sidebar:
        st.header("Agent Configuration")
        st.divider()

        # Sections for different types of agents
        st.subheader("General Agent")
        st.text_area("System message", "Define general agent behavior here.")
        uploaded_files = st.file_uploader("Upload Files", accept_multiple_files=True, key="general_agent")
        if uploaded_files:
            for uploaded_file in uploaded_files:
                st.write("Filename:", uploaded_file.name)
        st.divider()


        st.subheader("Validation Agent")
        st.text_area("System message", "Define validation behavior here.")
        uploaded_files = st.file_uploader("Upload Files", accept_multiple_files=True, key="validation_agent")
        if uploaded_files:
            for uploaded_file in uploaded_files:
                st.write("Filename:", uploaded_file.name)
        st.divider()

        st.subheader("Personal Concierge Agent")
        st.text_area("System message", "Define personal agent behavior here.")
        uploaded_files = st.file_uploader("Upload Files", accept_multiple_files=True, key="personal_agent")
        if uploaded_files:
            for uploaded_file in uploaded_files:
                st.write("Filename:", uploaded_file.name)
        st.divider()

        # Dropdown for GPT model version
        gpt_version = st.selectbox("Choose GPT Model", ['3.5', '4.0'])

        # Button to save changes
        if st.button("Save Changes"):
            st.success("Changes saved!")

    col1, col2 = st.columns(2)

    with col1:
        clear_button = st.button('Clear')

    with col2:
        voice_button = st.toggle("Voice")
    
    if clear_button:
        st.session_state.messages = []
    
    # Handling user prompts for question-answering
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("How can I help you?", key="chat_input")
    if prompt:
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            st.markdown("AI: {}".format(prompt))
        st.session_state.messages.append({"role": "AI", "content": "AI: {}".format(prompt)})

if __name__ == "__main__":
    main()
