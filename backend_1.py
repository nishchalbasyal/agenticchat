from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph.message import add_messages
from langchain_openrouter import ChatOpenRouter
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv


load_dotenv()


class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    

llm = ChatOpenRouter(
    model="deepseek/deepseek-v3.2")

def chat_node(state: ChatState):

    #take user query from state
    messages = state['messages']

    #send to LLM
    response = llm.invoke(messages)

    # response store state
    return {'messages': [response]}

checkpointer = MemorySaver()

graph = StateGraph(ChatState)

graph.add_node('chat_node', chat_node)
graph.add_edge(START, 'chat_node')

graph.add_edge('chat_node', END)


chatbot = graph.compile(checkpointer=checkpointer)

# stream = for message_chunk chatbot.stream(
#     {'messages': [HumanMessage(content='Which is the beautiful country in the World ?')]},
#     stream_mode="messages"
# )
