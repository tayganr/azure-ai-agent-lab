# Tutorial 01: Getting Started with Azure AI Agents

[Home](../README.md) - [Next Module >](./02-file-search.md)
   
Welcome to the first tutorial in the Azure AI Agent Service series! In this tutorial, we will guide you through creating a basic AI agent using the Python SDK. This agent will interact with users by responding to a simple query.   
  
## Step 1: Prerequisites  
  
Before starting this tutorial, ensure you have completed the setup as described in the [Technical Prerequisites](../README.md#-technical-prerequisites) section of the README. Key steps include:
  
- **Python Environment**: Python 3.8 or later should be installed and configured.
- **Azure CLI**: Install Azure CLI and log in to your subscription.
- **Repository Setup**: Clone the repository and set up a Python virtual environment.  
- **Install Dependencies**: Use `pip` to install the required packages from `requirements.txt`.
- **Environment Variable**: Ensure the `PROJECT_CONNECTION_STRING` is set.

## Step 2: Create the Agent  
   
1. **Write the Python Code:**  
  
   Open your preferred text editor and create a new Python file. Copy and paste the following code into the file:
   
  ```python
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
  ```  
   
## Step 3: Run Your Code
   
2. **Execute the Python Script:**  
  
   Open your terminal or command prompt, navigate to the directory where your Python file is saved, and run the script:  
  
   ```bash  
   python your_script_name.py  
   ```  
  
   Replace `your_script_name.py` with the actual filename of your script.  
   
3. **Observe the Output:**  
  
   - As the script executes, it will create an agent, set up a conversation thread, and send a user message.  
   - The agent will process the message and respond based on its instructions.  
   - You should see the following output in your terminal:  
  
     ```  
      Starting the AI agent setup process.
      Step 0: Validating environment variables...
      Environment variables validated successfully.
      Step 1: Initializing Azure AI Project Client...
      Azure AI Project Client initialized.
      Step 2: Creating a simple agent...
      Created agent: joke-agent (ID: asst_iInqZCp66emWKKuYhSaksFDl)
      Step 3: Creating conversation thread...
      Created conversation thread (ID: thread_bHDkalKAz1YlakOmsq5HlL3f)
      Step 4: Adding user message to the thread...
      Added user message (ID: msg_hNk3laRakqZchyYt9bRr1Uye)
      Step 5: Running the agent...
      Run completed with status: RunStatus.COMPLETED
      Step 6: Retrieving agent's response...
      Agent Response: Why did Microsoft break up with...
      Step 7: Cleaning up resources...
      Deleted agent (ID: asst_iInqZCp66emWKKuYhSaksFDl)
      AI agent setup process completed.
     ```  
  
   Note: The agent's response may vary as it is generated by the language model.  
   
## Understanding the Code  
   
- **Agent Creation:**  
  
  The agent is created with minimal setup, using a model and basic instructions. No additional tools are used in this simple example.  
   
- **Thread and Message:**  
  
  A conversation thread is established where the user can send messages. In this tutorial, we send a single message.  
   
- **Agent Run:**  
  
  The agent processes the thread's messages and responds. The status of the run and the agent's response are printed to the console.  
   
- **Cleanup:**  
  
  After the interaction, the agent is deleted to clean up resources.  
   
## Next Steps  
   
Congratulations! You've successfully created a basic Azure AI agent that can respond to user inquiries. This foundational setup prepares you for more advanced tutorials where you'll integrate tools and extend your agent's capabilities.  
   
Proceed to the next tutorial in the series to learn how to enhance your agent with file search capabilities: [Tutorial 02: Integrating File Search](02-file-search.md).