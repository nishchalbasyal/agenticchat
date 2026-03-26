from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph.message import add_messages
from langchain_openrouter import ChatOpenRouter
from dotenv import load_dotenv
from shared_checkpoint import checkpointer, save_title, get_title, get_all_titles

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


graph = StateGraph(ChatState)

graph.add_node('chat_node', chat_node)
graph.add_edge(START, 'chat_node')

graph.add_edge('chat_node', END)


chatbot = graph.compile(checkpointer=checkpointer)

# stream = for message_chunk chatbot.stream(
#     {'messages': [HumanMessage(content='Which is the beautiful country in the World ?')]},
#     stream_mode="messages"
# )


def retrive_all_threads():
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config['configurable']['thread_id'])
        
    return list(all_threads)


def generate_title(user_message: str) -> str:
    """Generate a 4-5 word title from the first user message"""
    prompt = f"""Generate a very concise 4-5 word title for this conversation based on the user's first message. 
Return ONLY the title, nothing else.

User message: {user_message}"""
    
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        title = response.content.strip()
        # Ensure title is not too long
        words = title.split()
        if len(words) > 8:
            title = ' '.join(words[:8])
        return title
    except Exception as e:
        print(f"Error generating title: {e}")
        return user_message[:50]  # Fallback to first 50 chars of message
