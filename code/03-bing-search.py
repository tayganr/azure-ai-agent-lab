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