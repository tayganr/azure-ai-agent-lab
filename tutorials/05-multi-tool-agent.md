# Tutorial 05: Creating a Multi-Tool Agent  
  
[< Previous Module](./04-code-interpreter.md) - [Home](../README.md)
  
Welcome to the fifth tutorial in the Azure AI Agent Service series! In this comprehensive tutorial, you will learn how to create a **Multi-Tool Agent** that integrates multiple capabilities, including **File Search**, **Code Interpretation**, and **Bing Search**. This integration allows your agent to handle a wide range of user queries by leveraging different tools seamlessly.  
  
## Step 1: Prerequisites  
  
Before starting this tutorial, ensure you have completed the setup as described in the [Technical Prerequisites](../README.md#-technical-prerequisites) section of the README. Key steps include:  
  
- **Python Environment**: Python 3.8 or later should be installed and configured.  
- **Azure CLI**: Install Azure CLI and log in to your subscription.  
- **Repository Setup**: Clone the repository and set up a Python virtual environment.  
- **Install Dependencies**: Use `pip` to install the required packages from `requirements.txt`.  
- **Environment Variables**: Ensure the `PROJECT_CONNECTION_STRING` and `BING_CONNECTION_NAME` are set.  
  
### Setting Environment Variables  
  
Ensure the following environment variables are set in your system:  
  
1. **PROJECT_CONNECTION_STRING**: This variable should be set as described in the [Technical Prerequisites](../README.md#-technical-prerequisites).  
     
   - **For Bash (macOS/Linux)**:  
     ```bash  
     export PROJECT_CONNECTION_STRING="your_project_connection_string_here"  
     ```  
     
   - **For Windows Command Prompt**:  
     ```cmd  
     set PROJECT_CONNECTION_STRING="your_project_connection_string_here"  
     ```  
     
   - **For PowerShell**:  
     ```powershell  
     $env:PROJECT_CONNECTION_STRING="your_project_connection_string_here"  
     ```  
  
2. **BING_CONNECTION_NAME**: Set this variable with the name of your Bing Search connection.  
     
   - **For Bash (macOS/Linux)**:  
     ```bash  
     export BING_CONNECTION_NAME="your_bing_connection_name_here"  
     ```  
     
   - **For Windows Command Prompt**:  
     ```cmd  
     set BING_CONNECTION_NAME="your_bing_connection_name_here"  
     ```  
     
   - **For PowerShell**:  
     ```powershell  
     $env:BING_CONNECTION_NAME="your_bing_connection_name_here"  
     ```  
  
## Step 2: Write and Configure the Python Code  
  
Open your preferred text editor and create a new Python file named `multi_tool_agent.py`. Copy and paste the following code into the file:  
  
```python  
import os  
  
from azure.ai.projects import AIProjectClient  
from azure.ai.projects.models import (  
    BingGroundingTool,  
    CodeInterpreterTool,  
    FilePurpose,  
    FileSearchTool,  
    ToolResources  
)  
from azure.identity import DefaultAzureCredential  
  
# === Environment Variables ===  
PROJECT_CONNECTION_STRING_ENV = "PROJECT_CONNECTION_STRING"  
BING_CONNECTION_NAME_ENV = "BING_CONNECTION_NAME"  
  
# === Agent Configuration ===  
AGENT_NAME = "multi-tool-agent"  
AGENT_MODEL = "gpt-4o"  # Ensure this model is supported  
AGENT_INSTRUCTIONS = (  
    "You are a helpful assistant with access to file search, code interpretation, "  
    "and Bing search capabilities."  
)  
  
# === Operational Constants ===  
FILE_SEARCH_FILE_PATH = './documents/product_catalog.pdf'        # Path for file search  
CODE_INTERPRETER_FILE_PATH = "./documents/quarterly_results.csv"  # Path for code interpretation  
VECTOR_STORE_NAME = "my_vectorstore"  
USER_MESSAGES = [  
    {  
        "role": "user",  
        "content": "Who is the current Prime Minister of the United Kingdom?"  
    },  
    {  
        "role": "user",  
        "content": "Can you provide details about the AI-Powered Smart Hub?"  
    },  
    {  
        "role": "user",  
        "content": (  
            "Could you please create a bar chart in the TRANSPORTATION sector for the "  
            "operating profit from the uploaded CSV file and provide the file to me?"  
        )  
    }  
]  
TARGET_DIR = './documents'  # Directory to save generated files  
  
  
def main():  
    """  
    Main function to set up an agent with multiple tools, interact with it, and manage resources.  
    """  
    print("Starting the Multi-Tool AI agent setup process.")  
  
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
        # Step 1: Initialize the AI Project Client  
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
  
            bing_tool = BingGroundingTool(connection_id=bing_conn_id)  
  
            # Step 3: Upload files and set up tools  
            print("Step 3: Uploading files and setting up tools...")  
  
            # Step 3.1: Upload file for file search  
            print(f"Step 3.1: Uploading file for file search '{FILE_SEARCH_FILE_PATH}'...")  
            file_search_file = project_client.agents.upload_file_and_poll(  
                file_path=FILE_SEARCH_FILE_PATH,  
                purpose=FilePurpose.AGENTS  
            )  
            print(f"Uploaded file for file search, file ID: {file_search_file.id}")  
  
            # Step 3.2: Create Vector Store  
            print(f"Step 3.2: Creating vector store '{VECTOR_STORE_NAME}'...")  
            vector_store = project_client.agents.create_vector_store_and_poll(  
                file_ids=[file_search_file.id],  
                name=VECTOR_STORE_NAME  
            )  
            print(f"Created vector store, vector store ID: {vector_store.id}")  
  
            # Step 3.3: Upload file for code interpretation  
            print(f"Step 3.3: Uploading file for code interpretation '{CODE_INTERPRETER_FILE_PATH}'...")  
            code_interpreter_file = project_client.agents.upload_file_and_poll(  
                file_path=CODE_INTERPRETER_FILE_PATH,  
                purpose=FilePurpose.AGENTS  
            )  
            print(f"Uploaded file for code interpretation, file ID: {code_interpreter_file.id}")  
  
            # Step 3.4: Initialize File Search and Code Interpreter tools  
            print("Step 3.4: Initializing File Search and Code Interpreter tools...")  
            file_search_tool = FileSearchTool(vector_store_ids=[vector_store.id])  
            code_interpreter_tool = CodeInterpreterTool(file_ids=[code_interpreter_file.id])  
  
            # Step 4: Combine tools and resources  
            print("Step 4: Combining tools and resources...")  
            combined_tool_resources = ToolResources(  
                file_search=file_search_tool.resources['file_search'],  
                code_interpreter=code_interpreter_tool.resources['code_interpreter']  
            )  
  
            # Step 5: Create an agent with all tools including Bing  
            print("Step 5: Creating agent with all tools...")  
            agent = project_client.agents.create_agent(  
                model=AGENT_MODEL,  
                name=AGENT_NAME,  
                instructions=AGENT_INSTRUCTIONS,  
                tools=(  
                    file_search_tool.definitions +  
                    code_interpreter_tool.definitions +  
                    bing_tool.definitions  
                ),  
                tool_resources=combined_tool_resources,  
                headers={"x-ms-enable-preview": "true"}  
            )  
            print(f"Created agent, ID: {agent.id}")  
  
            # Step 6: Create a conversation thread and add user messages  
            print("Step 6: Creating conversation thread and adding user messages...")  
            thread = project_client.agents.create_thread()  
            print(f"Created thread, ID: {thread.id}")  
  
            for idx, user_msg in enumerate(USER_MESSAGES, start=1):  
                # Step 6.{idx}: Adding user message {idx}  
                print(f"Step 6.{idx}: Adding user message {idx}: {user_msg['content']}")  
                message = project_client.agents.create_message(  
                    thread_id=thread.id,  
                    role=user_msg["role"],  
                    content=user_msg["content"]  
                )  
                print(f"Created user message {idx}, ID: {message.id}")  
  
                # Step 7.{idx}: Run the agent for each user message  
                print(f"Step 7.{idx}: Running the agent for message {idx}...")  
                run = project_client.agents.create_and_process_run(  
                    thread_id=thread.id,  
                    assistant_id=agent.id  
                )  
                print(f"Run {idx} finished with status: {run.status}")  
  
                if run.status == "failed":  
                    print(f"Run {idx} failed: {run.last_error}")  
                    continue  
  
                # Step 8.{idx}: Retrieve and print the agent's response  
                print(f"Step 8.{idx}: Retrieving agent's response for message {idx}...")  
                messages = project_client.agents.list_messages(thread_id=thread.id)  
  
                if user_msg["content"].startswith("Could you please create a bar chart"):  
                    # Assuming this is for code interpreter output  
                    last_msg = messages.get_last_message_by_role("assistant")  
                    if last_msg:  
                        # Print text response  
                        if hasattr(last_msg, 'text_messages') and last_msg.text_messages:  
                            print(f"Agent Response to Code Interpretation: {last_msg.text_messages[-1].text.value}")  
  
                        # Save generated file  
                        if hasattr(last_msg, 'file_path_annotations'):  
                            for annotation in last_msg.file_path_annotations:  
                                file_info = annotation.file_path  
                                file_id = file_info.get('file_id')  
                                # Explicitly set file_name to 'chart.png' for this context  
                                file_name = 'chart.png'  
                                if file_id:  
                                    print(f"Step 8.{idx}: Saving generated file '{file_name}'...")  
                                    project_client.agents.save_file(  
                                        file_id=file_id,  
                                        file_name=file_name,  
                                        target_dir=TARGET_DIR  
                                    )  
                                    print(f"Saved file: {file_name} in '{TARGET_DIR}'")  
                else:  
                    last_msg = messages.get_last_text_message_by_role("assistant")  
                    if last_msg:  
                        print(f"Agent Response: {last_msg.text.value}")  
  
            # Step 9: Clean up resources  
            print("Step 9: Cleaning up resources...")  
            print(f"Deleting vector store (ID: {vector_store.id})...")  
            project_client.agents.delete_vector_store(vector_store.id)  
            print(f"Deleted vector store, ID: {vector_store.id}")  
  
            print(f"Deleting code interpreter file (ID: {code_interpreter_file.id})...")  
            project_client.agents.delete_file(code_interpreter_file.id)  
            print(f"Deleted code interpreter file, ID: {code_interpreter_file.id}")  
  
            print(f"Deleting agent (ID: {agent.id})...")  
            project_client.agents.delete_agent(agent.id)  
            print(f"Deleted agent, ID: {agent.id}")  
  
    except Exception as e:  
        print(f"An error occurred: {e}")  
  
    print("Multi-Tool AI agent setup process completed.")  
  
  
if __name__ == "__main__":  
    main()  
```  
  
### Explanation of the Code  
  
- **Imports**: The script imports necessary modules from `azure.ai.projects` and `azure.identity` to interact with Azure AI services.  
    
- **Environment Variables**: It defines environment variables required for connecting to the Azure project and Bing Search service.  
    
- **Agent Configuration**: Specifies the agent's name, model, and instructions. The instructions inform the agent of its capabilities.  
    
- **Operational Constants**: Defines file paths for file search and code interpretation, the name of the vector store, user messages to interact with the agent, and the target directory for saving generated files.  
  
- **Main Function**:   
  - **Step 0**: Validates that all necessary environment variables are set.  
  - **Step 1**: Initializes the `AIProjectClient` using the provided connection string.  
  - **Step 2**: Enables the Bing Grounding Tool by retrieving the connection ID.  
  - **Step 3**: Uploads files required for file search and code interpretation and sets up the corresponding tools.  
    - **Step 3.1**: Uploads a PDF for file search.  
    - **Step 3.2**: Creates a vector store using the uploaded file.  
    - **Step 3.3**: Uploads a CSV file for code interpretation.  
    - **Step 3.4**: Initializes both File Search and Code Interpreter tools.  
  - **Step 4**: Combines the tools' resources.  
  - **Step 5**: Creates the agent with all integrated tools, including Bing Search.  
  - **Step 6**: Creates a conversation thread and iterates through predefined user messages, running the agent for each message and handling responses.  
    - **Steps 6.{idx}** to **Step 8.{idx}**: Handles each user message, runs the agent, and processes the response accordingly.  
  - **Step 9**: Cleans up all resources by deleting the vector store, uploaded files, and the agent itself.  
  
## Step 3: Run Your Code  
  
1. **Execute the Python Script:**  
  
   Open your terminal or command prompt, navigate to the directory where your `multi_tool_agent.py` file is saved, and run the script:  
  
   ```bash  
   python multi_tool_agent.py  
   ```  
  
2. **Observe the Output:**  
  
   As the script executes, it will perform the following actions:  
  
   - Upload necessary files for file search and code interpretation.  
   - Create and configure the vector store.  
   - Initialize and combine multiple tools (File Search, Code Interpreter, Bing Grounding).  
   - Create a multi-tool agent.  
   - Establish a conversation thread and process multiple user messages.  
   - Retrieve and handle the agent's responses, including saving generated files.  
   - Clean up all resources after execution.  
  
   **Sample Output:**  
  
    ```plaintext  
    Starting the Multi-Tool AI agent setup process.
    Step 0: Validating environment variables...
    Environment variables validated successfully.
    Step 1: Initializing Azure AI Project Client...
    Azure AI Project Client initialized.
    Step 2: Enabling Bing Grounding Tool...
    Step 3: Uploading files and setting up tools...
    Step 3.1: Uploading file for file search './documents/product_catalog.pdf'...
    Uploaded file for file search, file ID: assistant-xU3cImX2A2ehuS34JG0gsICQ
    Step 3.2: Creating vector store 'my_vectorstore'...
    Created vector store, vector store ID: vs_1AdwFrBYCRMPExDMrx05rwWP
    Step 3.3: Uploading file for code interpretation './documents/quarterly_results.csv'...
    Uploaded file for code interpretation, file ID: assistant-bY7MV1y9ZHFsIv2N6pEqwYcL
    Step 3.4: Initializing File Search and Code Interpreter tools...
    Step 4: Combining tools and resources...
    Step 5: Creating agent with all tools...
    Created agent, ID: asst_4GTHAqZbF8ADcIOz0CJuS0Es
    Step 6: Creating conversation thread and adding user messages...
    Created thread, ID: thread_jGvHprvebgQQARewoNuj0F0b
    Step 6.1: Adding user message 1: Who is the current Prime...
    Created user message 1, ID: msg_7R3nF1QCVPuc4EW7vdJTzfz9
    Step 7.1: Running the agent for message 1...
    Run 1 finished with status: RunStatus.COMPLETED
    Step 8.1: Retrieving agent's response for message 1...
    Agent Response: The current Prime Minister of the ...
    Step 6.2: Adding user message 2: Can you provide details about the AI-Pow...
    Created user message 2, ID: msg_ww76reEyNTGMxywANZNjzm0H
    Step 7.2: Running the agent for message 2...
    Run 2 finished with status: RunStatus.COMPLETED
    Step 8.2: Retrieving agent's response for message 2...
    Agent Response: The AI-Powered Smart Hub is a ...
    Step 6.3: Adding user message 3: Could you please create a bar chart ...
    Created user message 3, ID: msg_GC0uWTMaKml5bzfVy8eV0Sex
    Step 7.3: Running the agent for message 3...
    Run 3 finished with status: RunStatus.COMPLETED
    Step 8.3: Retrieving agent's response for message 3...
    Agent Response to Code Interpretation: I have created a bar chart showing...
    Step 8.3: Saving generated file 'chart.png'...
    Saved file: chart.png in './documents'
    Step 9: Cleaning up resources...
    Deleting vector store (ID: vs_1AdwFrBYCRMPExDMrx05rwWP)...
    Deleted vector store, ID: vs_1AdwFrBYCRMPExDMrx05rwWP
    Deleting code interpreter file (ID: assistant-bY7MV1y9ZHFsIv2N6pEqwYcL)...
    Deleted code interpreter file, ID: assistant-bY7MV1y9ZHFsIv2N6pEqwYcL
    Deleting agent (ID: asst_4GTHAqZbF8ADcIOz0CJuS0Es)...
    Deleted agent, ID: asst_4GTHAqZbF8ADcIOz0CJuS0Es
    Multi-Tool AI agent setup process completed.
    ```  
  
   **Note:** The agent's responses and file IDs in the output are placeholders and will vary based on your actual implementation and data.  
  
## Understanding the Code  
  
- **Agent Creation with Multiple Tools:**  
    
  The agent is configured to utilize three distinct tools:  
    
  - **File Search Tool**: Enables the agent to search and retrieve information from uploaded documents.  
  - **Code Interpreter Tool**: Allows the agent to perform computations and generate visualizations based on data files.  
  - **Bing Grounding Tool**: Integrates Bing Search capabilities to fetch real-time web information.  
  
- **Uploading Files:**  
    
  The script uploads two files:  
    
  - A PDF (`product_catalog.pdf`) for file search functionality.  
  - A CSV (`quarterly_results.csv`) for code interpretation and visualization tasks.  
  
- **Creating Vector Store:**  
    
  A vector store (`my_vectorstore`) is created using the uploaded PDF to facilitate semantic searches within the document.  
  
- **Combining Tools and Resources:**  
    
  The script initializes each tool and combines their resources to integrate them into the agent seamlessly.  
  
- **Conversation Thread and User Messages:**  
    
  A conversation thread is established where multiple user messages are sent to the agent. The agent processes each message using the appropriate tool:  
    
  - **Message 1**: Utilizes Bing Grounding to provide real-time information.  
  - **Message 2**: Leverages File Search to extract details from the uploaded PDF.  
  - **Message 3**: Uses Code Interpreter to generate a bar chart based on the CSV data.  
  
- **Handling Responses:**  
    
  For each user message, the agent's response is retrieved and printed. In the case of file generation (e.g., chart creation), the generated file is saved to the specified `TARGET_DIR`.  
  
- **Resource Cleanup:**  
    
  After processing all messages, the script cleans up by deleting the vector store, uploaded files, and the agent to free up resources.  
  
## Next Steps  
  
Congratulations! You've successfully created a **Multi-Tool AI Agent** that can handle diverse user queries by leveraging File Search, Code Interpretation, and Bing Search capabilities. This integration empowers your agent to provide comprehensive and dynamic responses based on both static documents and real-time web data.