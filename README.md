# Azure AI Agent Service Lab

## What is Azure AI Agent Service

[Azure AI Agent Service](https://learn.microsoft.com/en-us/azure/ai-services/agents/overview) is a fully managed platform designed to help developers create, deploy, and scale AI agents with ease, without the need to manage underlying compute and storage resources. By utilising advanced language models, it simplifies the process of building AI agents that can answer questions, perform tasks, and automate workflows. The service offers seamless integration with various tools and data sources, enabling agents to access and interact with real-world data. It provides features like automatic tool calling, secure data management, and extensive data integrations, making it ideal for enterprise applications requiring enhanced security and flexibility.

## Azure AI Agent Service vs. OpenAI Assistants API

| **Feature**      | **Azure AI Agent Service**                                                                                       | **OpenAI Assistants API**                      |  
|------------------|-----------------------------------------------------------------------------------------------------------------|------------------------------------------------------|  
| 🧠 [**Model Selection**](https://learn.microsoft.com/en-us/azure/ai-services/agents/concepts/model-region-support) | OpenAI, Llama 3, Mistral, and Cohere                     | OpenAI              |  
| 📚 [**Knowledge**](https://learn.microsoft.com/en-us/azure/ai-services/agents/how-to/tools/overview#knowledge-tools) | Microsoft Fabric, SharePoint, Bing Search, Azure AI Search, and File Search | File search      |  
| 🛠️ [**Tools**](https://learn.microsoft.com/en-us/azure/ai-services/agents/how-to/tools/overview#action-tools)         | Azure Logic Apps, OpenAPI, Azure Functions, Code Interpreter, and Function Calling                      | Code Interpreter and Function Calling |  

## Concepts
   
| **Concept** | **Explanation** |  
|-------------|-----------------|  
| 🤖 **Agent**   | An AI-driven microservice that uses models and tools to perform tasks, answer questions, and automate workflows. Think of it as a virtual assistant powered by AI. |  
| 🧵 **Thread**  | A conversation session between an agent and a user. It stores messages and manages conversation history, ensuring the content fits within the model's context. |  
| ✉️ **Message** | A piece of communication within a thread, which can be text, images, or other files, created by either the agent or the user. |  
| 🚀 **Run**     | The activation of an agent to perform tasks based on the thread's messages. During a run, the agent processes the information and may call models and tools to achieve its objectives. |  
| 📝 **Run Step**     | A detailed list of actions taken by the agent during a run. Each step shows how the agent interacts with tools, models, and messages to reach its final outcome. Examining run steps helps you understand the agent's decision-making process. |  

Based on the provided context, here's an explanation of how pricing works for the Azure AI Agent Service:  
   
### 💵 Pricing  
   
1. **Inference Costs**:  
   - You are charged based on the inference cost of the base model used by each agent. This means that for each agent you create, you will incur charges for using the specific model (e.g., `gpt-4-0125`) associated with that agent.
   
2. **Code Interpreter Tool**:  
   - If your agent utilises the Code Interpreter tool, the charges are based on the sessions created. For example, if the Code Interpreter is invoked simultaneously in two separate threads, this results in two distinct sessions. Each session lasts for an hour by default. Therefore, if a user continues to interact with the Code Interpreter within the same thread for up to an hour, the fee is only charged once for that session.  
   
3. **File Search**:  
   - File search is billed according to the vector storage used. This implies that charges are associated with the amount of storage required to manage and index the files used in search operations.  
   
4. **No Additional Pricing or Quotas**:  
   - There are no additional pricing structures or quotas specifically for using the AI Agent Service. The charges are primarily associated with the models and tools used within the service.  
   
## 🤔 Technical Prerequisites  
   
1. **Azure Subscription**:   
   - You need an active Azure subscription. You can create one for free if you don't have it.  
   
2. **Python Environment**:  
   - Install Python 3.8 or later. Make sure your Python environment is set up and properly configured.  
   
3. **Azure AI Developer Role**:  
   - Ensure you have the Azure AI Developer RBAC role assigned at the appropriate level to access and manage Azure AI services.  
   
4. **Cognitive Services OpenAI User Role**:  
   - Assign the Cognitive Services OpenAI User role to your account to access OpenAI models and features.  
   
5. **Azure CLI**:  
   - Install the Azure CLI and the machine learning extension. Ensure it is updated to the latest version.  
   
6. **Python Packages**:  
   - Install necessary Python packages using pip:  
     ```bash  
     pip install azure-ai-projects  
     pip install azure-identity  
     ```  
   
7. **Connection String**:  
   - Create a connection string using information from your Azure AI project. This includes `HostName`, `AzureSubscriptionId`, `ResourceGroup`, and `ProjectName`. Set this as an environment variable `PROJECT_CONNECTION_STRING`.  
   
8. **Login to Azure**:  
   - Use the Azure CLI to log in to your Azure subscription.  

## 📚 Tutorial Series  
   
To help you get started with the Azure AI Agent Service, we've prepared a series of tutorials. These tutorials will guide you through the process of building and enhancing AI agents using the service.  
   
1. **[Getting Started with Azure AI Agents: Your First Agent](/tutorials/01-basic-agent.md)**    
   Learn how to create a basic agent using the Python SDK, focusing on instructions and messages.  
   
2. **[Empowering Your Agent: Integrating File Search](/tutorials/02-file-search.md)**    
   Discover how to add file search capabilities to your agent, enabling it to handle file-based interactions.  
   
3. **[Augmenting Intelligence: Using Bing Search with Your Agent](/tutorials/03-bing-search.md)**    
   Integrate Bing Search to fetch real-time web data and enhance agent responses.  
   
4. **[Enhancing Interactivity: Implementing the Code Interpreter Tool](/tutorials/04-code-interpreter.md)**    
   Utilize the Code Interpreter tool to perform complex computations within your agent.  
   
5. **[Creating a Multi-Tool Agent: Combining File Search, Bing Search, and Code Interpreter](/tutorials/05-multi-tool-agent.md)**    
   Build a comprehensive agent solution that leverages multiple tools for advanced functionality.  
   
Feel free to follow these tutorials in order to gradually build up your skills and understanding of the Azure AI Agent Service.  