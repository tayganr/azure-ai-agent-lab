# Tutorial 03: Grounding Your Agent with Bing Search

[< Previous Module](./02-file-search.md) - [Home](../README.md) - [Next Module >](./04-code-interpreter.md)
  
Welcome to the third tutorial in the Azure AI Agent Service series! In this tutorial, we will enhance our AI agent by integrating the Bing Search tool. This integration will enable your agent to retrieve real-time information from the web, providing more accurate and up-to-date responses to user queries.  
   
## Step 1: Prerequisites  
  
Before starting this tutorial, ensure you have completed the setup as described in the [Technical Prerequisites](../README.md#-technical-prerequisites) section of the README. Key steps include:
  
- **Python Environment**: Python 3.8 or later should be installed and configured.
- **Azure CLI**: Install Azure CLI and log in to your subscription.
- **Repository Setup**: Clone the repository and set up a Python virtual environment.  
- **Install Dependencies**: Use `pip` to install the required packages from `requirements.txt`.
- **Environment Variables**: Ensure the `PROJECT_CONNECTION_STRING` and `BING_CONNECTION_NAME` are set.  
  
### Setting Environment Variables  
  
To configure your environment correctly, set the following variables:  
  
1. **PROJECT_CONNECTION_STRING**: Follow the instructions in the README to set this variable.  
  
2. **BING_CONNECTION_NAME**: Export this variable with the name of your Bing Search connection:  
  
   - **For Bash (macOS/Linux)**:  
     ```bash  
     export BING_CONNECTION_NAME="your_connection_name_here"  
     ```  
   - **For Windows Command Prompt**:  
     ```cmd  
     set BING_CONNECTION_NAME="your_connection_name_here"  
     ```  
   - **For PowerShell**:  
     ```powershell  
     $env:BING_CONNECTION_NAME="your_connection_name_here"  
     ```  
  
Replace `"your_connection_name_here"` with the actual name used for your Bing Search connection.  
  
### Grounding with Bing Search Setup  
  
To use the Grounding with Bing Search resource, you must follow these steps:  
   
1. **Provision the Grounding with Bing Search Resource:**    
   - Create a new Grounding with Bing Search resource in the [Azure portal](https://portal.azure.com/#create/Microsoft.BingGroundingSearch). Ensure that this resource is provisioned within the same resource group as your Azure AI Agent and other related resources.  
   
2. **Register Bing Search as a Resource Provider:**    
   - You need to manually register Bing Search as an Azure resource provider. This requires permission to perform the `/register/action` operation, which is included in the Contributor and Owner roles. Use the following command in Azure CLI:  
   ```bash  
   az provider register --namespace 'Microsoft.Bing'  
   ```  
   
3. **Set Up Connection in Azure AI Foundry:**    
   - After creating the **Grounding with Bing Search** resource, navigate to the **Azure AI Foundry portal**.
   - Select your **AI Project** from the available projects.
   - In the left sidebar, click on **Management Center**.
   - Under the Management Center, locate and click on **Connected Resources**.
   - Click on **+ New Connection** to create a new connection.
   - Choose the **API Key** option under other resource types and enter the following information:
     - **Endpoint:** `https://api.bing.microsoft.com/`  
     - **Key:** `YOUR_API_KEY` (the key you copied from the Azure portal)  
     - **Connection name:** `YOUR_CONNECTION_NAME` (this name will be used in the sample code below)  
     - **Access:** Choose whether the connection is for this project only or shared with all projects.  
   
4. **Use Supported Models:**    
   - Note that Grounding with Bing Search only works with the following Azure OpenAI models: `gpt-3.5-turbo-0125`, `gpt-4-0125-preview`, `gpt-4-turbo-2024-04-09`, and `gpt-4o-0513`.  
   
## Step 2: Write the Python Code    
  
5. **Create a New Python File:**    
   Open your preferred text editor and create a new Python file. Copy and paste the following code into the file:  
   
```python  
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
```  
   
## Step 3: Run Your Code    
  
6. **Execute the Python Script:**    
   Open your terminal or command prompt, navigate to the directory where your Python file is saved, and run the script:  
   
```bash  
python your_script_name.py  
```  
   
Replace `your_script_name.py` with the actual filename of your script.  
   
7. **Observe the Output:**    
   - As the script executes, it will create an agent configured with the Bing Search tool, set up a conversation thread, and send a user message.  
   - The agent will process the message and respond based on real-time data from Bing.  
   - You should see output similar to:  
   
```  
Bing connection ID: /subscripti...
Created agent, ID: asst_J95x2F7i2GkYEOeMr5gqNvko
Created thread, ID: thread_4kT79eR9Tppfgm4lFRmzRLfw
Created user message, ID: msg_RBXd2NbdlT1GMp4vDB0bSvkd
Run finished with status: RunStatus.COMPLETED
Last run step detail: [{'id': 'step_...
Agent Response: The current Prime Minister of the United Kingdom is Keir Starmer. He has been serving in this position since July 5, 2024【3†source】.
Deleted agent
```  
   
## Understanding the Code    
  
- **Bing Grounding Tool Initialization:** The code initializes the Bing Grounding tool using the connection ID from your Azure resources, allowing the agent to perform web searches.  
- **Agent Creation:** The agent is created with instructions to assist users. The Bing tool is included in the agent's capabilities.  
- **Thread and Message:** A conversation thread is established where the user can send messages. In this case, we ask a question about the current Prime Minister.  
- **Agent Run:** The agent processes the thread's messages, retrieves information from Bing, and provides a response.  
- **Cleanup:** After the interaction, the agent is deleted to free up resources.  
   
## Next Steps    
  
Congratulations! You've successfully integrated Bing Search capabilities into your Azure AI agent. This enhancement allows your agent to provide up-to-date responses based on real-world information.  
   
Proceed to the next tutorial in the series to learn how to enhance your agent with multiple tools: [Tutorial 04: Implementing the Code Interpreter Tool](04-code-interpreter.md).