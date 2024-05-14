import os

import streamlit as st
from langchain.chains import RetrievalQA
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import Chroma
from openai import AzureOpenAI, OpenAI
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

load_dotenv()

# Azure OpenAI client
azure_openai_client = AzureOpenAI(azure_endpoint=os.getenv(
    "AZURE_OPENAI_ENDPOINT", ""),
                                  api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                                  api_version="2023-12-01-preview")

# OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# LangChain OpenAI client
langchain_openai_client = ChatOpenAI(api_key=os.getenv(
    "OPENAI_API_KEY", ""), model_name=st.session_state.gpt_version if "gpt_version" in st.session_state else "gpt-3.5-turbo-16k")


def chat(prompt, use_azure=True):
    """
    Send a chat prompt to the OpenAI API or Azure OpenAI API and return the response.

    Args:
        prompt (str): The prompt to send to the API.
        use_azure (bool, optional): Whether to use the Azure OpenAI API or the OpenAI API.
            Defaults to True.

    Returns:
        str: The response from the API.
    """

    client = azure_openai_client if use_azure else langchain_openai_client
    response = client.invoke(input=prompt)
    return response.content


def get_model_name(gpt_version):
    """
    Get the model name for the specified GPT version.

    Args:
        gpt_version (str): The GPT version.

    Retruns:
        str: The model name.
    """
    model_mapping = {"3.5": "gpt-3.5-turbo-16k", "4.0": "gpt-4-0125-preview"}
    return model_mapping.get(gpt_version, "gpt-3.5-turbo-16k")

def generate_rag_response(query):
    """
    Generate a response using the RAG pipeline.

    Args:
        query (str): The query to generate a response using qa_chain.

    Returns:
        str: The generated response.
    """
   
    if "qa_chain" not in st.session_state:
        return chat(query, use_azure=False)
    
    response = st.session_state.qa_chain.run(query)
    return response       
    
def generate_qa_chain(documents):
    """
    Generate qa chain

    Args:
        documents (list): List of documents.

    Returns:
        qa_chain (QAChain): The QA chain.
    """
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    texts = text_splitter.create_documents(documents)
    embeddings = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"), model="text-embedding-3-small")

    db = Chroma.from_documents(texts, embeddings)
    retriever = db.as_retriever()

    print(st.session_state.general_agent_system_message)

    base_prompt = '''
    You are a helpful assistant to respond to user queries based on the provided context.
    '''
    template = '''
    {base_prompt}

    {{context}}

    Question: {{question}}
    Answer:
    '''.format(base_prompt=st.session_state.general_agent_system_message if "general_agent_system_message" in st.session_state else base_prompt)

    prompt = PromptTemplate(
        template=template,
        input_variables=[
            'context', 
            'question',
        ]
    )

    qa_chain = RetrievalQA.from_llm(llm=langchain_openai_client, retriever=retriever, prompt=prompt)
    return qa_chain
