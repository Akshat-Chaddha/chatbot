import importlib
import json
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
import backend
importlib.reload(backend)

SAVE_FILE = Path('chat_resume.json')
ARCHIVE_FILE = Path('chat_archive.json')


def history_to_messages(history):
    messages = []
    for msg in history:
        if not msg['content']:
            continue
        if msg['role'] == 'user':
            messages.append(HumanMessage(content=msg['content']))
        else:
            messages.append(AIMessage(content=msg['content']))
    return messages


def extract_personal_details(history):
    details = []
    keywords = [
        'my name is', 'i am', "i'm", 'call me', 'you can call me',
        'i work as', 'i work at', 'i am from', 'i live in', 'i like',
        'i love', 'i prefer', 'my favorite', 'favorite', 'interested in',
        'i enjoy', 'my email is', 'from ', 'based in', 'my birthday',
        'my age', 'i study', 'i go to', 'i am a', 'i am an', 'i feel',
    ]
    for msg in history:
        if msg.get('role') != 'user' or not msg.get('content'):
            continue
        content = msg['content'].strip()
        low = content.lower()
        if any(keyword in low for keyword in keywords):
            details.append(content)
    return details


def build_context_message():
    context_lines = []
    archive = load_json(ARCHIVE_FILE) or []
    saved = load_saved_history() or []

    for history in ([saved] if saved else []) + [item.get('history', []) for item in archive]:
        context_lines.extend(extract_personal_details(history))

    if not context_lines:
        return None

    summary = (
        'Use the following previous user details to personalize your response in this conversation. '
        'Remember names, preferences, favorites, and personal details mentioned earlier. '
        'Do not treat this context as part of the current chat history.'
    )
    for index, line in enumerate(context_lines[-20:], 1):
        summary += f"\n{index}. {line}"

    return SystemMessage(content=summary)


def build_request_messages(history):
    messages = []
    context_message = build_context_message()
    if context_message:
        messages.append(context_message)
    messages.extend(history_to_messages(history))
    return messages

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


def save_json(path: Path, data):
    path.write_text(json.dumps(data, indent=2), encoding='utf-8')


def load_json(path: Path):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding='utf-8'))
        except json.JSONDecodeError:
            return None
    return None


def save_current_history():
    save_json(SAVE_FILE, st.session_state.history)


def get_chat_title(history):
    first_user = next(
        (message['content'] for message in history if message['role'] == 'user' and message['content'].strip()),
        None,
    )
    if first_user:
        short = first_user.strip().replace('\n', ' ')
        return short[:60] + ('...' if len(short) > 60 else '')
    return 'Untitled chat'


def archive_current_history():
    archive = load_json(ARCHIVE_FILE) or []
    archive.append({
        'saved_at': datetime.now(timezone.utc).isoformat(),
        'title': get_chat_title(st.session_state.history),
        'history': st.session_state.history,
    })
    save_json(ARCHIVE_FILE, archive)


def load_saved_history():
    return load_json(SAVE_FILE)


def load_latest_archive():
    archive = load_json(ARCHIVE_FILE)
    if archive and isinstance(archive, list):
        return archive[-1]['history']
    return None


def delete_archive_entry(index):
    archive = load_json(ARCHIVE_FILE) or []
    if 0 <= index < len(archive):
        archive.pop(index)
        save_json(ARCHIVE_FILE, archive)


if 'history' not in st.session_state:
    loaded = load_saved_history()
    if loaded:
        st.session_state.history = loaded
    else:
        st.session_state.history = [
            {'role': 'assistant', 'content': 'Hello, how can I assist you today?'}
        ]

save_current_history()

if 'checkpoint_config' not in st.session_state:
    st.session_state.checkpoint_config = {
        'checkpoint_id': 'streamlit_chat',
        'checkpoint_ns': 'default',
        'thread_id': 'main',
    }

with st.sidebar:
    st.markdown('### Chat history')
    archived = load_json(ARCHIVE_FILE) or []
    archived_items = list(reversed(archived))

    if archived_items:
        st.caption('Open any previous conversation:')
        for index, item in enumerate(archived_items):
            title = item.get('title', 'Untitled chat')
            saved_at = item.get('saved_at', '')[:16]
            original_index = len(archived) - 1 - index
            cols = st.columns([4, 1])
            with cols[0]:
                if st.button(f'{title} — {saved_at}', key=f'archive_{index}'):
                    st.session_state.history = item.get('history', []) or [
                        {'role': 'assistant', 'content': 'Hello, how can I assist you today?'}
                    ]
                    save_current_history()
                    st.success('Loaded previous chat.')
            with cols[1]:
                if st.button('Delete', key=f'delete_{index}'):
                    delete_archive_entry(original_index)
                    st.success('Deleted archived chat.')
    else:
        st.info('No previous chats saved yet.')

    st.write('')
    if st.button('New conversation'):
        if len(st.session_state.history) > 1:
            archive_current_history()
        st.session_state.history = [
            {'role': 'assistant', 'content': 'Hello, how can I assist you today?'}
        ]
        save_current_history()

st.markdown('<div class="chat-panel">', unsafe_allow_html=True)
chat_display = st.empty()
user_input = st.chat_input('Write a message...')

if user_input:
    st.session_state.history.append({'role': 'user', 'content': user_input})
    st.session_state.history.append({'role': 'assistant', 'content': ''})
    chat_display.markdown(render_chat_html(st.session_state.history), unsafe_allow_html=True)

    history_messages = build_request_messages(st.session_state.history[:-1])
    for chunk in backend.stream_chat(history_messages, config=st.session_state.checkpoint_config):
        st.session_state.history[-1]['content'] += chunk
        chat_display.markdown(render_chat_html(st.session_state.history), unsafe_allow_html=True)

    if not st.session_state.history[-1]['content'].strip():
        st.session_state.history[-1]['content'] = 'Sorry, I could not generate a response.'
        chat_display.markdown(render_chat_html(st.session_state.history), unsafe_allow_html=True)

    save_current_history()
else:
    chat_display.markdown(render_chat_html(st.session_state.history), unsafe_allow_html=True)
