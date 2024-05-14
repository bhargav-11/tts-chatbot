import os

import streamlit as st
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI as LangChainOpenAI
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from openai import AzureOpenAI, OpenAI

# Azure OpenAI client
azure_openai_client = AzureOpenAI(azure_endpoint=os.getenv(
    "AZURE_OPENAI_ENDPOINT", ""),
                                  api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                                  api_version="2023-12-01-preview")

# OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# LangChain OpenAI client
langchain_openai_client = LangChainOpenAI(api_key=os.getenv(
    "OPENAI_API_KEY", ""))


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

    client = azure_openai_client if use_azure else openai_client
    model = get_model_name(st.session_state.gpt_version)
    print("Prompt :", prompt)
    res = client.chat.completions.create(model=model,
                                         messages=[
                                             {
                                                 "role":
                                                 "system",
                                                 "content":
                                                 "You are a helpful assistant."
                                             },
                                             {
                                                 "role": "user",
                                                 "content": prompt
                                             },
                                         ])
    response = res.choices[0].message.content
    return response


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
        return chat(query,use_azure=False)
    
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
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=0)
    texts = text_splitter.create_documents(documents)
    embeddings = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))

    db = Chroma.from_documents(texts, embeddings)
    # Create retriever interface
    retriever = db.as_retriever()

    qa_chain = RetrievalQA.from_chain_type(llm=langchain_openai_client, chain_type='stuff', retriever=retriever)
    return qa_chain