import os  
from azure.ai.projects import AIProjectClient  
from azure.ai.projects.models import CodeInterpreterTool, FilePurpose  
from azure.identity import DefaultAzureCredential  
  
# Step 1: Create an Azure AI Client from a connection string  
project_client = AIProjectClient.from_connection_string(  
    credential=DefaultAzureCredential(),   
    conn_str=os.environ["PROJECT_CONNECTION_STRING"]  
)  
  
# Step 2: Upload a file  
file = project_client.agents.upload_file_and_poll(  
    file_path="./documents/quarterly_results.csv",  # Specify the path to your local CSV file  
    purpose=FilePurpose.AGENTS  
)  
print(f"Uploaded file, file ID: {file.id}")  
  
# Step 3: Create an agent with the code interpreter tool  
code_interpreter = CodeInterpreterTool(file_ids=[file.id])  
  
# Create agent with code interpreter tool and tools_resources  
agent = project_client.agents.create_agent(  
    model="gpt-4o-mini",  # Ensure to use a supported model  
    name="my-agent",  
    instructions="You are a helpful agent.",  
    tools=code_interpreter.definitions,  
    tool_resources=code_interpreter.resources,  
)  
print(f"Created agent, ID: {agent.id}")  
  
# Step 4: Create a thread and a user message  
thread = project_client.agents.create_thread()  
print(f"Created thread, thread ID: {thread.id}")  
  
# Create a user message that triggers the code interpreter tool  
message = project_client.agents.create_message(  
    thread_id=thread.id,  
    role="user",  
    content="Could you please create a bar chart in the TRANSPORTATION sector for the operating profit from the uploaded CSV file and provide the file to me?"  
)  
print(f"Created message, message ID: {message.id}")  
  
# Step 5: Create and execute a run  
run = project_client.agents.create_and_process_run(  
    thread_id=thread.id,  
    assistant_id=agent.id  
)  
print(f"Run finished with status: {run.status}")  
  
if run.status == "failed":  
    # Check if you got "Rate limit is exceeded.", then you want to get more quota  
    print(f"Run failed: {run.last_error}")  
  
# Step 6: Delete the original file from the agent to free up space  
project_client.agents.delete_file(file.id)  
print("Deleted file")  
  
# Step 7: Print the messages from the agent  
messages = project_client.agents.list_messages(thread_id=thread.id)  
  
# Step 8: Download files generated by the code interpreter  
# Retrieve the last message from the assistant  
last_msg = messages.get_last_message_by_role("assistant")  
  
if last_msg:  
    # Retrieve the text messages from the last message  
    text_messages = last_msg.text_messages  # Get all text messages in the last assistant message  
      
    # Print the content of the last text message  
    if text_messages:  
        print(f"Last Message: {text_messages[-1].text.value}")
  
    # Check for file path annotations  
    for file_path_annotation in last_msg.file_path_annotations:  
        file_path = file_path_annotation.file_path 
        file_id = file_path['file_id']
        project_client.agents.save_file(file_id=file_id, file_name='chart.png', target_dir='./documents')  
        print(f"Saved file: {file_id} as chart.png")