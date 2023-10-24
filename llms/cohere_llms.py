from typing import Any
from langchain.embeddings import CohereEmbeddings
from langchain.llms import Cohere
from langchain.agents import AgentExecutor
from dotenv import load_dotenv

#load environment variables
load_dotenv()

def create_llm(temp=0.4, max_tokens=2000):
    return Cohere(model="command-nightly", temperature=temp, max_tokens=max_tokens)
    
def create_cohere_embedder():
    return CohereEmbeddings(model = "multilingual-22-12")

def run_in_agent(agent: AgentExecutor, query: Any) -> Any:
    return agent.run(query)
