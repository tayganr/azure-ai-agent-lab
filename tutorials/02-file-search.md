# Tutorial 02: Integrating File Search  
   
[< Previous Module](./01.md) - [Home](../README.md) - [Next Module >](./03-bing-search.md)  
   
Welcome to the second tutorial in the Azure AI Agent Service series! In this tutorial, we will guide you through the process of integrating file search capabilities into your AI agent. This enhancement will allow your agent to respond to user queries based on the information contained in uploaded documents.  
   
## Step 1: Prerequisites  
   
Before starting this tutorial, ensure you have completed the setup as described in the [Technical Prerequisites](../README.md#-technical-prerequisites) section of the README. Key steps include:  
   
- **Python Environment**: Python 3.8 or later should be installed and configured.  
- **Azure CLI**: Install Azure CLI and log in to your subscription.  
- **Repository Setup**: Clone the repository and set up a Python virtual environment.  
- **Install Dependencies**: Use `pip` to install the required packages from `requirements.txt`.  
- **Environment Variable**: Ensure the `PROJECT_CONNECTION_STRING` is set.  
   
## Step 2: Write and Configure the Python Code  
   
Open your preferred text editor and create a new Python file. Copy and paste the following comprehensive code into the file. This script handles file upload, vector store creation, agent setup with file search capabilities, running the agent, and cleaning up resources.  
   
```python  
import os  
  
from azure.ai.projects import AIProjectClient  
from azure.ai.projects.models import FilePurpose, FileSearchTool  
from azure.identity import DefaultAzureCredential  
  
# === Environment Variables ===  
PROJECT_CONNECTION_STRING_ENV = "PROJECT_CONNECTION_STRING"  
  
# === Agent Configuration ===  
AGENT_NAME = "file-search-agent"  
AGENT_MODEL = "gpt-4o-mini"  
AGENT_INSTRUCTIONS = (  
    "You are a helpful assistant. Your responses should be based solely on the information "  
    "available in the provided documents. If you cannot find the relevant information, "  
    "please respond with 'I couldn't find the information in the documents provided.'"  
)  
  
# === Operational Constants ===  
FILE_PATH = './documents/product_catalog.pdf'  # Path to the local file to upload  
VECTOR_STORE_NAME = "my_vectorstore"  
USER_MESSAGE_CONTENT = "Can you provide details about the AI-Powered Smart Hub?"  
  
  
def main():  
    """  
    Main function to set up an AI agent with file search capabilities, interact with it, and manage resources.  
    """  
    print("Starting the File Search AI agent setup process.")  
  
    # Step 0: Validate environment variables  
    print("Step 0: Validating environment variables...")  
    project_conn_str = os.environ.get(PROJECT_CONNECTION_STRING_ENV)  
    if not project_conn_str:  
        raise EnvironmentError(  
            f"Environment variable '{PROJECT_CONNECTION_STRING_ENV}' is not set."  
        )  
    print("Environment variables validated successfully.")  
  
    try:  
        # Step 1: Initialize the AI Project Client with default credentials  
        print("Step 1: Initializing Azure AI Project Client...")  
        credential = DefaultAzureCredential()  
        project_client = AIProjectClient.from_connection_string(  
            credential=credential,  
            conn_str=project_conn_str  
        )  
        print("Azure AI Project Client initialized.")  
  
        with project_client:  
            # Step 2: Upload Files and Add to Vector Store  
            print("Step 2: Uploading file to the project...")  
            uploaded_file = project_client.agents.upload_file_and_poll(  
                file_path=FILE_PATH,  
                purpose=FilePurpose.AGENTS  
            )  
            print(f"Uploaded file, file ID: {uploaded_file.id}")  
  
            print("Step 3: Creating vector store...")  
            vector_store = project_client.agents.create_vector_store_and_poll(  
                file_ids=[uploaded_file.id],  
                name=VECTOR_STORE_NAME  
            )  
            print(f"Created vector store, vector store ID: {vector_store.id}")  
  
            # Step 4: Create an Agent and Enable File Search  
            print("Step 4: Setting up file search tool...")  
            file_search_tool = FileSearchTool(vector_store_ids=[vector_store.id])  
  
            print("Step 5: Creating agent with file search capabilities...")  
            agent = project_client.agents.create_agent(  
                model=AGENT_MODEL,  
                name=AGENT_NAME,  
                instructions=AGENT_INSTRUCTIONS,  
                tools=file_search_tool.definitions,  
                tool_resources=file_search_tool.resources,  
            )  
            print(f"Created agent, agent ID: {agent.id}")  
  
            # Step 6: Create a Thread and Add a User Message  
            print("Step 6: Creating conversation thread...")  
            thread = project_client.agents.create_thread()  
            print(f"Created thread, thread ID: {thread.id}")  
  
            print("Step 7: Adding user message to the thread...")  
            user_message = project_client.agents.create_message(  
                thread_id=thread.id,  
                role="user",  
                content=USER_MESSAGE_CONTENT  
            )  
            print(f"Created user message, message ID: {user_message.id}")  
  
            # Step 8: Run the Agent  
            print("Step 8: Running the agent...")  
            run = project_client.agents.create_and_process_run(  
                thread_id=thread.id,  
                assistant_id=agent.id  
            )  
            print(f"Run finished with status: {run.status}")  
  
            if run.status == "failed":  
                print(f"Run failed: {run.last_error}")  
            else:  
                # Step 9: Retrieve and Print the Agent's Response  
                print("Step 9: Retrieving agent's response...")  
                messages = project_client.agents.list_messages(thread_id=thread.id)  
                last_msg = messages.get_last_text_message_by_role("assistant")  
                if last_msg:  
                    print(f"Agent Response: {last_msg.text.value}")  
                else:  
                    print("No response from the agent.")  
  
            # Step 10: Clean Up Resources  
            print("Step 10: Cleaning up resources...")  
            project_client.agents.delete_vector_store(vector_store.id)  
            print(f"Deleted vector store (ID: {vector_store.id})")  
  
            project_client.agents.delete_agent(agent.id)  
            print(f"Deleted agent (ID: {agent.id})")  
  
    except Exception as e:  
        print(f"An error occurred: {e}")  
  
    print("File Search AI agent setup process completed.")  
  
  
if __name__ == "__main__":  
    main()  
```  
   
## Step 3: Run Your Code  
   
1. **Execute the Python Script:**  
  
   Open your terminal or command prompt, navigate to the directory where your Python file is saved, and run the script:  
  
   ```bash  
   python your_script_name.py  
   ```  
  
   Replace `your_script_name.py` with the actual filename of your script.  
   
2. **Observe the Output:**  
  
   - As the script executes, it will upload a file, create a vector store, set up an agent with file search capabilities, establish a conversation thread, and send a user message.  
   - The agent will process the message based on the content of the uploaded document and respond accordingly.  
   - You should see output similar to:  
  
    ```  
    Starting the File Search AI agent setup process.
    Step 0: Validating environment variables...
    Environment variables validated successfully.
    Step 1: Initializing Azure AI Project Client...
    Azure AI Project Client initialized.
    Step 2: Uploading file to the project...
    Uploaded file, file ID: assistant-PWuRtEtcEUM8CyPkcnMnkdxm
    Step 3: Creating vector store...
    Created vector store, vector store ID: vs_PMLSPmQGRlEuKijbJ5eryZJ3
    Step 4: Setting up file search tool...
    Step 5: Creating agent with file search capabilities...
    Created agent, agent ID: asst_av6gaMrny2rufU3lP8QpPjTl
    Step 6: Creating conversation thread...
    Created thread, thread ID: thread_FaRMQdNAqxQ6mRG6G10Ra1vN
    Step 7: Adding user message to the thread...
    Created user message, message ID: msg_mqp18n7qtHh8l2L526RYSVAK
    Step 8: Running the agent...
    Run finished with status: RunStatus.COMPLETED
    Step 9: Retrieving agent's response...
    Agent Response: The AI-Powered Smart Hub is ...
    Step 10: Cleaning up resources...
    Deleted vector store (ID: vs_PMLSPmQGRlEuKijbJ5eryZJ3)
    Deleted agent (ID: asst_av6gaMrny2rufU3lP8QpPjTl)
    File Search AI agent setup process completed.
    ```  
  
   **Note:** The agent's response will vary based on the content of your uploaded document.  
   
## Understanding the Code  
   
- **File Upload and Vector Store Creation:**  
    
  The script uploads a specified document (`product_catalog.pdf`) and creates a vector store. The vector store enables the agent to perform semantic searches on the uploaded content, allowing it to retrieve relevant information when responding to queries.  
   
- **Agent Creation with File Search Capabilities:**  
    
  An agent is created with instructions to base its responses solely on the information from the provided documents. The `FileSearchTool` is integrated, enabling the agent to utilize the vector store for fetching information.  
   
- **Thread and Message:**  
    
  A conversation thread is established where a user message is sent. In this example, the query is about the "AI-Powered Smart Hub."  
   
- **Agent Run:**  
    
  The agent processes the thread's messages, utilizing the file search tool to fetch information from the uploaded document and generate an appropriate response.  
   
- **Cleanup:**  
    
  After the interaction, both the vector store and the agent are deleted to free up resources and ensure a clean environment for future operations.  
   
## Next Steps  
   
Congratulations! You've successfully integrated file search capabilities into your Azure AI agent. This enhancement allows your agent to leverage document-based information for more informed responses.  
   
Proceed to the next tutorial in the series to learn how to enhance your agent with Bing Search capabilities: [Tutorial 03: Grounding Your Agent with Bing Search](./03-bing-search.md). 