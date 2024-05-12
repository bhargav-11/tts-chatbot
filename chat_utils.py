import os

import streamlit as st
from openai import AzureOpenAI, OpenAI

# Azure OpenAI client
azure_openai_client = AzureOpenAI(azure_endpoint=os.getenv(
    "AZURE_OPENAI_ENDPOINT", ""),
                                  api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                                  api_version="2023-12-01-preview")

# OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


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
    model_mapping = {"3.5": "gpt-3.5-turbo-16k", "4.0": "gpt-4-0125-preview"}
    return model_mapping.get(gpt_version, "gpt-3.5-turbo-16k")
