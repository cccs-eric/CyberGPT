import argparse
import http
import os
from langchain import PromptTemplate, LLMChain
from langchain.agents import load_tools, initialize_agent, AgentType, AgentExecutor
from langchain.tools import StructuredTool
from langchain.memory import ConversationBufferMemory
from langchain.prompts import MessagesPlaceholder

from tools.borealis_tools_cohere import borealis_tool
from tools.ipapi_tools import ipapi_tool
from tools.datahub_tool import DatahubSearchTool
from tools.howler_tools import HowlerSearchStructuredTool, HowlerSearchTool

from dotenv import load_dotenv

from gql import Client
from gql.transport.requests import RequestsHTTPTransport

import logging

def enable_verbose():
    logging.basicConfig(level=logging.DEBUG)
    http.client.HTTPConnection.debuglevel = 1
    os.environ["LANGCHAIN_TRACING"] = "true" # If you want to trace the execution of the program, set to "true"

def ask_copilot_chain(question: str, llm) -> str:
    template = """Question: {question}

    Answer: Let's think step by step."""

    prompt = PromptTemplate(template=template, input_variables=["question"])
    llm_chain = LLMChain(prompt=prompt, llm=llm)
    return llm_chain.run(question)

def ask_copilot_agent_graphql(question: str, llm) -> str:
    # tools = load_tools(["ddg-search", "llm-math", "graphql"], llm=llm, graphql_endpoint="https://datahub.hogwarts.u.azure.chimera.cyber.gc.ca/api/graphiql")
    # tools = load_tools(["graphql"], graphql_endpoint="https://swapi-graphql.netlify.app/.netlify/functions/index")
    access_token = "eyJhbGciOiJIUzI1NiJ9.eyJhY3RvclR5cGUiOiJVU0VSIiwiYWN0b3JJZCI6IkVyaWMuTGFkb3VjZXVyQGN5YmVyLmdjLmNhIiwidHlwZSI6IlBFUlNPTkFMIiwidmVyc2lvbiI6IjIiLCJqdGkiOiI2ZDRmNDRlNS1mNmZmLTRmZGEtODIxYS05MjQ0MWQ1ZGI4YmIiLCJzdWIiOiJFcmljLkxhZG91Y2V1ckBjeWJlci5nYy5jYSIsImV4cCI6MTY5NTQ3Nzg1NSwiaXNzIjoiZGF0YWh1Yi1tZXRhZGF0YS1zZXJ2aWNlIn0.GNgH2jWeREG8mIuey3THDYcRQPR2rJ9PSMEzUcW9Wpw"
    auth_headers = {'Authorization': 'Bearer ' + access_token}
    graphql_endpoint = "https://datahub.hogwarts.u.azure.chimera.cyber.gc.ca/api/graphql"
    transport = RequestsHTTPTransport(url=graphql_endpoint, headers=auth_headers)
    client = Client(transport=transport, fetch_schema_from_transport=True)

    tools = load_tools(["graphql"], graphql_endpoint=graphql_endpoint, custom_headers=auth_headers)
    
    # Waiting for https://github.com/langchain-ai/langchain/pull/8187 to be merged, until then, there is a bug with auth
    tools[0].graphql_wrapper.gql_client.transport = client.transport
    # tools.append(borealis_tool)
    # tools.append(ipapi_tool)
    tools.append(DatahubSearchTool())
    agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)
    graphql_fields = """allFilms {
        films {
        title
        director
        releaseDate
        speciesConnection {
            species {
            name
            classification
            homeworld {
                name
            }
            }
        }
        }
    }

    """
    s = """
    {
    dataset {
        properties {
            name
        }
    }
    }
    """

    suffix = "Search for the titles of all the datasets stored in the graphql database that has this schema "
    return agent.run(suffix + s)
    # return agent.run(question)

def ask_copilot_agent(question: str, llm) -> str:
    access_token = "eyJhbGciOiJIUzI1NiJ9.eyJhY3RvclR5cGUiOiJVU0VSIiwiYWN0b3JJZCI6IkVyaWMuTGFkb3VjZXVyQGN5YmVyLmdjLmNhIiwidHlwZSI6IlBFUlNPTkFMIiwidmVyc2lvbiI6IjIiLCJqdGkiOiI2ZDRmNDRlNS1mNmZmLTRmZGEtODIxYS05MjQ0MWQ1ZGI4YmIiLCJzdWIiOiJFcmljLkxhZG91Y2V1ckBjeWJlci5nYy5jYSIsImV4cCI6MTY5NTQ3Nzg1NSwiaXNzIjoiZGF0YWh1Yi1tZXRhZGF0YS1zZXJ2aWNlIn0.GNgH2jWeREG8mIuey3THDYcRQPR2rJ9PSMEzUcW9Wpw"
    auth_headers = {'Authorization': 'Bearer ' + access_token}

    tools = []
    # tools.append(borealis_tool)
    # tools.append(ipapi_tool)
    tools.append(DatahubSearchTool())
    agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)
    return agent.run(question)

