import os
import re
from langchain_openai import ChatOpenAI


openai_generic_client = ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY", ""),
    model="gpt-4o",
)

generic_prompt = """ 

You are an AI assistant that determines which specialized agent should handle a given user query. The available agents are:

general_agent: This agent handles generic queries.
personal_concierge_agent: This agent handles queries related to a user's personal account details, for example orders and purchase history.

Your task is to analyze the input query and output the name of the agent that should handle it, formatted as:

Agent: <agent_name>

Where <agent_name> is either "general_agent" or "personal_concierge_agent".

Do not provide any additional response or execute the agent's functionality. Simply output the agent name based on the input query.

Input Query: {input}

Agent:

"""


def router_agent(query):
    """ 
    Generic agent inorder to make desicion for the chatbot
    """
    prompt_with_input = generic_prompt.format(input=query)
    response = openai_generic_client.invoke(
        input=prompt_with_input
    )
    # Use regular expression to extract agent name from response
    agent_pattern = r"Agent:\s*(general_agent|personal_concierge_agent)"
    match = re.search(agent_pattern, response.content, re.IGNORECASE)

    if match:
        agent_name = match.group(1)
        print(f"Routing to {agent_name.replace('_', ' ').title()} Agent")
        return agent_name
    else:
        print("Invalid response from the agent")
        return None
