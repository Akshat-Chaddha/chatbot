import streamlit as st
from langchain_core.messages import HumanMessage
import backend

st.set_page_config(page_title='LangGraph Chatbot', page_icon='💬')
st.title('LangGraph Streamlit Chatbot')
st.write('A basic chat UI connected to the backend chatbot in `backend.py`.')

if 'history' not in st.session_state:
    st.session_state.history = [
        {'role': 'ai', 'content': 'Hello, how can I assist you today?'}
    ]

if 'checkpoint_config' not in st.session_state:
    st.session_state.checkpoint_config = {
        'checkpoint_id': 'streamlit_chat',
        'checkpoint_ns': 'default',
        'thread_id': 'main',
    }

with st.sidebar:
    st.header('Chat Controls')
    if st.button('Clear conversation'):
        st.session_state.history = [
            {'role': 'ai', 'content': 'Hello, how can I assist you today?'}
        ]

user_input = st.chat_input('Type your message here...')

if user_input:
    st.session_state.history.append({'role': 'user', 'content': user_input})
    try:
        result = backend.chatbot.invoke(
            {'messages': [HumanMessage(content=user_input)]},
            config=st.session_state.checkpoint_config,
        )
        ai_messages = result.get('messages', [])
        if ai_messages:
            bot_message = ai_messages[-1].content
        else:
            bot_message = 'Sorry, I could not generate a response.'
    except Exception as exc:
        bot_message = f'Error: {exc}'

    st.session_state.history.append({'role': 'ai', 'content': bot_message})

for message in st.session_state.history:
    with st.chat_message(message['role']):
        st.write(message['content'])