def ask_copilot_agent_openapi(question: str, llm) -> str:
    import json
    from langchain.agents.agent_toolkits.openapi import planner
    from langchain.agents.agent_toolkits.openapi.spec import reduce_openapi_spec
    from langchain.requests import RequestsWrapper
    with open("tools/datahub_openapi_spec.json") as f:
        raw_datahub_api_spec = json.load(f)
    datahub_api_spec = reduce_openapi_spec(raw_datahub_api_spec)
    # Get API credentials.
    access_token = "eyJhbGciOiJIUzI1NiJ9.eyJhY3RvclR5cGUiOiJVU0VSIiwiYWN0b3JJZCI6IkVyaWMuTGFkb3VjZXVyQGN5YmVyLmdjLmNhIiwidHlwZSI6IlBFUlNPTkFMIiwidmVyc2lvbiI6IjIiLCJqdGkiOiI2ZDRmNDRlNS1mNmZmLTRmZGEtODIxYS05MjQ0MWQ1ZGI4YmIiLCJzdWIiOiJFcmljLkxhZG91Y2V1ckBjeWJlci5nYy5jYSIsImV4cCI6MTY5NTQ3Nzg1NSwiaXNzIjoiZGF0YWh1Yi1tZXRhZGF0YS1zZXJ2aWNlIn0.GNgH2jWeREG8mIuey3THDYcRQPR2rJ9PSMEzUcW9Wpw"
    auth_headers = {'Authorization': 'Bearer ' + access_token}
    requests_wrapper = RequestsWrapper(headers=auth_headers)
    agent = planner.create_openapi_agent(datahub_api_spec, requests_wrapper, llm)
    return agent.run(question)

def get_copilot_agent_agent_howler_structured(llm) -> AgentExecutor:

    tools = [HowlerSearchStructuredTool()]
    # tools = [StructuredTool.from_function(HowlerSearchStructuredTool()._run)]
    agent_kwargs = {
        "extra_prompt_messages": [MessagesPlaceholder(variable_name="chat_history")],
    }
    memory = ConversationBufferMemory(memory_key="chat_history")
    agent = initialize_agent(tools, llm, agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION, verbose=True, 
                             agent_kwargs=agent_kwargs, memory=memory)
    return agent

def get_copilot_agent_agent_howler(llm) -> AgentExecutor:
    tool = HowlerSearchTool()
    tools = [tool]
    agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True, max_iterations=5)
    return agent

def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description="Analytical platform Copilot")
    parser.add_argument("-l","--llm", help="Name of LLM to use", required=False, default="OpenAI")
    parser.add_argument("-d","--debug", help="To enable verbose/debug information", action="store_true")
    args = parser.parse_args()
    if args.debug:
        enable_verbose()
    if args.llm.casefold() == "OpenAI".casefold():
        from llms.azure_llms import create_llm, run_in_agent
    elif args.llm.casefold() == "Cohere".casefold():
        from llms.cohere_llms import create_llm, run_in_agent
    else:
        raise ValueError(f"--llm value not supported: {args.llm}")
    llm = create_llm(temp=0.0)

    # answer = ask_copilot_chain("What NFL team won the Super Bowl in the year Justin Beiber was born?")
    # answer = ask_copilot_chain("Which team won the Stanley Cup in the second year of Barrack Obama's presidency and which player got the Conn Smythe trophy?")
    # answer = ask_copilot_agent("Which team won the Stanley Cup in 2023?")
    # answer = ask_copilot_agent("What was the weather like in Montreal on July 1st 2023?")
    # answer = ask_copilot_agent("What do you know about ip 1.1.1.1, present the result in a table formatted using markdown")
    
    # Datahub OpenAPI questions
    datahub_urn = "urn:li:dataset:(urn:li:dataPlatform:iceberg,hogwarts_u.opensource.aws_btc_blocks,PROD)"
    # answer = ask_copilot_agent_openapi("What datasets do you know?", llm)
    answer = ask_copilot_agent_openapi(f"Get the latest information about entity '{datahub_urn}'", llm)

    # Howler questions
    # agent = get_copilot_agent_agent_howler()
    # answer = get_copilot_agent_agent_howler_structured(llm).run("Search for alerts occurring at VRAB in the last year that came from the 206 subnet.  Return their ID and score fields and list everything in a Markdown table.")

    # Random questions
    # answer = agent.run("Which NFL team won the Super Bowl in 2023?")
    # print(answer)
    # answer = agent.run("Who was their quarterback?  Give the name of the player and the name of his team")

    # Show results
    print(answer)

if __name__ == "__main__":
    main()

