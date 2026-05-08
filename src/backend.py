from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph.message import add_messages
from langchain_openrouter import ChatOpenRouter
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv
from shared_checkpoint import checkpointer, save_title, get_title, get_all_titles

from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

import requests
import time
load_dotenv()

llm =  ChatOpenAI(model="gpt-5.4-nano")

# Tools
search_tool = DuckDuckGoSearchRun(region="us-en")

@tool
def calculator(first_num: float,second_num: float, operation:str)->dict:
    
    
    """
      Perform a basic arithmetic operation on two numbers.
      Supported operations: add, sub, mul,div
    """
    
    # Add delay to show status
    time.sleep(10)
 
    try:
        if operation == "add":
            result = first_num + second_num
        elif operation == "sub":
            result = first_num - second_num
        elif operation == "mul":
            result = first_num * second_num
        elif operation == "div":
            if second_num == 0: return {"error":"Division by 0 is not allowed"}
            result = first_num/second_num
        else:
            return {"error": f"Unsupported operation '{operation}'"}
        return{"first_num": first_num,"second_num":second_num,"operation":operation,"result":result}        
    except Exception as e:
        return {"error": str(e)}
    
@tool
def get_stock_price(symbol:str)->dict:
    """
     Fetch latest stock price for a given symbol (e.g. 'AAPL','TSLA')
     using Alpha Vantage with API key in the URL.
    """
    
    # Add delay to show status
    time.sleep(2)
    
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey=VJA7TM3FZFLDMWZM"
    r = requests.get(url)
    return r.json()


# Make tool list
tools = [get_stock_price, search_tool, calculator]

#Make the LLM tool-aware
llm_with_tools = llm.bind_tools(tools)

# state 
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# graph nodes
def chat_node(state: ChatState):
    """LLM ndode that may answer or request a tool call"""
    messages = state['messages']
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

tool_node = ToolNode(tools)


#graph structure
graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_node("tools", tool_node)

graph.add_edge(START,"chat_node")

graph.add_conditional_edges("chat_node", tools_condition)
graph.add_edge("tools","chat_node")

chatbot = graph.compile(checkpointer=checkpointer)



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