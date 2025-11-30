import streamlit as st
import dspy
import os

from agent import WikiAssistantAgent
from config import USERNAME
from utils import (
    get_sessions,
    create_session,
    get_session_messages,
    update_session_messages,
    update_session_title,
    delete_session
)

# UI Translations
TRANSLATIONS = {
    "en": {
        "title": "Wikipedia Chat Assistant",
        "greeting": "Hello {user}! Ask me anything about Wikipedia articles.",
        "settings": "Settings",
        "username": "Username",
        "chat_history": "Chat History",
        "new_chat": "New Chat",
        "delete": "Delete",
        "input_placeholder": "Say something",
        "select_language": "Select Wikipedia Language",
        "loading": "Loading..."
    },
    "zh": {
        "title": "維基百科聊天助手",
        "greeting": "你好 {user}！問我任何關於維基百科條目的問題。",
        "settings": "設定",
        "username": "使用者名稱",
        "chat_history": "聊天記錄",
        "new_chat": "新對話",
        "delete": "刪除",
        "input_placeholder": "說點什麼...",
        "select_language": "選擇維基百科語言",
        "loading": "載入中..."
    },
    "es": {
        "title": "Asistente de Chat de Wikipedia",
        "greeting": "¡Hola {user}! Pregúntame cualquier cosa sobre artículos de Wikipedia.",
        "settings": "Configuración",
        "username": "Nombre de usuario",
        "chat_history": "Historial de Chat",
        "new_chat": "Nuevo Chat",
        "delete": "Eliminar",
        "input_placeholder": "Di algo",
        "select_language": "Seleccionar idioma de Wikipedia",
        "loading": "Cargando..."
    },
    "fr": {
        "title": "Assistant de Chat Wikipédia",
        "greeting": "Bonjour {user}! Demandez-moi n'importe quoi sur les articles Wikipédia.",
        "settings": "Paramètres",
        "username": "Nom d'utilisateur",
        "chat_history": "Historique du Chat",
        "new_chat": "Nouvelle Discussion",
        "delete": "Supprimer",
        "input_placeholder": "Dites quelque chose",
        "select_language": "Sélectionner la langue Wikipédia",
        "loading": "Chargement..."
    },
    "de": {
        "title": "Wikipedia Chat Assistent",
        "greeting": "Hallo {user}! Frag mich alles über Wikipedia-Artikel.",
        "settings": "Einstellungen",
        "username": "Benutzername",
        "chat_history": "Chat-Verlauf",
        "new_chat": "Neuer Chat",
        "delete": "Löschen",
        "input_placeholder": "Sag etwas",
        "select_language": "Wikipedia-Sprache auswählen",
        "loading": "Laden..."
    },
    "ja": {
        "title": "ウィキペディアチャットアシスタント",
        "greeting": "こんにちは {user}! ウィキペディアの記事について何でも聞いてください。",
        "settings": "設定",
        "username": "ユーザー名",
        "chat_history": "チャット履歴",
        "new_chat": "新しいチャット",
        "delete": "削除",
        "input_placeholder": "何か言ってください",
        "select_language": "ウィキペディアの言語を選択",
        "loading": "読み込み中..."
    }
}

LANGUAGES = {
    "en": "English",
    "zh": "Traditional Chinese (繁體中文)",
    "es": "Spanish (Español)",
    "fr": "French (Français)",
    "de": "German (Deutsch)",
    "ja": "Japanese (日本語)"
}

# Initialize Session State
if "username" not in st.session_state:
    st.session_state.username = USERNAME
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar
with st.sidebar:
    # Language Selector
    language_code = st.selectbox(
        "Select Language / 選擇語言", # Keep generic label for initial selection
        options=list(LANGUAGES.keys()),
        format_func=lambda x: LANGUAGES[x],
        index=0
    )
    
    t = TRANSLATIONS.get(language_code, TRANSLATIONS["en"])

    # Settings
    with st.expander(t["settings"]):
        new_username = st.text_input(t["username"], value=st.session_state.username)
        if new_username != st.session_state.username:
            st.session_state.username = new_username
            st.rerun()

    st.divider()

    # Chat History Management
    st.header(t["chat_history"])
    
    if st.button(t["new_chat"], use_container_width=True):
        new_session = create_session(t["new_chat"])
        st.session_state.current_session_id = new_session["session_id"]
        st.session_state.messages = []
        st.rerun()

    sessions = get_sessions()
    for session in sessions:
        col1, col2 = st.columns([0.8, 0.2])
        with col1:
            if st.button(session["title"], key=f"sess_{session['id']}", use_container_width=True):
                st.session_state.current_session_id = session["id"]
                st.session_state.messages = get_session_messages(session["id"])
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"del_{session['id']}"):
                delete_session(session["id"])
                if st.session_state.current_session_id == session["id"]:
                    st.session_state.current_session_id = None
                    st.session_state.messages = []
                st.rerun()

# Main Chat Interface
st.title(t["title"])

if not st.session_state.current_session_id:
    # Auto-create session if none exists
    if not sessions:
        new_session = create_session(t["new_chat"])
        st.session_state.current_session_id = new_session["session_id"]
        st.session_state.messages = []
    else:
        # Load most recent session
        st.session_state.current_session_id = sessions[0]["id"]
        st.session_state.messages = get_session_messages(sessions[0]["id"])

st.markdown(t["greeting"].format(user=st.session_state.username))

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input(t["input_placeholder"]):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Update session title if it's the first message
    if len(st.session_state.messages) == 1:
        # Simple truncation for title
        new_title = prompt[:30] + "..." if len(prompt) > 30 else prompt
        update_session_title(st.session_state.current_session_id, new_title)

    # Simulate assistant response
    with st.chat_message("assistant"):
        past_messages = st.session_state.messages[:-1]
        lm = dspy.LM("gemini/gemini-2.5-flash", api_key=os.getenv("GEMINI_API_KEY"))
        
        wiki_assistant_agent = WikiAssistantAgent(language=language_code)
        
        with dspy.context(lm=lm):
            response = wiki_assistant_agent(
                question=prompt, past_messages=past_messages, language=language_code
            )
        st.markdown(response)
    
    # Add assistant response
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Update backend
    try:
        update_session_messages(st.session_state.current_session_id, list(st.session_state.messages))
    except Exception as e:
        st.error(f"Error updating chat history: {e}")
