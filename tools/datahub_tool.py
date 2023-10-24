import json
import yaml
from typing import Optional
from langchain.tools import BaseTool, Tool
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain.agents.agent_toolkits.openapi import planner
from langchain.agents.agent_toolkits.openapi.spec import reduce_openapi_spec

# with open("tools/datahub_openapi_spec.json") as f:
#     raw_datahub_api_spec = json.load(f)
# datahub_api_spec = reduce_openapi_spec(raw_datahub_api_spec)
# with open("tools/datahub_openapi_spec.yaml", encoding="utf8", errors='ignore') as f:
#     raw_datahub_api_spec = yaml.load(f, Loader=yaml.Loader)
# datahub_api_spec = reduce_openapi_spec(raw_datahub_api_spec)

class DatahubSearchTool(BaseTool):
    name = "datahub_search"
    description = "useful for when you need to answer questions about datasets"

    def _run(
        self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool."""
        # return search.run(query)
        return "this is the list of datasets found in datahub: 1. ip_data 2. geo_data 3. domain_data"

    async def _arun(
        self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError(f"{self.name} does not support async")
