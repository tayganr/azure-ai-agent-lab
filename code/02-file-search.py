import os  
from azure.ai.projects import AIProjectClient  
from azure.ai.projects.models import FileSearchTool, FilePurpose  
from azure.identity import DefaultAzureCredential  
  
# Set up the credentials and client  
credential = DefaultAzureCredential()  
project_client = AIProjectClient.from_connection_string(  
    credential=credential,  
    conn_str=os.environ["PROJECT_CONNECTION_STRING"]  
)  
  
# Step 2: Upload files and add them to a Vector Store  
file = project_client.agents.upload_file_and_poll(  
    file_path='./documents/product_catalog.pdf',  # Specify the path to your local file  
    purpose=FilePurpose.AGENTS  
)  
print(f"Uploaded file, file ID: {file.id}")  
  
vector_store = project_client.agents.create_vector_store_and_poll(  
    file_ids=[file.id],  
    name="my_vectorstore"  
)  
print(f"Created vector store, vector store ID: {vector_store.id}")  
  
# Step 3: Create an agent and enable file search  
file_search_tool = FileSearchTool(vector_store_ids=[vector_store.id])  
  
agent = project_client.agents.create_agent(  
    model="gpt-4o-mini",  
    name="my-agent",  
    instructions=(  
        "You are a helpful assistant. Your responses should be based solely on the information "  
        "available in the provided documents. If you cannot find the relevant information, "  
        "please respond with 'I couldn't find the information in the documents provided.'"  
    ),   
    tools=file_search_tool.definitions,  
    tool_resources=file_search_tool.resources,  
)  
print(f"Created agent, agent ID: {agent.id}")  
  
# Step 4: Create a thread and add a user message  
thread = project_client.agents.create_thread()  
print(f"Created thread, thread ID: {thread.id}")  
  
# Create a user message asking about the product  
user_message = project_client.agents.create_message(  
    thread_id=thread.id,  
    role="user",  
    content="Can you provide details about the AI-Powered Smart Hub?"  
)  
print(f"Created user message, message ID: {user_message.id}")  
  
# Step 5: Run the agent  
run = project_client.agents.create_and_process_run(  
    thread_id=thread.id,  
    assistant_id=agent.id  
)  
print(f"Run finished with status: {run.status}")  
  
if run.status == "failed":  
    print(f"Run failed: {run.last_error}")  
  
# Retrieve and print the agent's response  
messages = project_client.agents.list_messages(thread_id=thread.id)  
last_msg = messages.get_last_text_message_by_role("assistant")  
if last_msg:  
    print(f"Agent Response: {last_msg.text.value}")  
  
# Clean up resources  
project_client.agents.delete_vector_store(vector_store.id)  
print("Deleted vector store")  
  
project_client.agents.delete_agent(agent.id)  
print("Deleted agent")  