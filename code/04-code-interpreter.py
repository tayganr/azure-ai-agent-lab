import os  
  
from azure.ai.projects import AIProjectClient  
from azure.ai.projects.models import CodeInterpreterTool, FilePurpose  
from azure.identity import DefaultAzureCredential  
  
# === Environment Variables ===  
PROJECT_CONNECTION_STRING_ENV = "PROJECT_CONNECTION_STRING"  
  
# === Agent Configuration ===  
AGENT_NAME = "code-interpreter-agent"  
AGENT_MODEL = "gpt-4o-mini"  # Ensure to use a supported model  
AGENT_INSTRUCTIONS = "You are a helpful agent."  
  
# === Operational Constants ===  
FILE_PATH = "./documents/quarterly_results.csv"  # Path to the local CSV file to upload  
VECTOR_STORE_NAME = "my_vectorstore"  # Although not used here, keeping for consistency  
USER_MESSAGE_CONTENT = (  
    "Could you please create a bar chart in the TRANSPORTATION sector for the "  
    "operating profit from the uploaded CSV file and provide the file to me?"  
)  
TARGET_DIR = "./documents"  # Directory to save the generated files  
  
  
def main():  
    """  
    Main function to set up an AI agent with Code Interpreter tool, interact with it, and manage resources.  
    """  
    print("Starting the Code Interpreter AI agent setup process.")  
  
    # Step 0: Validate environment variables  
    print("Step 0: Validating environment variables...")  
    project_conn_str = os.environ.get(PROJECT_CONNECTION_STRING_ENV)  
    if not project_conn_str:  
        raise EnvironmentError(  
            f"Environment variable '{PROJECT_CONNECTION_STRING_ENV}' is not set."  
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
            # Step 2: Upload the CSV file  
            print(f"Step 2: Uploading file '{FILE_PATH}'...")  
            uploaded_file = project_client.agents.upload_file_and_poll(  
                file_path=FILE_PATH,  
                purpose=FilePurpose.AGENTS  
            )  
            print(f"Uploaded file, file ID: {uploaded_file.id}")  
  
            # Step 3: Initialize Code Interpreter Tool  
            print("Step 3: Setting up Code Interpreter tool...")  
            code_interpreter = CodeInterpreterTool(file_ids=[uploaded_file.id])  
  
            # Step 4: Create an agent with the Code Interpreter tool  
            print("Step 4: Creating agent with Code Interpreter tool...")  
            agent = project_client.agents.create_agent(  
                model=AGENT_MODEL,  
                name=AGENT_NAME,  
                instructions=AGENT_INSTRUCTIONS,  
                tools=code_interpreter.definitions,  
                tool_resources=code_interpreter.resources,  
                headers={"x-ms-enable-preview": "true"}  # If necessary  
            )  
            print(f"Created agent, ID: {agent.id}")  
  
            # Step 5: Create a conversation thread  
            print("Step 5: Creating conversation thread...")  
            thread = project_client.agents.create_thread()  
            print(f"Created thread, ID: {thread.id}")  
  
            # Step 6: Add a user message to the thread  
            print("Step 6: Adding user message to the thread...")  
            user_message = project_client.agents.create_message(  
                thread_id=thread.id,  
                role="user",  
                content=USER_MESSAGE_CONTENT  
            )  
            print(f"Created message, ID: {user_message.id}")  
  
            # Step 7: Run the agent  
            print("Step 7: Running the agent...")  
            run = project_client.agents.create_and_process_run(  
                thread_id=thread.id,  
                assistant_id=agent.id  
            )  
            print(f"Run finished with status: {run.status}")  
  
            if run.status == "failed":  
                print(f"Run failed: {run.last_error}")  
            else:  
                # Step 8: Delete the uploaded file to free up space  
                print("Step 8: Deleting the uploaded file to free up space...")  
                project_client.agents.delete_file(uploaded_file.id)  
                print("Deleted uploaded file.")  
  
                # Step 9: Retrieve and print the agent's response  
                print("Step 9: Retrieving agent's response...")  
                messages = project_client.agents.list_messages(thread_id=thread.id)  
                last_msg = messages.get_last_message_by_role("assistant")  
  
                if last_msg:  
                    # Print the content of the last text message  
                    if hasattr(last_msg, 'text_messages') and last_msg.text_messages:  
                        print(f"Agent Response: {last_msg.text_messages[-1].text.value}")  
  
                    # Check for file path annotations and download files  
                    if hasattr(last_msg, 'file_path_annotations'):  
                        for file_path_annotation in last_msg.file_path_annotations:  
                            file_info = file_path_annotation.file_path  
                            file_id = file_info.get('file_id')  
                            file_name = file_info.get('file_name', 'chart.png')  
                            if file_id:  
                                print(f"Downloading file with ID: {file_id} as '{file_name}'...")  
                                project_client.agents.save_file(  
                                    file_id=file_id,  
                                    file_name=file_name,  
                                    target_dir=TARGET_DIR  
                                )  
                                print(f"Saved file: {file_name} in '{TARGET_DIR}'")  
                else:  
                    print("No response from the agent.")  
  
            # Step 10: Clean up resources  
            print("Step 10: Cleaning up resources...")  
            project_client.agents.delete_agent(agent.id)  
            print(f"Deleted agent (ID: {agent.id})")  
  
    except Exception as e:  
        print(f"An error occurred: {e}")  
  
    print("Code Interpreter AI agent setup process completed.")  
  
  
if __name__ == "__main__":  
    main()  