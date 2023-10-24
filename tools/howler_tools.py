import os
from pydantic import BaseModel, Field
from typing import Optional, Type, List
from langchain.tools import BaseTool
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from howler_client import get_client

from dotenv import load_dotenv

class HowlerSearchSchema(BaseModel):
    organization_name: str = Field(description="should be the name of an organization")
    subnet_name: str = Field(description="should be the name of a subnet")
    date_range: str = Field(description="Date range in string that follows the Elasticsearch nomenclature.")
    field_list: str = Field(description="""Comma separated list of fields to return. Possible values to select from are: 
           - howler.id: ID of alert
           - howler.analytic: Analytic that found the alert
           - howler.score: Score of the alert""")

class HowlerSearchStructuredTool(BaseTool):
    name = "Howler alerts and hits search"
    description = "Use to get a list of alerts and hits in Howler for a particular organization."
    args_schema: Type[HowlerSearchSchema] = HowlerSearchSchema

    def _run(
        self, organization_name: str, subnet_name: str, date_range: str, field_list: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Use this tool to get a list of alerts and hits in Howler for a particular organization.  It will return an array of JSON objects describing the alerts and hits found."""
        apikey = (os.getenv("HOWLER_USER"), os.getenv("HOWLER_API_KEY"))
        howler = get_client("https://howler.hogwarts.u.azure.chimera.cyber.gc.ca", apikey=apikey)
        query_string = f"howler.escalation:alert AND organization.name:{organization_name} AND howler.outline.threat:{subnet_name}*"
        print(f"Query string to Howler is {query_string}")
        print(f"Query date range is {date_range}")
        print(f"Query field list is {field_list}")
        out = howler.search.hit(query_string, 
                                filters=[f"event.created:[{date_range} TO now]"], fl=field_list, rows=10, 
                                offset=0)
        print(out)
        # return search.run(query)
        return out

    async def _arun(
        self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError(f"{self.name} does not support async")

class HowlerSearchTool(BaseTool):
    name = "Howler alerts ans hits search"
    description = """Use this tool to get a list of alerts and hits in Howler for a particular organization.  
        It will return an array of JSON objects describing the alerts and hits found.  The number of results
        returned will be found in the 'total' field.  If 'total' is zero, simply say that not result was found.

        The query string should look like: <field_list>; <organization_name>; <subnet_name>; <date_range>
        where 
          field_list is a comma separated list of fields to return. Possible values to select from are: 
           - howler.id: ID of alert
           - howler.analytic: Analytic that found the alert
           - howler.score: Score of the alert
          organization_name is the name of the organization to search for
          subnet_name is the name of the subnet
          date_range is the date range expressed as a Lucene date range expression
        """


    def _run(
        self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Use this tool to get a list of alerts and hits in Howler for a particular organization.  
        It will return an array of JSON objects describing the alerts and hits found.  The number of results
        returned will be found in the 'total' field.  If 'total' is zero, simply say that not result was found.
        """
        apikey = (os.getenv("HOWLER_USER"), os.getenv("HOWLER_API_KEY"))
        howler = get_client("https://howler.hogwarts.u.azure.chimera.cyber.gc.ca", apikey=apikey)
        fl, org, subnet, date_range = query.split(";")
        query_string = f"howler.escalation:alert AND organization.name:{org} AND howler.outline.threat:{subnet}*"
        print(f"Query string to Howler is {query_string}")
        out = howler.search.hit(query_string, 
                                filters=["event.created:[now-365d TO now]"], fl="howler.score,howler.*", rows=10, 
                                offset=0)
        print(out)
        # return search.run(query)
        return out

    async def _arun(
        self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError(f"{self.name} does not support async")
