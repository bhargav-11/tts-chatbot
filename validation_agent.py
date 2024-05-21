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

        return phone_number, first_name
    except Exception as e:
        print("Error extracting user information:", e)
        return None,None


# My name is John and phone number is 555-123-4567


def get_security_question(phone_number, first_name, user_data):
    try:
       user = user_data[(user_data['PhoneNumber'] == phone_number)
                        & (user_data['FirstName'] == first_name)]

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
           return None, None
           
    except Exception as e:
        print("Error getting security question:", e)
        return None,None


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

        print("Phone number:", phone_number, "\n\n", "First Name:", first_name)
        selected_question, correct_answer = get_security_question(
            phone_number, first_name, user_data)

        print("Security Questions:", selected_question, "\n\n", "Answer:",
              correct_answer, "\n\n\n")
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
