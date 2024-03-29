from langchain.agents import ConversationalChatAgent, AgentExecutor
from bs_agents.tools.vectordb_tool import get_vectordb_tool
from bs_agents.tools.general_tool import get_general_tool
from bs_agents.tools.greetuser_tool import get_greet_user_tool
from model import get_chat_model
from bs_agents.agent_chat_memory import get_memory
from bs_agents.service_agent_prompt import service_agent_prompt
from langchain.agents import load_tools
from model import get_llm



def get_tools():
    tools = load_tools([], llm = get_llm('openai'))
    tools.append(get_vectordb_tool())
    tools.append(get_greet_user_tool())
    tools.append(get_general_tool())
    return tools

# def get_agent():
model = get_chat_model('openai')
system_message = service_agent_prompt

agent_definition = ConversationalChatAgent.from_llm_and_tools(
    llm = model,
    tools  = get_tools(),
    system_message = system_message
)

agent_execution = AgentExecutor.from_agent_and_tools(
    agent=agent_definition,
    llm=model,
    tools= get_tools(),
    handle_parsing_erros= True,
    verbose = True,
    max_iterations=3,
    memory = get_memory(),
    handle_parsing_errors=True
)
    # return agent_execution



