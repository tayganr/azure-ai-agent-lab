import os  
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient  
from azure.identity import DefaultAzureCredential  
  
# Agent Configuration
AGENT_NAME = "joke-agent"  
AGENT_MODEL = "gpt-4o-mini"  
AGENT_INSTRUCTIONS = (  
    "You are a humorous AI agent. Your task is to generate a joke based on the topic "  
    "provided by the user. Ensure the joke is light-hearted, appropriate, and relevant to the topic."  
)  
  
# User Message Configuration
USER_MESSAGE_CONTENT = "Microsoft"  

# Load environment variables from .env file  
load_dotenv()  

# Initialize the AI Project Client
project_client = AIProjectClient.from_connection_string(  
    credential=DefaultAzureCredential(),  
    conn_str=os.environ.get("PROJECT_CONNECTION_STRING")  
)  

# Create an agent  
agent = project_client.agents.create_agent(  
    model=AGENT_MODEL,  
    name=AGENT_NAME,  
    instructions=AGENT_INSTRUCTIONS,  
    tools=[]  
)  

# Create a thread  
thread = project_client.agents.create_thread()  

# Add a message to the thread  
message = project_client.agents.create_message(  
    thread_id=thread.id,  
    role="user",  
    content=USER_MESSAGE_CONTENT  
)

# Run the agent  
run = project_client.agents.create_and_process_run(  
    thread_id=thread.id,  
    assistant_id=agent.id  
)  

# Retrieve and print the agent's response  
messages = project_client.agents.list_messages(thread_id=thread.id)  
last_msg = messages.get_last_text_message_by_role("assistant")  
print(last_msg.text.value)  

# Clean up resources
project_client.agents.delete_agent(agent.id)  
project_client.agents.delete_thread(thread.id)
