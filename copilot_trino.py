import argparse
from typing import Any
from langchain.sql_database import SQLDatabase
from langchain.agents import create_sql_agent, AgentExecutor
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.agents.agent_types import AgentType
from trino.auth import OAuth2Authentication

import http
import logging
import os

# logging.basicConfig(level=logging.DEBUG)
# http.client.HTTPConnection.debuglevel = 1
# os.environ["LANGCHAIN_TRACING"] = "true" # If you want to trace the execution of the program, set to "true"

# catalog = "hogwartsu"
# schema = "opensource"
catalog = "hogwartsusersu"
schema = "erladou"
engine_args={
    "connect_args": {
        "auth": OAuth2Authentication(),
        "http_scheme": "https",
    }
}

def main():
    parser = argparse.ArgumentParser(description="Analytical platform Copilot")
    parser.add_argument("-l","--llm", help="Name of LLM to use", required=False, default="OpenAI")
    args = parser.parse_args()
    if args.llm.casefold() == "OpenAI".casefold():
        from llms.azure_llms import create_llm, run_in_agent
    elif args.llm.casefold() == "Cohere".casefold():
        from llms.cohere_llms import create_llm, run_in_agent
    else:
        raise ValueError(f"--llm value not supported: {args.llm}")

    db = SQLDatabase.from_uri(database_uri=f"trino://trino.hogwarts.u.azure.chimera.cyber.gc.ca:443/{catalog}", engine_args=engine_args, 
                            schema=schema)
    llm = create_llm(temp=0.0)

    agent_executor = create_sql_agent(
        llm=llm,
        toolkit=SQLDatabaseToolkit(db=db, llm=llm),
        verbose=True,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    )

    result = run_in_agent(agent_executor,
        # "List the total sales per country. Which country's customers spent the most?"
        # "List the available tables in opensource.  Display as markdown."
        # "What are the top 5 domain listed in opensource.cisco_top1m?"
        # "I have an IPv4 address as an integer: 16777222.  Find the country associated with it by using the neustar_geo_ipv4 table."
        # "Give me the subdomain and TLD of the most recent subdomain according to its last seen date."
        # "I have an IPv4 address as an integer: 2222222.  Find the country and the range associated with it by using geolocation information found in table ipv4_geolocation.  You will need to check that the input value is between start_ip_int and end_ip_int.  start_ip_int and end_ip_int and the lower and upper bound of the range.  In order to convert an IPv4 address from an integer to a string, you can use the following function: cast(substr(to_big_endian_64(ip_as_integer), 5, 4) as IPADDRESS)"
        # "I have an IPv4 address as an integer: 2222222.  Find the country and the range associated with it by using geolocation information found in table ipv4_geolocation."
        # "I have an IPv4 address as an integer: 2222222.  Find the country and the range associated with it by using geolocation information found in table ipv4_geolocation.  Display each IPv4 address from the range as a string instead of an integer.  To convert an IPv4 address from an integer to a string, you can use the following Trino SQL function: 'cast(substr(to_big_endian_64(ip_as_integer), 5, 4) as IPADDRESS)' where ip_as_integer is the name of the column holding the IPv4 address to convert."
        "I have an IPv4 address as an integer: 2222222.  Find the country and the range associated with it by using a geolocation dataset.  Display each IPv4 address from the range as a string instead of an integer.  To convert an IPv4 address from an integer to a string, you can use the following Trino SQL function: 'cast(substr(to_big_endian_64(ip_as_integer), 5, 4) as IPADDRESS)' where ip_as_integer is the name of the column holding the IPv4 address to convert. Present everything in a Markdown tble."
    )
    print(f"Copilot answer: {result}")

if __name__ == "__main__":
    main()
