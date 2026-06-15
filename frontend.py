import importlib
import streamlit as st
from langchain_core.messages import HumanMessage
import backend
importlib.reload(backend)

st.set_page_config(page_title='LangGraph Chatbot', page_icon='💬')

st.title('Chatbot')

st.markdown(
    """
    <style>
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    
    .stButton>button {
        border-radius: 999px;
    }
    .chat-history {
        display: flex;
        flex-direction: column;
        gap: 12px;
    }
    .message-row {
        display: flex;
        align-items: flex-start;
        gap: 12px;
    }
    .message-row.user {
        justify-content: flex-end;
    }
    .message-row.assistant {
        justify-content: flex-start;
    }
    .bubble {
        max-width: 74%;
        padding: 14px 18px;
        border-radius: 20px;
        line-height: 1.6;
        font-size: 0.98rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        word-break: break-word;
    }
    .assistant-bubble {
        background: #111827;
        color: #e2e8f0;
        border-top-left-radius: 6px;
        border-top-right-radius: 20px;
        border-bottom-left-radius: 20px;
        border-bottom-right-radius: 20px;
    }
    .user-bubble {
        background: #2563eb;
        color: white;
        border-top-left-radius: 20px;
        border-top-right-radius: 6px;
        border-bottom-left-radius: 20px;
        border-bottom-right-radius: 20px;
    }
    .avatar {
        width: 34px;
        height: 34px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 0.9rem;
        font-weight: 700;
        color: white;
    }
    .avatar.assistant {
        background: #2563eb;
    }
    .avatar.user {
        background: #111827;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def render_chat_html(history):
    safe_history = []
    for message in history:
        role = message['role']
        content = message['content'] or ''
        escaped = (
            content.replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('\n', '<br>')
        )
        bubble_class = 'assistant-bubble' if role != 'user' else 'user-bubble'
        avatar_label = 'AI' if role != 'user' else 'You'
        avatar_class = 'assistant' if role != 'user' else 'user'
        safe_history.append(
            f'<div class="message-row {role}">'
            f'<div class="avatar {avatar_class}">{avatar_label}</div>'
            f'<div class="bubble {bubble_class}">{escaped}</div>'
            '</div>'
        )
    return '<div class="chat-history">' + ''.join(safe_history) + '</div>'

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
chat_display = st.empty()
user_input = st.chat_input('Write a message...')

if user_input:
    st.session_state.history.append({'role': 'user', 'content': user_input})
    st.session_state.history.append({'role': 'assistant', 'content': ''})
    chat_display.markdown(render_chat_html(st.session_state.history), unsafe_allow_html=True)

    for chunk in backend.stream_chat([HumanMessage(content=user_input)], config=st.session_state.checkpoint_config):
        st.session_state.history[-1]['content'] += chunk
        chat_display.markdown(render_chat_html(st.session_state.history), unsafe_allow_html=True)

    if not st.session_state.history[-1]['content'].strip():
        st.session_state.history[-1]['content'] = 'Sorry, I could not generate a response.'
        chat_display.markdown(render_chat_html(st.session_state.history), unsafe_allow_html=True)
else:
    chat_display.markdown(render_chat_html(st.session_state.history), unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
