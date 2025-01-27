# Tutorial 02: Empowering Your Agent: Integrating File Search  
   
Welcome to the second tutorial in the Azure AI Agent Service series! In this tutorial, we will guide you through the process of integrating file search capabilities into your AI agent. This enhancement will allow your agent to respond to user queries based on the information contained in uploaded documents.  
   
## Prerequisites  
   
Before starting this tutorial, ensure you have completed the following prerequisites:  
   
- An active Azure subscription.  
- Python 3.8 or later installed.  
- Azure CLI and machine learning extension installed and updated.  
- Necessary roles assigned (Azure AI Developer and Cognitive Services OpenAI User).  
- Required Python packages installed:  
   
```bash  
pip install azure-ai-projects azure-identity  
```  
   
## Step 1: Set Up Your Environment  
   
1. **Create a Connection String:**  
   First, create a connection string using your Azure AI project details. The format is:  
  
   ```  
   <HostName>;<AzureSubscriptionId>;<ResourceGroup>;<ProjectName>  
   ```  
  
   Example:  
  
   ```  
   eastus.api.azureml.ms;12345678-abcd-1234-9fc6-62780b3d3e05;my-resource-group;my-project-name  
   ```  
   
2. **Set the Connection String as an Environment Variable:**  
   Export your connection string to an environment variable named `PROJECT_CONNECTION_STRING`.  
  
   - For **PowerShell**:  
     ```powershell  
     $env:PROJECT_CONNECTION_STRING="your-connection-string-here"  
     ```  
   - For **Bash**:  
     ```bash  
     export PROJECT_CONNECTION_STRING="your-connection-string-here"  
     ```  
   - For **Windows Command Prompt**:  
     ```cmd  
     set PROJECT_CONNECTION_STRING="your-connection-string-here"  
     ```  
   
## Step 2: Upload Files and Create a Vector Store  
   
3. **Write the Python Code:**  
   Open your preferred text editor and create a new Python file. Copy and paste the following code into the file:  
  
   ```python  
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
   ```  
   
## Step 3: Create an Agent with File Search Capabilities  
   
4. **Extend the Code to Create the Agent:**  
  
   Add the following code below your previous code to create an agent that utilizes the file search tool:  
  
   ```python  
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
   ```  
   
## Step 4: Create a Thread and Run the Agent  
   
5. **Continue with the Code:**  
  
   Now, add the following code to create a thread, add a user message, and run the agent:  
  
   ```python  
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
   ```  
   
## Step 5: Clean Up Resources  
   
6. **Add Cleanup Code:**  
  
   Finally, add the following lines at the end of your script to clean up resources:  
  
   ```python  
   # Clean up resources  
   project_client.agents.delete_vector_store(vector_store.id)  
   print("Deleted vector store")  
  
   project_client.agents.delete_agent(agent.id)  
   print("Deleted agent")  
   ```  
   
## Step 6: Run Your Code  
   
7. **Execute the Python Script:**  
  
   Open your terminal or command prompt, navigate to the directory where your Python file is saved, and run the script:  
  
   ```bash  
   python your_script_name.py  
   ```  
  
   Replace `your_script_name.py` with the actual filename of your script.  
   
8. **Observe the Output:**  
   - As the script executes, it will upload a file, create a vector store, set up a conversation thread, and send a user message.  
   - The agent will process the message and respond based on the content of the uploaded document.  
   - You should see output similar to:  
  
   ```  
   Uploaded file, file ID: file_123456  
   Created vector store, vector store ID: vectorstore_789012  
   Created agent, agent ID: asst_345678  
   Created thread, thread ID: thread_901234  
   Created user message, message ID: msg_567890  
   Run finished with status: RunStatus.COMPLETED  
   Agent Response: Here are the details about the AI-Powered Smart Hub...  
   Deleted vector store  
   Deleted agent  
   ```  
   
## Understanding the Code  
   
- **File Upload and Vector Store Creation:** The code uploads a document and creates a vector store, which allows the agent to perform searches on the uploaded content.  
- **Agent Creation:** The agent is created with specific instructions to base its responses solely on the provided documents.  
- **Thread and Message:** A conversation thread is established where the user can send messages. In this tutorial, we send a query about a product.  
- **Agent Run:** The agent processes the thread's messages and provides a response based on the document's content.  
- **Cleanup:** After the interaction, both the vector store and the agent are deleted to free up resources.  
   
## Next Steps  
   
Congratulations! You've successfully integrated file search capabilities into your Azure AI agent. This enhancement allows your agent to leverage document-based information for more informed responses.   
  
Proceed to the next tutorial in the series to learn how to enhance your agent with Bing Search capabilities: [Tutorial 03: Augmenting Intelligence: Using Bing Search with Your Agent](03-bing-search.md).