---
title: "LangGraph Chatbot with Tools, Memory, and Streaming UI"
slug: "langgraph-chatbot-tools-memory-streaming"
date: "2026-05-27"
author: "Nishchal Basyal"
description: "Built a LangGraph chatbot with Streamlit UI, SQLite conversation memory, multi-chat threads, AI-generated chat titles, and tool calling for search, calculation, and stock price lookup."
categories:
  - "LangGraph"
  - "AI Agent"
  - "Streamlit"
  - "LLM App"
  - "Python"
image: "/Images/projects/langgraph_chatbot/langgraph_chatbot_architecture.svg"
---

### Problem

Most basic chatbot projects only send one message to an LLM and show one response back.

That is fine for a demo, but it does not feel like a real chat application. A useful chatbot needs to remember previous messages, keep separate conversations, stream the response while it is being generated, and call tools when the answer needs external data or calculation.

### Goal

The goal of this project was simple:

- Build a chatbot using **LangGraph**
- Keep conversation history using persistent checkpoints
- Support multiple chat threads
- Stream assistant responses in the UI
- Add tool calling for practical tasks
- Keep the app easy to run locally or with Docker

### Solution Overview

I built a conversational AI chatbot using **LangGraph**, **Streamlit**, **LangChain**, and **SQLite**.

The backend is handled by LangGraph. The frontend is built with Streamlit. Conversation state is saved with a SQLite checkpointer, so old chats can be loaded again later.

The chatbot can also call tools when needed, including:

- DuckDuckGo search
- basic calculator
- stock price lookup using Alpha Vantage

![](/Images/projects/langgraph_chatbot/langgraph_chatbot_architecture.svg)

### How It Works

#### 1. Streamlit Chat UI

The user interacts with the chatbot from a Streamlit interface.

The UI handles:

- user input
- chat message display
- new chat creation
- old chat loading
- assistant response streaming
- tool running status

I used Streamlit session state to keep the selected chat thread and message history available while the app is running.

#### 2. LangGraph State Management

The main backend is built with LangGraph's `StateGraph`.

The chat state is simple and focused:

```python
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
```

This keeps the conversation as a list of messages. LangGraph manages how new user messages, AI messages, and tool messages are added into the state.

#### 3. Tool Calling

The model is connected with tools using LangChain tool binding.

Current tools in the project:

- `calculator()` for add, subtract, multiply, and divide
- `DuckDuckGoSearchRun()` for web search
- `get_stock_price()` for stock price data from Alpha Vantage

When the model decides a tool is needed, LangGraph routes the flow to the tool node and then sends the result back to the chat node.

The flow is:

```text
User message -> chat node -> tool needed? -> tool node -> chat node -> final response
```

This makes the chatbot more useful than a normal LLM wrapper because it can use external functions before answering.

#### 4. Persistent Conversation Memory

For memory, I used LangGraph's SQLite checkpointer.

Each conversation has its own `thread_id`, and the thread id is passed through the graph config:

```python
CONFIG = {
    "configurable": {
        "thread_id": str(st.session_state["thread_id"])
    },
    "metadata": {
        "thread_id": str(st.session_state["thread_id"])
    },
    "run_name": "chat_turn"
}
```

Because of this, each chat thread keeps its own message history.

The user can start a new chat, switch back to an old one, and continue from the previous context.

#### 5. AI-Generated Chat Titles

Instead of showing raw thread ids in the sidebar, I added generated titles.

When the first message is sent, the app asks the model to create a short 4-5 word title. That title is saved in a separate SQLite metadata table.

This makes the sidebar easier to read.

Example:

```text
Thread id: 932c1e2a-8b6f...
Title: Stock Price Lookup Help
```

This is a small feature, but it improves the experience a lot when there are many saved conversations.

#### 6. Streaming Response

The assistant response is streamed back into the Streamlit UI.

Instead of waiting for the full response, the user can see the answer as it is being generated. When tools are running, the UI also shows a status message like tool running or tool finished.

This makes the chatbot feel more interactive and gives better feedback during slower tool calls.

#### 7. Docker Support

I also added Docker support so the project can be run in a cleaner environment.

The Docker setup installs dependencies, copies the `src` folder, exposes Streamlit on port `8501`, and starts the app using:

```bash
streamlit run src/frontend.py --server.port=8501 --server.address=0.0.0.0
```

This makes the project easier to test outside my local Python setup.

### Project Structure

The main files are:

- `src/frontend.py` - Streamlit chat interface
- `src/backend.py` - LangGraph graph, model call, and tool setup
- `src/shared_checkpoint.py` - SQLite checkpoint and chat title metadata
- `Dockerfile` - container setup
- `docker-compose.yml` - local Docker run configuration

### What This Project Shows

This project helped me understand how to move from a simple chatbot to a more structured AI agent application.

It covers:

- LangGraph state management
- persistent chat memory
- multi-thread conversations
- tool calling
- streaming UI responses
- SQLite metadata storage
- Docker-based app running

### Why I Built It This Way

I wanted to keep the project practical.

Instead of building a large dashboard or full authentication system, I focused on the core agent workflow:

- user sends a message
- LangGraph manages state
- model decides whether tools are needed
- tools run when required
- result streams back to the UI
- conversation is saved for later

That gives the project a strong base without making it unnecessarily complex.

### Future Improvements

If I extend this further, I would add:

- authentication for private chat history
- better error handling for tool failures
- configurable model provider from the UI
- database path cleanup for Docker volume persistence
- conversation delete and rename options
- LangSmith tracing view for debugging agent steps

### Final Thoughts

This project is a good example of how LangGraph can be used to build a chatbot that has memory, tools, and a real interface.

It is still simple enough to understand, but it has the important parts needed for a more serious AI assistant: state, persistence, streaming, and tool execution.

That balance is what I wanted from this project.
