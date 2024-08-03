import streamlit as st
import base64
from audiorecorder import audiorecorder

from audio_utils import convert_audio_to_text, convert_text_to_audio
from chat_utils import generate_personal_agent_response, generate_rag_response
from constants import GREETING_MESSAGE
from file_utils import remove_all_files_in_folder
from router_agent import router_agent
from validation_agent import extract_user_info, get_security_question

def add_message(role, content,audio_file_name=None):
    st.session_state.messages.append({
        "role": role,
        "content": content,
        "audio_file_name":audio_file_name if audio_file_name else None
    })

def send_chat_message(role, content):
    audio_file_name=None

    if role== "assistant" or role== "validation_agent":
        audio_file_name = f"audio/message{len(st.session_state.messages)}.wav"
        convert_text_to_audio(content,audio_file_name)

    add_message(role, content,audio_file_name)
    
    with st.chat_message(role):
        st.markdown(content)
        if audio_file_name:
            st.audio(audio_file_name,autoplay=True)
        


def prompt_user_for_data():
    send_chat_message("assistant", "Please upload your data to validate.")

def prompt_user_for_phone_and_name():
    send_chat_message("assistant", "Please provide your phone number and first name.")

def handle_validation_stage_0(prompt):
    if "user_data" not in st.session_state:
        prompt_user_for_data()
    elif not st.session_state["prompt_user_for_phone_and_name"]:
        prompt_user_for_phone_and_name()
        st.session_state.prompt_user_for_phone_and_name= True
    else:
        phone_number, first_name = extract_user_info(prompt)
        selected_question, correct_answer,user_id = get_security_question(phone_number, first_name, st.session_state.user_data)

        if selected_question and correct_answer:
            st.session_state.selected_question = selected_question
            st.session_state.correct_answer = correct_answer
            st.session_state.user_id = user_id
            send_chat_message("assistant", f"Security Question: {selected_question}")
            st.session_state.validation_stage = 1
        else:
            send_chat_message("assistant", "User not found. Please check your phone number and first name.")
            st.session_state.validation_stage = 0

def handle_validation_stage_1(prompt):
    if 'validation_attempts' not in st.session_state:
        st.session_state.validation_attempts = 0

    max_attempts = 3

    if prompt.lower() == st.session_state.correct_answer.lower():
        send_chat_message("assistant", "Thanks for validating your identity. How can I help?")
        st.session_state.is_user_validated = True
        st.session_state.validation_stage = 0
        st.session_state.validation_attempts = 0  # Reset attempts
    else:
        st.session_state.validation_attempts += 1
        
        if st.session_state.validation_attempts < max_attempts:
            remaining_attempts = max_attempts - st.session_state.validation_attempts
            send_chat_message("assistant", f"Incorrect answer. You have {remaining_attempts} {'attempts' if remaining_attempts > 1 else 'attempt'} left. Please try again.")
            st.session_state.validation_stage = 1  # Keep in validation stage
        else:
            send_chat_message("assistant", "Maximum attempts reached. Validation failed. Please start over with your phone number and first name.")
            st.session_state.validation_stage = 0
            st.session_state.validation_attempts = 0  # Reset attempts

def handle_general_agent(prompt):
    response = generate_rag_response(prompt)
    send_chat_message("assistant", response)

def handle_personal_concierge_agent(query):
    response = generate_personal_agent_response(query)
    send_chat_message("assistant", response)

def clear_and_reset_all_session_state():
    st.session_state.transcribed_text = ""
    st.session_state.is_user_validated = False
    st.session_state.validation_stage = 0
    st.session_state.prompt_user_for_phone_and_name = False
    st.session_state.user_validation_invoked =False
    st.session_state.user_id = None

def render_chat_interface():
    """
  Render the chat interface for question-answering.
  """
    if "transcribed_text" not in st.session_state:
        st.session_state.transcribed_text = ""
    if "is_user_validated" not in st.session_state:
        st.session_state.is_user_validated = False

    if "validation_stage" not in st.session_state:
        st.session_state.validation_stage = 0
    
    if "prompt_user_for_phone_and_name" not in st.session_state:
        st.session_state.prompt_user_for_phone_and_name = False
    
    if "user_validation_invoked" not in st.session_state:
        st.session_state.user_validation_invoked =False
    
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    
    if "prompt_greeting_message" not in st.session_state:
        st.session_state.prompt_greeting_message = False

    col1, col2 = st.columns([6,1], gap="large")
    with col1:
        clear_button = st.button('Clear')
    with col2:
        audio = audiorecorder("🎙️", "⏹️")

        if len(audio) > 0:
            audio.export("audio.wav", format="wav")
            transcribed_text = convert_audio_to_text("audio.wav")
            if transcribed_text == st.session_state.transcribed_text:
                st.session_state.transcribed_text = ""
            else:
                st.session_state.transcribed_text = transcribed_text

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if clear_button:
        st.session_state.messages = []
        remove_all_files_in_folder("audio")
        clear_and_reset_all_session_state()

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["audio_file_name"]:
                st.audio(message["audio_file_name"])

    prompt = st.chat_input("Enter your message:", key="chat_input")

    js = f"""
        <script>
            function insertText(dummy_var_to_force_repeat_execution) {{
                var chatInput = parent.document.querySelector('textarea[data-testid="stChatInputTextArea"]');
                var nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value").set;
                nativeInputValueSetter.call(chatInput, "{st.session_state.transcribed_text}");
                var event = new Event('input', {{ bubbles: true}});
                chatInput.dispatchEvent(event);
            }}
            insertText({len(st.session_state.messages)});
        </script>
        """
    if not st.session_state.prompt_greeting_message:
        send_chat_message("assistant",GREETING_MESSAGE)
        st.session_state.prompt_greeting_message=True
    if prompt:
        send_chat_message("user", prompt)
        
        if st.session_state.user_validation_invoked and not st.session_state.is_user_validated:
            if st.session_state.validation_stage == 0:
                handle_validation_stage_0(prompt)
            elif st.session_state.validation_stage == 1:
                handle_validation_stage_1(prompt)
        else:
            response=router_agent(prompt)
            if response == "general_agent":
                handle_general_agent(prompt)
            elif response == "personal_concierge_agent":
                if not st.session_state.is_user_validated:
                    st.session_state.user_validation_invoked =True
                    if st.session_state.validation_stage == 0:
                        handle_validation_stage_0(prompt)
                    elif st.session_state.validation_stage == 1:
                        handle_validation_stage_1(prompt)
                else:
                    handle_personal_concierge_agent(prompt)
        
    st.components.v1.html(js, height=0)