# LanGraph Chatbot

A multi-threaded conversational AI chatbot built with **LanGraph**, **Streamlit**, and **DeepSeek LLM** via OpenRouter. This application demonstrates state management, conversation persistence, and streaming-based UI interactions.

## 📋 Project Overview

This project is a full-stack chatbot application that showcases:

- **LanGraph State Management**: Uses LanGraph's StateGraph for managing conversation states
- **Multi-Thread Conversations**: Supports multiple concurrent chat threads with persistent storage
- **Real-Time Streaming**: Stream AI responses to the UI in real-time using Streamlit
- **Conversation Persistence**: SQLite database for storing and retrieving conversation history
- **Tool Integration Ready**: Architecture supports adding tools for extended functionality

## 🎯 Key Features

- **Multi-Chat Support**: Create and manage multiple independent conversation threads
- **AI-Generated Titles**: LLM automatically generates 4-5 word titles for each conversation based on the first message
- **Persistent Storage**: All conversations are saved in SQLite database
- **Stream Responses**: Real-time AI response streaming with status indicators
- **Tool Integration**: Built-in support for tool execution with status tracking
- **Thread Management**: Load previous conversations and switch between threads
- **Easy Navigation**: Sidebar shows all conversations with readable AI-generated titles instead of thread IDs
- **Modern UI**: Built with Streamlit for responsive and interactive interface

## 📁 Core Files

### `frontend.py`

The Streamlit-based user interface that handles:

- Chat message display and input
- Thread/conversation management (create, load, switch)
- Real-time streaming of AI responses
- Tool execution status indicators
- Session state management
- **Auto-generates AI titles for conversations on first message**
- **Displays readable conversation titles in sidebar for easy navigation**

### `backend.py`

The LanGraph backend that contains:

- `ChatState`: TypedDict defining the conversation state structure
- `chat_node()`: Node function that sends messages to the LLM
- `chatbot`: Compiled LanGraph that manages chat workflow
- `retrive_all_threads()`: Function to retrieve all conversation threads from database
- `generate_title()`: **Generates 4-5 word AI titles from the first user message**

### `shared_checkpoint.py`

Shared checkpoint configuration:

- SQLite-based conversation persistence using `SqliteSaver`
- **Metadata table for storing conversation titles and timestamps**
- Database: `chatbot.db`
- Shared connection to ensure consistency across the application
- **Helper functions**:
  - `save_title()`: Save conversation title
  - `get_title()`: Retrieve title for a specific conversation
  - `get_all_titles()`: Get all titles for sidebar display

## 🚀 Setup Guide

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd "Langgraph Chatbot"
   ```

2. **Create a virtual environment (optional but recommended)**

   ```bash
   python -m venv venv

   # On Windows
   venv\Scripts\activate

   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the project root:

   ```
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   ```

   Get your OpenRouter API key from: https://openrouter.ai

5. **Run the application**

   ```bash
   streamlit run frontend.py
   ```

   The application will open at `http://localhost:8501`

## 💻 Code Architecture

### Message Flow

```
User Input (Streamlit UI)
    ↓
frontend.py: Chat Input Handler
    ↓
backend.py: Send to LLM via LanGraph
    ↓
chat_node(): Process with DeepSeek LLM
    ↓
shared_checkpoint.py: Store in SQLite DB
    ↓
frontend.py: Stream Response & Display
```

### State Management

The chatbot uses LanGraph's `StateGraph` with a `ChatState` TypedDict:

```python
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
```

Each message is tracked with its type (HumanMessage, AIMessage, ToolMessage), enabling the UI to render appropriate status indicators.

### Thread Configuration

Conversations use a thread-based configuration:

```python
CONFIG = {
    "configurable": {"thread_id": str(uuid)},
    "metadata": {"thread_id": str(uuid)},
    "run_name": "chat_turn"
}
```

Each thread maintains its own conversation history in the SQLite database.

### Conversation Title Generation

Each conversation gets an AI-generated title automatically:

1. **First Message Trigger**: When the user sends their first message, the `generate_title()` function is called
2. **LLM Processing**: The message is sent to the LLM with a prompt requesting a 4-5 word summary title
3. **Title Storage**: The generated title is saved to the `conversation_metadata` table with the thread ID
4. **UI Display**: The sidebar displays the title instead of the thread ID for easy navigation

