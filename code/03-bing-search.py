import os  
from azure.ai.projects import AIProjectClient  
from azure.ai.projects.models import BingGroundingTool  
from azure.identity import DefaultAzureCredential  
  
# Step 1: Set up the credentials and client  
credential = DefaultAzureCredential()  
project_client = AIProjectClient.from_connection_string(  
    credential=credential,  
    conn_str=os.environ["PROJECT_CONNECTION_STRING"]  
)  
  
# Step 2: Enable the Grounding with Bing search tool  
bing_connection = project_client.connections.get(  
    connection_name=os.environ["BING_CONNECTION_NAME"]  
)  
conn_id = bing_connection.id  
print(f"Bing connection ID: {conn_id}")  
  
# Initialize the Bing Grounding tool and add the connection ID  
bing = BingGroundingTool(connection_id=conn_id)  
  
# Create the agent with the Bing tool  
agent = project_client.agents.create_agent(  
    model="gpt-4o",  # Make sure you use a supported model  
    name="my-assistant",  
    instructions="You are a helpful assistant.",  
    tools=bing.definitions,  
    headers={"x-ms-enable-preview": "true"}  
)  
print(f"Created agent, ID: {agent.id}")  
  
# Step 3: Create a thread for communication  
thread = project_client.agents.create_thread()  
print(f"Created thread, ID: {thread.id}")  
  
# Create a user message to the thread  
user_message = project_client.agents.create_message(  
    thread_id=thread.id,  
    role="user",  
    content="who is the current Prime Minister of the United Kingdom?"  
)  
print(f"Created user message, ID: {user_message.id}")  
  
# Step 4: Create and process the agent run with tools  
run = project_client.agents.create_and_process_run(  
    thread_id=thread.id,  
    assistant_id=agent.id  
)  
print(f"Run finished with status: {run.status}")  
  
# Retrieve run step details to get Bing Search query link  
run_steps = project_client.agents.list_run_steps(run_id=run.id, thread_id=thread.id)  
run_steps_data = run_steps['data']  
print(f"Last run step detail: {run_steps_data}")  

# Retrieve and print the agent's response  
messages = project_client.agents.list_messages(thread_id=thread.id)  
last_msg = messages.get_last_text_message_by_role("assistant")  
  
if last_msg:  
    print(f"Agent Response: {last_msg.text.value}")  
  
# Check for errors  
if run.status == "failed":  
    print(f"Run failed: {run.last_error}")  
  
# Delete the assistant when done  
project_client.agents.delete_agent(agent.id)  
print("Deleted agent")  
