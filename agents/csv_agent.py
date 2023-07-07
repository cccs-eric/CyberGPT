import os
import boto3
import pandas as pd
from llms.azure_llms import create_llm
from langchain.agents import create_csv_agent
from langchain.agents.agent_types import AgentType

llm = create_llm(temp=0)

print("Creating CSV Agent.")
combined_data = os.path.join("data", "combined.csv")
df = pd.read_csv(combined_data)

# mitre_dir = "../data"
# mitre_data = [os.path.join(mitre_dir, fn) for fn in ["software.csv", "groups.csv", "mitigations.csv"]]
# if not os.path.exists(combined_data):
#     combined_df = None
#     keys = ['TID', 'Technique Name']
#     for fp in mitre_data:
#         next_df = pd.read_csv(fp)
#         if combined_df is not None:
#             combined_df = combined_df.merge(
#                 next_df,
#                 on=['TID', 'Technique Name'],
#                 how='outer'
#             )
#         else:
#             combined_df = next_df
    
#     combined_df.to_csv(combined_data)


# Waiting on Secret Key info for Amazon.
def download_files(bucket_name="team5.2-mitre", data_dir="data", files=[]):
    s3_client = boto3.client('s3')
    os.makedirs(data_dir, exist_ok=True)
    for fn in files:
        fp = os.path.join(data_dir, fn)
        if not os.path.exists(fp):
            print(f"Downloading {fn}")
            s3_client.download_file(bucket_name, fn, fp)

download_files(files=["combined.csv"])


mitre_csv_agent = create_csv_agent(
    llm,
    combined_data,
    verbose=True,
    agent_type=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION, # Added CHAT_
)
print("Finished Creating CSV Agent.")

#agent.run("What Techniques does FlawedAmmyy use?")
