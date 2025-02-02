import os  
  
from azure.ai.projects import AIProjectClient  
from azure.identity import DefaultAzureCredential  
  
# === Environment Variables ===  
PROJECT_CONNECTION_STRING_ENV = "PROJECT_CONNECTION_STRING"  
  
# === Agent Configuration ===  
AGENT_NAME = "joke-agent"  
AGENT_MODEL = "gpt-4o-mini"  
AGENT_INSTRUCTIONS = (  
    "You are a humorous AI agent. Your task is to generate a joke based on the topic "  
    "provided by the user. Ensure the joke is light-hearted, appropriate, and relevant to the topic."  
)  
  
# === Operational Constants ===  
USER_MESSAGE_CONTENT = "Microsoft"  
  
  
def main():  
    """  
    Main function to set up a basic AI agent, interact with it, and manage resources.  
    """  
    print("Starting the AI agent setup process.")  
  
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
            # Step 2: Create a simple agent  
            print("Step 2: Creating a simple agent...")  
            agent = project_client.agents.create_agent(  
                model=AGENT_MODEL,  
                name=AGENT_NAME,  
                instructions=AGENT_INSTRUCTIONS,  
                tools=[]  # No tools for this basic setup  
            )  
            print(f"Created agent: {AGENT_NAME} (ID: {agent.id})")  
  
            # Step 3: Create a conversation thread  
            print("Step 3: Creating conversation thread...")  
            thread = project_client.agents.create_thread()  
            print(f"Created conversation thread (ID: {thread.id})")  
  
            # Step 4: Add a user message to the thread  
            print("Step 4: Adding user message to the thread...")  
            message = project_client.agents.create_message(  
                thread_id=thread.id,  
                role="user",  
                content=USER_MESSAGE_CONTENT  
            )  
            print(f"Added user message (ID: {message.id})")  
  
            # Step 5: Run the agent  
            print("Step 5: Running the agent...")  
            run = project_client.agents.create_and_process_run(  
                thread_id=thread.id,  
                assistant_id=agent.id  
            )  
            print(f"Run completed with status: {run.status}")  
  
            if run.status == "failed":  
                print(f"Run failed: {run.last_error}")  
            else:  
                # Step 6: Retrieve and print the agent's response  
                print("Step 6: Retrieving agent's response...")  
                messages = project_client.agents.list_messages(thread_id=thread.id)  
                last_msg = messages.get_last_text_message_by_role("assistant")  
                if last_msg:  
                    print(f"Agent Response: {last_msg.text.value}")  
                else:  
                    print("No response from the agent.")  
  
            # Step 7: Clean up by deleting the agent  
            print("Step 7: Cleaning up resources...")  
            project_client.agents.delete_agent(agent.id)  
            print(f"Deleted agent (ID: {agent.id})")  
  
    except Exception as e:  
        print(f"An error occurred: {e}")  
  
    print("AI agent setup process completed.")  
  
  
if __name__ == "__main__":  
    main()  