**Example Flow**:

- User sends: "What's the capital of France?"
- LLM generates title: "French Capital Question"
- Sidebar shows: "French Capital Question" instead of "abc-123-def-456..."

**Benefits**:

- ✅ Easy conversation browsing
- ✅ Quick visual identification of past chats
- ✅ Clean separation between message history and metadata
- ✅ Automatic and zero-configuration

## 📚 Usage

### Sending Messages

1. Type your message in the input box
2. Press Enter or click Send
3. Watch the AI response stream in real-time

### Managing Conversations

- **New Chat**: Click "New Chat" button to start a fresh conversation thread
- **Load Old Chat**: Click on any thread ID in the sidebar to load previous conversations
- **View History**: All messages from the loaded thread appear automatically

### Tool Execution (When Enabled)

- When the LLM calls a tool, a status indicator shows "Running tools..."
- Tool execution is tracked and displayed when complete
- Status updates in real-time

## 🔧 Configuration

### LLM Model

In `backend.py`, change the model by updating:

```python
llm = ChatOpenRouter(model="deepseek/deepseek-v3.2")
```

Available models via OpenRouter: https://openrouter.ai/docs/models

### Database

SQLite database is created automatically as `chatbot.db` in the project root.

**Tables**:

1. **Message Storage** (LanGraph managed):
   - Stores all conversation messages
   - Automatically created and maintained by SqliteSaver

2. **conversation_metadata** (Custom):

   ```sql
   CREATE TABLE conversation_metadata (
       thread_id TEXT PRIMARY KEY,
       title TEXT,
       created_at TIMESTAMP
   )
   ```

   - Stores AI-generated conversation titles
   - `thread_id`: Links to the conversation thread
   - `title`: 4-5 word summary generated by LLM
   - `created_at`: Timestamp when the conversation started

## 🛠️ Extending the Project

### Adding Tools

1. Create tool functions in `backend.py`
2. Add tool nodes to the StateGraph
3. Update the graph edges to include tool execution
4. Frontend will automatically display tool status

### Custom LLM Integration

Replace the `ChatOpenRouter` with any LangChain LLM provider:

```python
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4")
```

### Database Migration

To use a different persistence backend:

1. Replace `SqliteSaver` in `shared_checkpoint.py`
2. LanGraph supports PostgreSQL, MongoDB, etc.

### Customizing Title Generation

To change how titles are generated, modify the `generate_title()` function in `backend.py`:

```python
def generate_title(user_message: str) -> str:
    """Customize the title generation prompt"""
    prompt = f"""Generate a custom title for: {user_message}"""

    response = llm.invoke([HumanMessage(content=prompt)])
    title = response.content.strip()
    return title
```

**Customization Ideas**:

- Generate emojis with titles
- Use different language for titles
- Extract keywords instead of generating
- Add maximum character limits
- Use local models for faster generation

## 📦 Dependencies

Key packages used:

- **langgraph**: State graph and workflow orchestration
- **streamlit**: Web UI framework
- **langchain**: LLM and tool abstraction
- **langchain-openrouter**: OpenRouter integration
- **python-dotenv**: Environment variable management

See `requirements.txt` for full list.

## 🐛 Troubleshooting

**Issue**: "API key not found"

- Solution: Ensure `.env` file exists with valid `OPENROUTER_API_KEY`

**Issue**: "Database locked"

- Solution: Ensure only one instance of the app is running

**Issue**: "Module not found"

- Solution: Reinstall dependencies: `pip install -r requirements.txt`

**Issue**: "Title generation fails" or "Conversations show as 'Chat (abc...)''"

- Solution: Check that LLM is working properly, titles use fallback if LLM fails (displays first 50 chars of message)
- The app still works fine without titles, so this won't block functionality

## 📝 License

This project is part of the Agents Course learning materials.

## 👨‍💻 Development

Built with modern Python web stack demonstrating:

- Async/streaming patterns with LanGraph
- Stateful application design
- Persistent message handling
- Real-time UI updates

---

**Happy chatting! 🤖**
