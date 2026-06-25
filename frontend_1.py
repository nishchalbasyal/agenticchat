import streamlit as st
from backend_1 import chatbot
from langchain_core.messages import  HumanMessage


CONFIG = {'configurable':{'thread_id': '1'}}

message_history = []


user_input = st.chat_input('Type your message here...')

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []



#loading the message history
for message in st.session_state['message_history']:
    with st.chat_message(message["role"]):
        st.text(message["content"])

if user_input:
    st.session_state['message_history'].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.text(user_input)

    
    response = chatbot.invoke({'messages': [HumanMessage(content=user_input)]}, config=CONFIG)
    ai_message = response['messages'][-1].content
    # first add the mesage to message_hostory
    st.session_state['message_history'].append({"role": "assistant", "content": ai_message})
    with st.chat_message("assistant"):
        st.text(ai_message)



