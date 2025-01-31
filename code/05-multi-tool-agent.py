import os  
from azure.ai.projects import AIProjectClient  
from azure.ai.projects.models import BingGroundingTool, FileSearchTool, CodeInterpreterTool, ToolResources, FilePurpose  
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
bing_tool = BingGroundingTool(connection_id=conn_id)  
  
# Step 3: Set up file search and code interpreter tools  
# Upload files and add them to a Vector Store for file search  
file_search_file = project_client.agents.upload_file_and_poll(  
    file_path='./documents/product_catalog.pdf',  # Path to your file for file search  
    purpose=FilePurpose.AGENTS  
)  
print(f"Uploaded file for file search, file ID: {file_search_file.id}")  
  
vector_store = project_client.agents.create_vector_store_and_poll(  
    file_ids=[file_search_file.id],  
    name="my_vectorstore"  
)  
print(f"Created vector store, vector store ID: {vector_store.id}")  
  
# Upload a file for code interpretation  
code_interpreter_file = project_client.agents.upload_file_and_poll(  
    file_path="./documents/quarterly_results.csv",  # Path to your file for code interpretation  
    purpose=FilePurpose.AGENTS  
)  
print(f"Uploaded file for code interpretation, file ID: {code_interpreter_file.id}")  
  
# Create the tools  
file_search_tool = FileSearchTool(vector_store_ids=[vector_store.id])  
code_interpreter_tool = CodeInterpreterTool(file_ids=[code_interpreter_file.id])  
  
# Step 4: Combine the tools and resources using ToolResources class  
combined_tool_resources = ToolResources(  
    file_search=file_search_tool.resources['file_search'],  
    code_interpreter=code_interpreter_tool.resources['code_interpreter']  
)  
  
# Step 5: Create an agent with all tools including Bing  
agent = project_client.agents.create_agent(  
    model="gpt-4o",  
    name="my-combined-assistant",  
    instructions="You are a helpful assistant with access to file search, code interpretation, and Bing search capabilities.",  
    tools=(file_search_tool.definitions + code_interpreter_tool.definitions + bing_tool.definitions),  
    tool_resources=combined_tool_resources,  
    headers={"x-ms-enable-preview": "true"}  
)  
print(f"Created agent, ID: {agent.id}")  
  
# Step 6: Create a thread and add user messages  
thread = project_client.agents.create_thread()  
print(f"Created thread, ID: {thread.id}")  
  
# Add a user message for Bing search  
user_message_bing = project_client.agents.create_message(  
    thread_id=thread.id,  
    role="user",  
    content="Who is the current Prime Minister of the United Kingdom?"  
)  
print(f"Created user message for Bing, ID: {user_message_bing.id}")  
  
# Run the agent for the Bing search question  
run_bing = project_client.agents.create_and_process_run(  
    thread_id=thread.id,  
    assistant_id=agent.id  
)  
print(f"Bing run finished with status: {run_bing.status}")  
  
# Retrieve and print the agent's response for Bing search  
messages = project_client.agents.list_messages(thread_id=thread.id)  
last_msg_bing = messages.get_last_text_message_by_role("assistant")  
if last_msg_bing:  
    print(f"Agent Response to Bing Search: {last_msg_bing.text.value}")  
  
# Add a user message for file search  
user_message_file_search = project_client.agents.create_message(  
    thread_id=thread.id,  
    role="user",  
    content="Can you provide details about the AI-Powered Smart Hub?"  
)  
print(f"Created user message for file search, ID: {user_message_file_search.id}")  
  
# Run the agent for the file search question  
run_file_search = project_client.agents.create_and_process_run(  
    thread_id=thread.id,  
    assistant_id=agent.id  
)  
print(f"File search run finished with status: {run_file_search.status}")  
  
# Retrieve and print the agent's response for file search  
messages = project_client.agents.list_messages(thread_id=thread.id)  
last_msg_file_search = messages.get_last_text_message_by_role("assistant")  
if last_msg_file_search:  
    print(f"Agent Response to File Search: {last_msg_file_search.text.value}")  
  
# Add a user message for code interpretation  
user_message_code_interpreter = project_client.agents.create_message(  
    thread_id=thread.id,  
    role="user",  
    content="Could you please create a bar chart in the TRANSPORTATION sector for the operating profit from the uploaded CSV file and provide the file to me?"  
)  
print(f"Created user message for code interpretation, ID: {user_message_code_interpreter.id}")  
  
# Run the agent for the code interpretation question  
run_code_interpreter = project_client.agents.create_and_process_run(  
    thread_id=thread.id,  
    assistant_id=agent.id  
)  
print(f"Code interpretation run finished with status: {run_code_interpreter.status}")  
  
# Retrieve and print the agent's response for code interpretation  
messages = project_client.agents.list_messages(thread_id=thread.id)  
last_msg_code_interpreter = messages.get_last_message_by_role("assistant")  
if last_msg_code_interpreter:  
    text_messages = last_msg_code_interpreter.text_messages  
    if text_messages:  
        print(f"Agent Response to Code Interpretation: {text_messages[-1].text.value}")  
  
    # Check for file path annotations  
    for file_path_annotation in last_msg_code_interpreter.file_path_annotations:  
        file_path = file_path_annotation.file_path  
        file_id = file_path['file_id']  
        project_client.agents.save_file(file_id=file_id, file_name='chart.png', target_dir='./documents')  
        print(f"Saved file: {file_id} as chart.png")  
  
# Clean up resources  
project_client.agents.delete_vector_store(vector_store.id)  
print("Deleted vector store")  
  
project_client.agents.delete_file(code_interpreter_file.id)  
print("Deleted code interpreter file")  
  
project_client.agents.delete_agent(agent.id)  
print("Deleted agent")  