import importlib
import streamlit as st
from langchain_core.messages import HumanMessage
import backend
importlib.reload(backend)

st.set_page_config(page_title='LangGraph Chatbot', page_icon='💬')
st.title('LangGraph Chatbot')
st.caption('A clean, simple chat interface.')

st.markdown(
    """
    <style>
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    .chat-panel {
        background: #0f172a;
        border-radius: 24px;
        padding: 20px;
        box-shadow: 0 20px 50px rgba(15, 23, 42, 0.35);
    }
    .chat-panel .stMarkdown, .chat-panel .stText, .chat-panel .stCaption {
        color: #e2e8f0;
    }
    .stButton>button {
        border-radius: 999px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if 'history' not in st.session_state:
    st.session_state.history = [
        {'role': 'assistant', 'content': 'Hello, how can I assist you today?'}
    ]

if 'checkpoint_config' not in st.session_state:
    st.session_state.checkpoint_config = {
        'checkpoint_id': 'streamlit_chat',
        'checkpoint_ns': 'default',
        'thread_id': 'main',
    }

with st.sidebar:
    st.write('')
    if st.button('Clear conversation'):
        st.session_state.history = [
            {'role': 'assistant', 'content': 'Hello, how can I assist you today?'}
        ]

st.markdown('<div class="chat-panel">', unsafe_allow_html=True)
user_input = st.chat_input('Write a message...')

if user_input:
    st.session_state.history.append({'role': 'user', 'content': user_input})

    try:
        full_response = ''
        response_slot = st.empty()
        for chunk in backend.stream_chat([HumanMessage(content=user_input)], config=st.session_state.checkpoint_config):
            full_response += chunk
            response_slot.chat_message('assistant').write(full_response)
        bot_message = full_response.strip() or 'Sorry, I could not generate a response.'
    except Exception as exc:
        bot_message = f'Error: {exc}'
        response_slot.chat_message('assistant').write(bot_message)

    st.session_state.history.append({'role': 'assistant', 'content': bot_message})

for message in st.session_state.history:
    with st.chat_message(message['role']):
        st.write(message['content'])

st.markdown('</div>', unsafe_allow_html=True)
