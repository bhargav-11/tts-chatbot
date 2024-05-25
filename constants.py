context_prompt = """
Keep the answer short and precise.
Question: {question}
Context: {context}
"""

system_rag_prompt_template = """ 
You are an assistant for question answering. You are given a question 
and a set of documents. 
Your task is to find the most relevant document that answers
"""
