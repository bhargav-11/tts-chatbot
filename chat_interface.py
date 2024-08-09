import streamlit as st
import base64
from audiorecorder import audiorecorder
from pydub import AudioSegment

from audio_utils import convert_audio_to_text, convert_text_to_audio
from chat_utils import chat, generate_personal_agent_response, generate_rag_response
from constants import GREETING_MESSAGE
from file_utils import remove_all_files_in_folder
from router_agent import router_agent
from validation_agent import extract_user_info, get_security_question, get_security_question_using_id, validate_security_question

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

def custom_prompt_to_user_based_on_instructions():
    if st.session_state.st.session_state.validation_agent_system_message is None:
        send_chat_message("assistant", "Please provide your phone number and first name.")
        return
    
    instructions = st.session_state.validation_agent_system_message
    prompt = f"""Follow the instructions provided below :
        instructions :{instructions} 
        Based on the instructions , Provide a simple string as a response which contains the question which needs to be asked as a validation agent.
        Example:
        Instructions :

        Your job is to validate the identity of the calling user by asking them for exactly 4 things: first name, last name, phone number, and a random one of three possible security questions (Mother's maiden name, first elementary school name, first pet name). If you can find their record in the supplied users.csv file, then they are a validated user.  If not, they have up to 5 attempts to get this right. 

        You do this by asking the user to identify their first and last name as well as their phone number on file. 
        You should then look up the first name, last name, and phone number in the attached users.csv file to see if that record exists.  
        If it does not, see if there are any records that match the first name and last name, but not the phone number. In that case, ask the user to try again with a different phone number.
        Allow up to 5 attempts to find the first name / last name / phone number combination and if all five attempts fail, offer to put the user through to a live agent.  

        Otherwise, if the record is found, randomly ask the user to supply one of 1. their mother's maiden name, 2. their first elementary school name or 3. their first pet name.  
        These are security questions. Once the user answers, make sure their answer matches the data stored in users.csv for that first name / last name/ phone number.  
        If it does, thank the user by first name for identifying themselves and ask what you can do for them. If it does not, appologize and tell them the answer doesn't match, and to please try again. Allow them up to 3 attempts to get the security question correct.  If not, appologize that you cannot authenticate them and ask if they would like to be transferred to a live agent.  
        Output: Please provide your first name , last name and phone number.
        """
    response = chat(prompt, use_azure=False)
    send_chat_message(response.lower())

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

    max_attempts = st.session_state.max_attempts

    if validate_security_question(st.session_state.correct_answer, prompt):
        send_chat_message("assistant", "Thanks for validating your identity. How can I help?")
        st.session_state.is_user_validated = True
        st.session_state.validation_stage = 0
        st.session_state.validation_attempts = 0  # Reset attempts
    else:
        st.session_state.validation_attempts += 1
        
        if st.session_state.validation_attempts < max_attempts:
            remaining_attempts = max_attempts - st.session_state.validation_attempts
            INCORRECT_ANSWER_AI_RESPONSE =  f"Incorrect answer. You have {remaining_attempts} {'attempts' if remaining_attempts > 1 else 'attempt'} left. Please try again."
            selected_question, correct_answer = get_security_question_using_id(st.session_state.user_id, st.session_state.user_data)
            if selected_question and correct_answer:
                st.session_state.selected_question = selected_question
                st.session_state.correct_answer = correct_answer
                security_question =f"Security Question: {selected_question}"
                INCORRECT_ANSWER_AI_RESPONSE += security_question
            
            send_chat_message("assistant",INCORRECT_ANSWER_AI_RESPONSE)
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
    
    if "max_attempts" not in st.session_state:
        st.session_state.max_attempts = 3 

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