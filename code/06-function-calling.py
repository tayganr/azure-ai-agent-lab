import os  
import json
import datetime
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient  
from azure.ai.projects.models import FunctionTool, ToolSet
from azure.identity import DefaultAzureCredential  

def fetch_weather(location: str) -> str:
    """
    Fetches the weather information for the specified location.

    :param location (str): The location to fetch weather for.
    :return: Weather information as a JSON string.
    :rtype: str
    """
    # In a real-world scenario, you'd integrate with a weather API.
    # Here, we'll mock the response.
    mock_weather_data = {"New York": "Sunny, 25°C", "London": "Cloudy, 18°C", "Tokyo": "Rainy, 22°C"}
    weather = mock_weather_data.get(location, "Weather data not available for this location.")
    weather_json = json.dumps({"weather": weather})
    return weather_json


def get_current_time() -> str:
    """
    Gets the current time in AM/PM format.

    :return: The current time in AM/PM format.
    :rtype: str
    """
    current_time = datetime.datetime.now().strftime("%I:%M:%S %p")
    return current_time

user_functions = set()
user_functions.add(fetch_weather)
user_functions.add(get_current_time)
functions = FunctionTool(user_functions)
toolset = ToolSet()
toolset.add(functions)
  
# Agent Configuration
AGENT_NAME = "weather-agent"
AGENT_MODEL = "gpt-4o-mini"  
AGENT_INSTRUCTIONS = (  
    "You are a weather bot. Use the provided functions to help answer questions."
)  
  
# User Message Configuration
# USER_MESSAGE_CONTENT = "What's the weather in New York?"
USER_MESSAGE_CONTENT = "What's the current time?"

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
    toolset=toolset
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
