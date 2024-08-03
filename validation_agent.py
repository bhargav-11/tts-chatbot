import random

import streamlit as st

from chat_utils import chat


def extract_user_info(user_input):
    try:
        # Prepare the prompt for the LLM
        prompt = f"Extract the phone number and first name from the following user input: '{user_input}'.Provide the answer in the following format: 'Phone Number: 123-456-7890, First Name: John'. If the user input does not contain a phone number or first name, provide 'no' as the answer."

        # Call the LLM API
        response = chat(prompt, use_azure=False)

        # Return None if the response starts with no
        if response.lower().startswith("no") or response is None:
            return None, None

        # Parse the LLM response
        extracted_info = response.strip().split(", ")
        phone_number = extracted_info[0].split(": ")[1]
        first_name = extracted_info[1].split(": ")[1]

        return phone_number, first_name.lower()
    except Exception as e:
        print("Error extracting user information:", e)
        return None, None


# My name is Sofia and phone number is 555-369-2580

def get_security_question_using_id(user_id,user_data):
    try:
        user = user_data[(user_data['ID'] ==user_id)]
        if not user.empty:
            security_questions = {
                'What is your mother\'s maiden name?':
                user['MothersMaidenName'].values[0],
                'What was the name of your first elementary school?':
                user['FirstElementarySchoolName'].values[0],
                'What was the name of your first pet?':
                user['FirstPetName'].values[0]
            }

            question = random.choice(list(security_questions.keys()))
            answer = security_questions[question]

            return question, answer
        else:
            return None,None
    except Exception as e:
        print("Error getting security question:", e)
        return None, None


def get_security_question(phone_number, first_name, user_data):
    try:
        user = user_data[(user_data['PhoneNumber'] == phone_number)
                       & (user_data['FirstName'].str.lower() == first_name)]

        if not user.empty:
            
            security_questions = {
                'What is your mother\'s maiden name?':
                user['MothersMaidenName'].values[0],
                'What was the name of your first elementary school?':
                user['FirstElementarySchoolName'].values[0],
                'What was the name of your first pet?':
                user['FirstPetName'].values[0]
            }

            question = random.choice(list(security_questions.keys()))
            answer = security_questions[question]
            user_id = user['ID'].values[0]
            return question, answer,user_id
        else:
            return None, None ,None

    except Exception as e:
        print("Error getting security question:", e)
        return None, None,None

def validate_security_question(security_question_correct_answer,user_answer_for_security_question):
    try:
        instructions = st.session_state.validation_agent_system_message or "Check if the correct answer and user answer are same or not."
        prompt = f"""
        Please follow the given instructions carefully. You will receive both a 
        correct answer and a user answer. 
        Your task is to validate the user answer and correct answer based on the provided instructions and
        return true if they match as per the instructions, or false if they do not.

        Instructions: {instructions}
        Correct answer: {security_question_correct_answer}
        User answer: {user_answer_for_security_question}

       Your response should be in the following format:
        - true or false (indicating whether the answers match according to the instructions)
        - Max attempts (if mentioned in the instructions), or 'Not specified' if not mentioned.

        Provide the response in a single line, comma-separated:
        - Example: true, 3
        - Example: false, Not specified
        """

        # Call the LLM API
        response = chat(prompt, use_azure=False)
        
        parts = response.split(',')
        match_result = parts[0].strip()
        max_attempts = parts[1].strip() if len(parts) > 1 else None

        if max_attempts and max_attempts != 'Not specified' :
            st.session_state.max_attempts =int(max_attempts)

        # Return true if the response starts has true
        if "true" in match_result.lower():
            return True
        
        return False
       
    except Exception as e:
        print("Error extracting user information:", e)
        return security_question_correct_answer.lower() == user_answer_for_security_question


def validate_user(user_data):
    with st.chat_message("validation_agent"):
        st.markdown("Please provide your phone number and first name")
    user_input = st.chat_input("Enter your information:", key="user_info")
    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })
        phone_number, first_name = extract_user_info(user_input)

        selected_question, correct_answer = get_security_question(
            phone_number, first_name, user_data)
        
        if selected_question:
            with st.chat_message("validation_agent"):
                st.markdown(f"Security Question: {selected_question}")
            answer = st.chat_input("Please enter your answer:",
                                   key="security_answer")

            if answer.lower() == correct_answer.lower():
                with st.chat_message("validation_agent"):
                    st.markdown(
                        "Validation successful! You can now chat with the assistant."
                    )
                return True
            else:
                with st.chat_message("validation_agent"):
                    st.markdown("Incorrect answer. Please try again.")
                return False
        else:
            with st.chat_message("validation_agent"):
                st.markdown(
                    "User not found. Please check your phone number and first name."
                )
            return False
