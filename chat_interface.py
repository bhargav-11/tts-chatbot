import streamlit as st

from chat_utils import generate_rag_response
from validation_agent import extract_user_info, get_security_question


def render_chat_interface():
    """
  Render the chat interface for question-answering.
  """
    if "is_user_validated" not in st.session_state:
        st.session_state.is_user_validated = False

    if "validation_stage" not in st.session_state:
        st.session_state.validation_stage = 0
        
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

    prompt_printed = False

    if "user_data" in st.session_state and not st.session_state.is_user_validated and st.session_state.validation_stage==0 and not prompt_printed:
        with st.chat_message("validation_agent"):
            st.markdown("Please provide your phone number and first name.")
        prompt_printed = True
    
    prompt = st.chat_input("Enter your message:", key="chat_input")

    if prompt:
        if not st.session_state.is_user_validated:
            if st.session_state.validation_stage == 0:
                if "user_data" not in st.session_state:
                    with st.chat_message("validation_agent"):
                        st.markdown("Please upload your data to validate.")
                    st.session_state.messages.append({"role": "validation_agent", "content": "Please upload your data to validate."})
                else:
                    with st.chat_message("user"):
                        st.markdown(prompt)
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    phone_number, first_name = extract_user_info(prompt)
                    selected_question, correct_answer = get_security_question(phone_number, first_name, st.session_state.user_data)
                    if selected_question and correct_answer:
                        st.session_state.selected_question = selected_question
                        st.session_state.correct_answer = correct_answer
                        with st.chat_message("validation_agent"):
                            st.markdown(f"Security Question: {st.session_state.selected_question}")
                            st.session_state.messages.append({"role":"validation_agent","content":f"Security Question: {st.session_state.selected_question}"})
                        st.session_state.validation_stage = 1
                    else:
                        with st.chat_message("validation_agent"):
                            st.markdown("User not found. Please provide your phone number and first name.")
                        st.session_state.messages.append({"role": "validation_agent", "content": "User not found.Please check your phone number and first name."})
                        st.session_state.validation_stage = 0
            
            elif st.session_state.validation_stage == 1:
                with st.chat_message("user"):
                    st.markdown(prompt)
                st.session_state.messages.append({"role":"user","content":prompt})
                    
                if prompt.lower() == st.session_state.correct_answer.lower():
                    with st.chat_message("validation_agent"):
                        st.markdown("Validation successful! You can now chat with the assistant.")
                    st.session_state.messages.append(
                        {"role": "validation_agent", "content": "Validation successful! You can now chat with the assistant."})
                    st.session_state.is_user_validated = True
                    st.session_state.validation_stage = 0
                else:
                    with st.chat_message("validation_agent"):
                        st.markdown("Incorrect answer. Please try again.Provde your phone number and first name.")
                    st.session_state.messages.append({"role":"validation_agent","content":"Incorrect answer. Please try again.Provde your phone number and first name."})
                    st.session_state.validation_stage = 0
                    
        else:
            with st.chat_message("user"):
                st.markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("assistant"):
                response = generate_rag_response(prompt)
                st.markdown(response)
                st.session_state.messages.append({"role": "AI", "content": response})