import os

import streamlit as st
from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from openai import AzureOpenAI, OpenAI

from constants import general_agent_rag_prompt, system_rag_prompt_template,personal_agent_rag_prompt,personal_agent_with_user_data,default_system_prompt

load_dotenv()

# Azure OpenAI client
azure_openai_client = AzureOpenAI(azure_endpoint=os.getenv(
    "AZURE_OPENAI_ENDPOINT", ""),
                                  api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                                  api_version="2023-12-01-preview")

# OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# LangChain OpenAI client
langchain_openai_client = ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY", ""),
    model="gpt-4o",
    verbose=True
)

def get_openai_client(gpt_version="4o"):

    model_name = "gpt-4o"

    if gpt_version == "4o-mini":
        model_name = "gpt-4o-mini"
        
    return ChatOpenAI(
                api_key=os.getenv("OPENAI_API_KEY", ""),
                model=model_name,
                verbose=True
            )
    


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

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

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

    prompt_template = ChatPromptTemplate.from_messages([
        ("system",system_prompt_template),
        ("human", general_agent_rag_prompt),
        ("ai", "Answer: ")
    ])
    retriever = st.session_state.retriever


    llm_client = get_openai_client(st.session_state.gpt_version)

    rag_chain = ({
        "context": retriever | format_docs ,
        "question": RunnablePassthrough()
    }
                 | prompt_template
                 | llm_client
                 | StrOutputParser())
    response = rag_chain.invoke(query)
    
    return response


def generate_personal_agent_response(query):
    if "personal_agent_retriever" not in st.session_state and "user_transactional_data" not in st.session_state:
        return chat(query, use_azure=False)

    user_data = "None"
    
    if "user_transactional_data" in st.session_state:
        user_data_json = get_user_related_data_in_json(st.session_state.user_transactional_data)
        user_data = json_to_str(user_data_json)

    system_prompt_template = st.session_state.personal_agent_system_message or default_system_prompt

    if "personal_agent_retriever" not in st.session_state:
        prompt_with_user_data = system_prompt_template + "\n\n" + personal_agent_with_user_data.format(question=query, user_data=user_data)
        response = chat(prompt_with_user_data, use_azure=False)
        return response

    

    prompt_with_user_data = personal_agent_rag_prompt.format(user_data=user_data,question="{question}",context="{context}")

    prompt_template = ChatPromptTemplate.from_messages([
        ("system",system_prompt_template),
        ("human", prompt_with_user_data),
    ])

    personal_agent_retriever = st.session_state.personal_agent_retriever

    llm_client = get_openai_client(st.session_state.gpt_version)
    

    rag_chain = ({
        "context": personal_agent_retriever,
        "question": RunnablePassthrough(),
    }
                 | prompt_template
                 | llm_client
                 | StrOutputParser())
    response = rag_chain.invoke(query)
    return response

def get_retriever_from_documents(documents):
    """ 
    Generate retriever from documents

    Args:
        documents (list): List of documents.

    Returns:
        retriever (Retriever): The retriever.
    """
    text_splitter = CharacterTextSplitter(chunk_size=100, chunk_overlap=50)
    texts = text_splitter.create_documents(documents)
    embeddings = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))

    db = Chroma.from_documents(texts, embeddings)

    # Create retriever interface
    retriever = db.as_retriever(search_kwargs={"k": 5})

    return retriever

def get_user_related_data_in_json(user_transactional_data):
    try:
        user_id =st.session_state.user_id
        user_data = user_transactional_data[user_transactional_data['UserID'] == user_id]
        user_data_json = user_data.to_json(orient='records')
        return user_data_json
    except Exception as e:
        print("Error occured while getting user data",e)
        return None

def json_to_str(json_data):
    return json_data.replace("{", "{{").replace("}", "}}")
