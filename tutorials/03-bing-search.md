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
  
# === Environment Variables ===  
PROJECT_CONNECTION_STRING_ENV = "PROJECT_CONNECTION_STRING"  
BING_CONNECTION_NAME_ENV = "BING_CONNECTION_NAME"  
  
# === Agent Configuration ===  
AGENT_NAME = "bing-search-agent"  
AGENT_MODEL = "gpt-4o"  # Ensure this model is supported  
AGENT_INSTRUCTIONS = "You are a helpful assistant."  
  
# === Operational Constants ===  
USER_MESSAGE_CONTENT = "Who is the current Prime Minister of the United Kingdom?"  
  
  
def main():  
    """  
    Main function to set up an AI agent with Bing Grounding tool, interact with it, and manage resources.  
    """  
    print("Starting the Bing Grounding AI agent setup process.")  
  
    # Step 0: Validate environment variables  
    print("Step 0: Validating environment variables...")  
    project_conn_str = os.environ.get(PROJECT_CONNECTION_STRING_ENV)  
    bing_connection_name = os.environ.get(BING_CONNECTION_NAME_ENV)  
    missing_vars = []  
    if not project_conn_str:  
        missing_vars.append(PROJECT_CONNECTION_STRING_ENV)  
    if not bing_connection_name:  
        missing_vars.append(BING_CONNECTION_NAME_ENV)  
    if missing_vars:  
        raise EnvironmentError(  
            f"Missing environment variable(s): {', '.join(missing_vars)}"  
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
            # Step 2: Enable the Grounding with Bing search tool  
            print("Step 2: Enabling Bing Grounding Tool...")  
            bing_connection = project_client.connections.get(  
                connection_name=bing_connection_name  
            )  
            bing_conn_id = bing_connection.id  
            print(f"Bing connection ID: {bing_conn_id}")  
  
            # Initialize the Bing Grounding tool with the connection ID  
            bing_tool = BingGroundingTool(connection_id=bing_conn_id)  
  
            # Step 3: Create an agent with the Bing Grounding tool  
            print("Step 3: Creating agent with Bing Grounding Tool...")  
            agent = project_client.agents.create_agent(  
                model=AGENT_MODEL,  
                name=AGENT_NAME,  
                instructions=AGENT_INSTRUCTIONS,  
                tools=bing_tool.definitions,  
                headers={"x-ms-enable-preview": "true"}  
            )  
            print(f"Created agent, ID: {agent.id}")  
  
            # Step 4: Create a conversation thread  
            print("Step 4: Creating conversation thread...")  
            thread = project_client.agents.create_thread()  
            print(f"Created thread, ID: {thread.id}")  
  
            # Step 5: Add a user message to the thread  
            print("Step 5: Adding user message to the thread...")  
            user_message = project_client.agents.create_message(  
                thread_id=thread.id,  
                role="user",  
                content=USER_MESSAGE_CONTENT  
            )  
            print(f"Created user message, message ID: {user_message.id}")  
  
            # Step 6: Run the agent  
            print("Step 6: Running the agent...")  
            run = project_client.agents.create_and_process_run(  
                thread_id=thread.id,  
                assistant_id=agent.id  
            )  
            print(f"Run finished with status: {run.status}")  
  
            if run.status == "failed":  
                print(f"Run failed: {run.last_error}")  
            else:  
                # Step 7: Retrieve run step details to get Bing Search query link  
                print("Step 7: Retrieving run step details...")  
                run_steps = project_client.agents.list_run_steps(  
                    run_id=run.id,  
                    thread_id=thread.id  
                )  
                run_steps_data = run_steps.get('data', [])  
                if run_steps_data:  
                    last_run_step = run_steps_data[-1]  
                    print(f"Last run step detail: {last_run_step}")  
                else:  
                    print("No run step details found.")  
  
                # Step 8: Retrieve and print the agent's response  
                print("Step 8: Retrieving agent's response...")  
                messages = project_client.agents.list_messages(thread_id=thread.id)  
                last_msg = messages.get_last_text_message_by_role("assistant")  
  
                if last_msg:  
                    print(f"Agent Response: {last_msg.text.value}")  
                else:  
                    print("No response from the agent.")  
  
            # Step 9: Clean up resources  
            print("Step 9: Cleaning up resources...")  
            project_client.agents.delete_agent(agent.id)  
            print(f"Deleted agent (ID: {agent.id})")  
  
    except Exception as e:  
        print(f"An error occurred: {e}")  
  
    print("Bing Grounding AI agent setup process completed.")  
  
  
if __name__ == "__main__":  
    main()  
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
Step 1: Initializing Azure AI Project Client...
Azure AI Project Client initialized.
Step 2: Enabling Bing Grounding Tool...
Step 3: Creating agent with Bing Grounding Tool...
Created agent, ID: asst_RQFUpY06fgfXeqj2R6RXE5wY
Step 4: Creating conversation thread...
Created thread, ID: thread_TCEor9xbjx1LY6Bnsn3MtsjU
Step 5: Adding user message to the thread...
Created user message, message ID: msg_NNhbMsPyEJ6x89MVlqtS8g3l
Step 6: Running the agent...
Run finished with status: RunStatus.COMPLETED
Step 7: Retrieving run step details...
Step 8: Retrieving agent's response...
Agent Response: The current Prime Minister of the ...
Step 9: Cleaning up resources...
Deleted agent (ID: asst_RQFUpY06fgfXeqj2R6RXE5wY)
Bing Grounding AI agent setup process completed.
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