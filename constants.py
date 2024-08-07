general_agent_rag_prompt = """
You are given a question and context.
Your task is to find answer for the query from the context.
Keep the answer short and precise.
Your answers should revolve around the provided context.
If the user greets you in their question, start your answer with a greeting as well.
If inquired about capabilities or background information, give a general brief overview derived from the context.
Question: {question}
Context: \n\n {context}

Answer:
"""

personal_agent_rag_prompt = """
You are given a question , context and user data.
Your task is to find answer for the query from the context and the user data.
Your answers should revolve arount the provided context and user data.
Understand the question and think step by step and provide answer to the question.

Question : {question}
User data : {user_data}
Context : {context}

Answer:
"""
personal_agent_with_user_data = """
You are given a question and user data.
Your task is to find answer based on the user data.
Understand the question and think step by step and provide answer to the question.

Question : {question}
User data: {user_data}

Answer:
"""


system_rag_prompt_template = """ 
You are an assistant for question answering. You are given a question 
and a set of documents. 
Your task is to find the most relevant document that answers
"""

default_system_prompt = """
You are a helpful assistant.
"""

GREETING_MESSAGE = """
Hello There, Greetings! I am an AI assistant. I am here to help you with your queries.
"""
