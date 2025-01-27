import os  
from azure.ai.projects import AIProjectClient  
from azure.identity import DefaultAzureCredential  

# Initialize the AI Project Client  
project_client = AIProjectClient.from_connection_string(  
    credential=DefaultAzureCredential(),   
    conn_str=os.environ["PROJECT_CONNECTION_STRING"]  
)  

with project_client:  
    # Create a simple agent  
    agent = project_client.agents.create_agent(  
        model="gpt-4o-mini",  
        name="joke-agent",  
        instructions="You are a humorous AI agent. Your task is to generate a joke based on the topic provided by the user. Ensure the joke is light-hearted, appropriate, and relevant to the topic.",  
        tools=[]  # No tools for this basic tutorial  
    )  
    print(f"Created agent, agent ID: {agent.id}")  

    # Create a conversation thread  
    thread = project_client.agents.create_thread()  
    print(f"Created thread, thread ID: {thread.id}")  

    # Add a user message to the thread  
    message = project_client.agents.create_message(  
        thread_id=thread.id,  
        role="user",  
        content="Microsoft"  
    )  
    print(f"Created message, message ID: {message.id}")  

    # Run the agent  
    run = project_client.agents.create_and_process_run(thread_id=thread.id, assistant_id=agent.id)  
    print(f"Run finished with status: {run.status}")  

    if run.status == "failed":  
        print(f"Run failed: {run.last_error}")  

    # Retrieve and print the agent's response  
    messages = project_client.agents.list_messages(thread_id=thread.id)  
    last_msg = messages.get_last_text_message_by_role("assistant")  
    if last_msg:  
        print(f"Agent Response: {last_msg.text.value}")  

    # Clean up by deleting the agent  
    project_client.agents.delete_agent(agent.id)  
    print("Deleted agent")  