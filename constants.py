context_prompt = """
You are given a question and context.
Your task is to find answer for the query from the context.
Keep the answer short and precise.
Your answers should revolve around the provided context.
If inquired about capabilities or background information, give a general brief overview derived from the context.
Also, 
Question: {question}
Context: {context}

Answer:
"""

system_rag_prompt_template = """ 
You are an assistant for question answering. You are given a question 
and a set of documents. 
Your task is to find the most relevant document that answers
"""

GREETING_MESSAGE = """
Hello , How can I help you?
"""
