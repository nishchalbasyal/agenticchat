import streamlit as st
from langraph_tool_backend import chatbot, retrive_all_threads, generate_title
from shared_checkpoint import save_title, get_title, get_all_titles
from langchain_core.messages import  HumanMessage, AIMessage, ToolMessage
import uuid


# utility functions

def generate_thread_id():
    thread_id = str(uuid.uuid4())
    return thread_id

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = str(thread_id)
    add_thread(st.session_state['thread_id'])
    st.session_state['message_history'] = []
    

def add_thread(thread_id):
    thread_id = str(thread_id)
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)
        

def load_converstation(thread_id):
    try:
        state = chatbot.get_state(config={'configurable':{'thread_id': str(thread_id)}}).values
        if not state:
            return []
        msgs = state.get('messages', [])
        return msgs or []
    except Exception as e:
        print(f"Error loading conversation for thread {thread_id}: {e}")
        return []


message_history = []


user_input = st.chat_input('Type your message here...')

# *************************** Session UI ****************************
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []
    
    
if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = str(generate_thread_id())
    
    
if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = [str(tid) for tid in retrive_all_threads()]
    
add_thread(st.session_state['thread_id'])
        

# ***************************** Sidebar UI ***************************

st.sidebar.title('My chatbot')

if st.sidebar.button('New Chat'):
    reset_chat()

st.sidebar.header('Chats')

# Get all titles for display
thread_titles = get_all_titles()

for thread_id in st.session_state['chat_threads'][::-1]:
        # Get title or use thread_id as fallback
        display_title = thread_titles.get(thread_id, f"Chat ({thread_id[:8]}...)")
        
        if st.sidebar.button(display_title, key=f"chat_{thread_id}"):
            st.session_state['thread_id'] = thread_id
            messages = load_converstation(thread_id)
            
            temp_messages = []
            for message in messages:
                if isinstance(message, HumanMessage):
                    role='user'
                    temp_messages.append({'role': role, 'content': message.content})
                elif isinstance(message, AIMessage):
                    role='assistant'
                    temp_messages.append({'role': role, 'content': message.content})
                elif isinstance(message, ToolMessage):
                    tool_name = getattr(message, "name", "tool")
                    temp_messages.append({'role': 'status', 'content': f"✅ Tool finished: {tool_name}", 'state': 'complete'})
            st.session_state['message_history'] = temp_messages
        
# *********************************Main UI 
 
#loading the message history
for message in st.session_state['message_history']:
    if message.get("role") == "status":
        st.status(message["content"], state=message.get("state", "complete"))
    else:
        with st.chat_message(message["role"]):
            st.text(message["content"])

if user_input:
    st.session_state['message_history'].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.text(user_input)

    # Generate and save title if this is the first message
    if len(st.session_state['message_history']) == 1:  # Only user message, no assistant response yet
        try:
            title = generate_title(user_input)
            save_title(st.session_state['thread_id'], title)
        except Exception as e:
            print(f"Error generating title: {e}")
     
    # CONFIG = {'configurable':{'thread_id':str(st.session_state['thread_id'])}}


    CONFIG  = {
        "configurable":{"thread_id":str(st.session_state["thread_id"]),
                        },
        "metadata":{
            "thread_id": str(st.session_state["thread_id"])
        },
        "run_name":"chat_turn"
    }    
    
    with st.chat_message("assistant"):
        status_ref = {"container": None}
        
        def ai_only_stream():
            for  message_chunk, metadata in chatbot.stream(
                        {'messages': [HumanMessage(content=user_input)]},
                        config=CONFIG,
                        stream_mode="messages"
            ):
                 
                # Detect Tool Start - create status container only on first tool detection
                if metadata.get("langgraph_node") == "tools":
                    if status_ref["container"] is None:
                        status_ref["container"] = st.status("Running tools...", expanded=True)
                    tool_name = metadata.get("name","tool")
                    status_ref["container"].update(label=f"Running {tool_name}...", state="running")
                
                # Detect Tool End
                if isinstance(message_chunk, ToolMessage):
                    if status_ref["container"] is not None:
                        status_ref["container"].update(label="✅ Tool finished", state="complete")

                if isinstance(message_chunk, AIMessage):
                   yield message_chunk.content
        
        ai_message = st.write_stream(ai_only_stream)
        
    st.session_state['message_history'].append({"role": "assistant", "content": ai_message})




