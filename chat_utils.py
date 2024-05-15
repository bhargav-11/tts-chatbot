import os

import streamlit as st
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI as LangChainOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from openai import AzureOpenAI, OpenAI
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv
from constants import context_prompt, system_rag_prompt_template

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
    
    if "retriever" not in st.session_state:
        return chat(query, use_azure=False)

    system_prompt_template = st.session_state.general_agent_system_message or system_rag_prompt_template

    prompt = system_prompt_template + context_prompt
    prompt_template = ChatPromptTemplate.from_template(prompt)

    retriever = st.session_state.retriever
    rag_chain = ({
        "context": retriever,
        "question": RunnablePassthrough()
    }
                 | prompt_template
                 | langchain_openai_client
                 | StrOutputParser())
    response = rag_chain.invoke(query)
    return response


def generate_qa_chain(documents):
    """
    Generate qa chain

    Args:
        documents (list): List of documents.

    Returns:
        qa_chain (QAChain): The QA chain.
    """
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=0)
    texts = text_splitter.create_documents(documents)
    embeddings = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"), model="text-embedding-3-small")

    db = Chroma.from_documents(texts, embeddings)
    # Create retriever interface
    retriever = db.as_retriever(search_kwargs={"k": 4})

    qa_chain = RetrievalQA.from_chain_type(llm=langchain_openai_client,
                                           chain_type='stuff',
                                           retriever=retriever)
    return qa_chain


def get_retriever_from_documents(documents):
    """ 
    Generate retriever from documents

    Args:
        documents (list): List of documents.

    Returns:
        retriever (Retriever): The retriever.
    """
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=0)
    texts = text_splitter.create_documents(documents)
    embeddings = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))

    db = Chroma.from_documents(texts, embeddings)
    # Create retriever interface
    retriever = db.as_retriever(search_kwargs={"k": 4})

    return retriever

def generate_qa_chain_with_custom_prompt(documents):
    """
    Generate qa chain

    Args:
        documents (list): List of documents.
        system_prompt (str): System prompt.

    Returns:
        qa_chain (QAChain): The QA chain.
    """
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=0)
    texts = text_splitter.create_documents(documents)
    embeddings = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))

    db = Chroma.from_documents(texts, embeddings)
    # Create retriever interface
    retriever = db.as_retriever(search_kwargs={"k": 4})

    system_prompt_template = st.session_state.general_agent_system_message or system_rag_prompt_template

    prompt = system_prompt_template + context_prompt
    prompt_template = ChatPromptTemplate.from_template(prompt)

    retriever = st.session_state.retriever
    rag_chain = ({
        "context": retriever,
        "question": RunnablePassthrough()
    }
                 | prompt_template
                 | langchain_openai_client
                 | StrOutputParser())
    
    return rag_chain
