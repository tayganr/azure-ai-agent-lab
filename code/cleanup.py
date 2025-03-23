import os  
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient  
from azure.identity import DefaultAzureCredential  

# Set to True to only display resources without deleting them
# Set to False to actually delete resources
DRY_RUN = False

# Load environment variables from .env file
print("Loading environment variables...")
load_dotenv()

# Initialize the AI Project Client  
project_conn_str = os.environ.get("PROJECT_CONNECTION_STRING")
project_client = AIProjectClient.from_connection_string(  
    credential=DefaultAzureCredential(),  
    conn_str=project_conn_str
)  

mode = "Displaying" if DRY_RUN else "Cleaning up"

# Agents
print(f"{mode} agents...")
agents = project_client.agents.list_agents()

for agent in agents.data:
    print(agent.id, agent.name)
    if not DRY_RUN:
        project_client.agents.delete_agent(agent.id)
        print(f"Deleted agent {agent.id}")

# Files
print(f"\n{mode} files...")
files = project_client.agents.list_files()

for file in files.data:
    print(file.id)
    if not DRY_RUN:
        project_client.agents.delete_file(file.id)
        print(f"Deleted file {file.id}")

# Vector stores
print(f"\n{mode} vector stores...")
vector_stores = project_client.agents.list_vector_stores()

for vector_store in vector_stores.data:
    print(vector_store.id, vector_store.name)
    if not DRY_RUN:
        project_client.agents.delete_vector_store(vector_store.id)
        print(f"Deleted vector store {vector_store.id}")

if DRY_RUN:
    print("\nDry run completed. No resources were deleted.")
else:
    print("\nCleanup completed successfully. All resources were deleted.")