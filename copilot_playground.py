import inspect
import re
import os

from llms.cohere_llms import create_llm
from langchain.llms import Cohere
from langchain import PromptTemplate
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate
from langchain.chains import LLMChain, LLMMathChain, TransformChain, SequentialChain, ConversationChain
from langchain.chains.conversation.memory import ConversationBufferMemory, ConversationBufferWindowMemory
from langchain.callbacks import get_openai_callback

from dotenv import load_dotenv
import logging

def count_tokens(chain, query):
    with get_openai_callback() as cb:
        result = chain.run(query)
        print(f'Spent a total of {cb.total_tokens} tokens')

    return result

def create_prompt_template() -> PromptTemplate:
    system_template = SystemMessagePromptTemplate.from_template("You are a cyber AI assistant specialized in answering questions using and regarding the CCCS Hogwarts analytical platform.")
    human_template = HumanMessagePromptTemplate.from_template("{question}")
    chat_template = ChatPromptTemplate.from_messages([system_template, human_template])
    print(chat_template)
    return PromptTemplate(template=chat_template, input_variables=["question"])

def main():
    logging.basicConfig(level=logging.DEBUG)
    # http.client.HTTPConnection.debuglevel = 1
    # os.environ["LANGCHAIN_TRACING"] = "true" # If you want to trace the execution of the program, set to "true".  It will go to localhost:8000

    load_dotenv()
    llm = create_llm(temp=0)
    memory = ConversationBufferWindowMemory(memory_key="history", k=3, return_messages=True)
    prompt = create_prompt_template()
    conversation_chain = ConversationChain(llm=llm, memory=memory, prompt=prompt, verbose=True)
    result = conversation_chain.run("Good morning! My favorite color is red.")
    print(result)
    # print(f"\n\nMemory: {conversation_chain.memory.buffer}")

if __name__ == "__main__":
    main()