from langchain.agents import initialize_agent
from langchain.chat_models import ChatOpenAI

llm = ChatOpenAI(temperature=0.5)

def create_agent():
    agent = initialize_agent(
        tools=[],
        llm=llm,
        agent="zero-shot-react-description"
    )
    return agent

def ask_agent(agent, question):
    return agent.run(question)
