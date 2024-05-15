import streamlit as st

from chat_utils import generate_rag_response


def render_chat_interface():
    """
  Render the chat interface for question-answering.
  """
    col1, col2 = st.columns(2)
    with col1:
        clear_button = st.button('Clear')
    with col2:
        voice_button = st.toggle("Voice")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if clear_button:
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
            response = generate_rag_response(prompt)
            st.markdown("AI: {}".format(response))
            st.session_state.messages.append({
                "role":
                "AI",
                "content":
                "AI: {}".format(response)
            })


