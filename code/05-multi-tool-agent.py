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