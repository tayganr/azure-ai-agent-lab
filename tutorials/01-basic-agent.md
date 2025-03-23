# Tutorial 01: Getting Started with Azure AI Agents

[Home](../README.md) - [Next Module >](./02-file-search.md)
   
Welcome to the first tutorial in the Azure AI Agent Service series! In this tutorial, we will guide you through creating a basic AI agent using the Python SDK. This agent will interact with users by responding to a simple query.   
  
## Step 1: Prerequisites  
  
Before starting this tutorial, ensure you have completed the setup as described in the [Technical Prerequisites](../README.md#-technical-prerequisites) section of the README. Key steps include:
  
- **Python Environment**: Python 3.8 or later should be installed and configured.
- **Azure CLI**: Install Azure CLI and log in to your subscription.
- **Repository Setup**: Clone the repository and set up a Python virtual environment.  
- **Install Dependencies**: Use `pip` to install the required packages from `requirements.txt`.
- **Environment Variable**: Create a `.env` file in the root directory of your project with the following content:
  ```
  PROJECT_CONNECTION_STRING=your_connection_string_value_here
  ```

## Step 2: Create the Agent  
   
**Write the Python Code:**  
  
Open your preferred text editor and create a new Python file. Copy and paste the following code into the file:
   
  ```python
    import os  
    from dotenv import load_dotenv
    from azure.ai.projects import AIProjectClient  
    from azure.identity import DefaultAzureCredential  
    
    # === Agent Configuration ===  
    AGENT_NAME = "joke-agent"  
    AGENT_MODEL = "gpt-4o-mini"  
    AGENT_INSTRUCTIONS = (  
        "You are a humorous AI agent. Your task is to generate a joke based on the topic "  
        "provided by the user. Ensure the joke is light-hearted, appropriate, and relevant to the topic."  
    )  
    
    # === User Message Configuration ===
    USER_MESSAGE_CONTENT = "Microsoft"  

    # Load environment variables from .env file  
    load_dotenv()  

    # Initialize the AI Project Client
    project_client = AIProjectClient.from_connection_string(  
        credential=DefaultAzureCredential(),  
        conn_str=os.environ.get("PROJECT_CONNECTION_STRING")  
    )  

    # Create an agent  
    agent = project_client.agents.create_agent(  
        model=AGENT_MODEL,  
        name=AGENT_NAME,  
        instructions=AGENT_INSTRUCTIONS,  
        tools=[]  
    )  

    # Create a thread  
    thread = project_client.agents.create_thread()  

    # Add a message to the thread  
    message = project_client.agents.create_message(  
        thread_id=thread.id,  
        role="user",  
        content=USER_MESSAGE_CONTENT  
    )

    # Run the agent  
    run = project_client.agents.create_and_process_run(  
        thread_id=thread.id,  
        assistant_id=agent.id  
    )  

    # Retrieve and print the agent's response  
    messages = project_client.agents.list_messages(thread_id=thread.id)  
    last_msg = messages.get_last_text_message_by_role("assistant")  
    print(last_msg.text.value)  

    # Clean up resources
    project_client.agents.delete_agent(agent.id)  
    project_client.agents.delete_thread(thread.id)
  ```  
   
## Step 3: Run Your Code
   
**Execute the Python Script:**  
  
Open your terminal or command prompt, navigate to the directory where your Python file is saved, and run the script:  

```bash  
python your_script_name.py  
```  
   
## Understanding the Code  
   

1. **Initialize AI Project Client:** Set up a client using credentials and connection settings to interact with the AI service.
2. **Create an Agent:** Define an AI agent by specifying its model, name, and behavior instructions.
3. **Create a Thread:** Establish a thread to facilitate communication with the agent.
4. **Add a Message to the Thread:** Insert a user message into the thread to initiate communication with the agent.
5. **Execute a Run:** Initiate a run to process the thread and generate a response from the agent.
6. **Retrieve and Print the Agent's Response:** Access and display the agent's reply from the thread.
7. **Clean Up Resources:** Delete the agent and thread to efficiently manage resources.
   
## Next Steps  
   
Congratulations! You've successfully created a basic Azure AI agent that can respond to user inquiries. This foundational setup prepares you for more advanced tutorials where you'll integrate tools and extend your agent's capabilities.  
   
Proceed to the next tutorial in the series to learn how to enhance your agent with file search capabilities: [Tutorial 02: Integrating File Search](02-file-search.md).