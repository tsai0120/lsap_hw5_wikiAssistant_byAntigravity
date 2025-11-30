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
    update_session_folder,
    delete_session,
    get_folders,
    create_folder,
    delete_folder
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
        "loading": "Loading...",
        "theme": "Theme",
        "avatar": "Avatar",
        "folders": "Folders",
        "new_folder": "New Folder",
        "uncategorized": "Uncategorized",
        "edit": "Edit",
        "save": "Save",
        "cancel": "Cancel"
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
        "loading": "載入中...",
        "theme": "主題",
        "avatar": "頭像",
        "folders": "資料夾",
        "new_folder": "新資料夾",
        "uncategorized": "未分類",
        "edit": "編輯",
        "save": "儲存",
        "cancel": "取消"
    },
    # ... (Other languages omitted for brevity, defaulting to English if missing)
}

LANGUAGES = {
    "en": "English",
    "zh": "Traditional Chinese (繁體中文)",
    "es": "Spanish (Español)",
    "fr": "French (Français)",
    "de": "German (Deutsch)",
    "ja": "Japanese (日本語)"
}

THEMES = {
    "Claude": """
        <style>
        /* General App Styling */
        .stApp {
            background-color: #252529; /* Deep charcoal */
            color: #e1e1e3;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #1e1e21; /* Slightly darker sidebar */
            border-right: 1px solid #333;
        }
        
        /* Sidebar Buttons (Navigation List Style) */
        [data-testid="stSidebar"] .stButton > button {
            width: 100%;
            background-color: transparent;
            color: #9ca3af; /* Muted text */
            border: none;
            text-align: left;
            padding: 0.5rem 0.75rem;
            border-radius: 6px;
            transition: all 0.2s ease;
            font-weight: 400;
        }
        
        [data-testid="stSidebar"] .stButton > button:hover {
            background-color: #2d2d31;
            color: #e1e1e3;
        }
        
        [data-testid="stSidebar"] .stButton > button:active, 
        [data-testid="stSidebar"] .stButton > button:focus {
            background-color: #3a3a3e;
            color: #ffffff;
            border: none;
            box-shadow: none;
        }

        /* Headers */
        h1, h2, h3 {
            color: #ffffff;
            font-weight: 600;
            letter-spacing: -0.02em;
        }
        
        /* Chat Input */
        .stChatInputContainer {
            padding-bottom: 20px;
        }
        .stChatInputContainer textarea {
            background-color: #2d2d31;
            color: #e1e1e3;
            border: 1px solid #3f3f46;
            border-radius: 12px;
        }
        .stChatInputContainer textarea:focus {
            border-color: #71717a;
            box-shadow: none;
        }
        
        /* Expander (Settings/Folders) */
        .streamlit-expanderHeader {
            background-color: transparent;
            color: #e1e1e3;
            font-weight: 500;
        }
        
        /* Dividers */
        hr {
            border-color: #3f3f46;
        }
        </style>
    """,
    "Dark": """
        <style>
        .stApp { background-color: #0e1117; color: #fafafa; }
        </style>
    """,
    "Light": """
        <style>
        .stApp { background-color: #ffffff; color: #000000; }
        </style>
    """,
    "Cyberpunk": """
        <style>
        .stApp { background-color: #000b1e; color: #00f3ff; }
        .stButton>button { border: 1px solid #00f3ff; color: #00f3ff; background: transparent; }
        .stTextInput>div>div>input { color: #00f3ff; background-color: #001233; }
        </style>
    """,
    "Nature": """
        <style>
        .stApp { background-color: #f0f7f4; color: #2d3e40; }
        .stButton>button { background-color: #a3c4bc; color: white; border: none; }
        </style>
    """
}

AVATARS = {
    "Robot": "🤖",
    "User": "👤",
    "Alien": "👽",
    "Fox": "🦊",
    "Owl": "🦉"
}

# Initialize Session State
if "username" not in st.session_state:
    st.session_state.username = USERNAME
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "theme" not in st.session_state:
    st.session_state.theme = "Claude" # Default to Claude theme
if "user_avatar" not in st.session_state:
    st.session_state.user_avatar = "👤"
if "editing_message_index" not in st.session_state:
    st.session_state.editing_message_index = None

# Sidebar
with st.sidebar:
    # Language Selector
    language_code = st.selectbox(
        "Select Language / 選擇語言",
        options=list(LANGUAGES.keys()),
        format_func=lambda x: LANGUAGES[x],
        index=0
    )
    
    t = TRANSLATIONS.get(language_code, TRANSLATIONS.get("en", TRANSLATIONS["en"]))

    # Settings
    with st.expander(t["settings"]):
        new_username = st.text_input(t["username"], value=st.session_state.username)
        if new_username != st.session_state.username:
            st.session_state.username = new_username
            st.rerun()
        
        selected_theme = st.selectbox(t["theme"], list(THEMES.keys()), index=list(THEMES.keys()).index(st.session_state.theme))
        if selected_theme != st.session_state.theme:
            st.session_state.theme = selected_theme
            st.rerun()
            
        selected_avatar = st.selectbox(t["avatar"], list(AVATARS.keys()), index=list(AVATARS.values()).index(st.session_state.user_avatar) if st.session_state.user_avatar in AVATARS.values() else 1)
        st.session_state.user_avatar = AVATARS[selected_avatar]

    st.divider()

    # Folder Management
    st.header(t["folders"])
    new_folder_name = st.text_input(t["new_folder"], placeholder="Folder Name")
    if st.button("➕", key="add_folder"):
        if new_folder_name:
            create_folder(new_folder_name)
            st.rerun()

    folders = get_folders()
    sessions = get_sessions()
    
    # Organize sessions by folder
    sessions_by_folder = {None: []} # None for Uncategorized
    for f in folders:
        sessions_by_folder[f["id"]] = []
    
    for s in sessions:
        fid = s.get("folder_id")
        if fid not in sessions_by_folder:
            fid = None # Default to uncategorized if folder missing
        sessions_by_folder[fid].append(s)

    # Display Folders and Sessions
    
    # Uncategorized
    with st.expander(t["uncategorized"], expanded=True):
        for session in sessions_by_folder[None]:
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

    # User Folders
    for folder in folders:
        with st.expander(folder["name"]):
            if st.button(f"{t['delete']} {folder['name']}", key=f"del_folder_{folder['id']}"):
                delete_folder(folder['id'])
                st.rerun()
                
            for session in sessions_by_folder[folder["id"]]:
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

    if st.button(t["new_chat"], use_container_width=True):
        # Create new chat in current folder context if possible, or Uncategorized
        new_session = create_session(t["new_chat"])
        st.session_state.current_session_id = new_session["session_id"]
        st.session_state.messages = []
        st.rerun()

# Apply Theme
st.markdown(THEMES[st.session_state.theme], unsafe_allow_html=True)

# Main Chat Interface
st.title(t["title"])

if not st.session_state.current_session_id:
    if not sessions:
        new_session = create_session(t["new_chat"])
        st.session_state.current_session_id = new_session["session_id"]
        st.session_state.messages = []
    else:
        st.session_state.current_session_id = sessions[0]["id"]
        st.session_state.messages = get_session_messages(sessions[0]["id"])
        
# Session Folder Mover
current_session_info = next((s for s in sessions if s["id"] == st.session_state.current_session_id), None)
if current_session_info:
    folder_options = {"None": None}
    for f in folders:
        folder_options[f["name"]] = f["id"]
    
    current_folder_id = current_session_info.get("folder_id")
    current_folder_name = next((f["name"] for f in folders if f["id"] == current_folder_id), "None")
    
    selected_folder_name = st.selectbox("Move to Folder", list(folder_options.keys()), index=list(folder_options.keys()).index(current_folder_name) if current_folder_name in folder_options else 0, key="folder_mover")
    
    if folder_options[selected_folder_name] != current_folder_id:
        update_session_folder(st.session_state.current_session_id, folder_options[selected_folder_name])
        st.rerun()

st.markdown(t["greeting"].format(user=st.session_state.username))

# Display chat messages
for i, message in enumerate(st.session_state.messages):
    avatar = st.session_state.user_avatar if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar):
        if st.session_state.editing_message_index == i:
            new_content = st.text_area("Edit message", message["content"])
            col1, col2 = st.columns(2)
            with col1:
                if st.button(t["save"], key=f"save_{i}"):
                    st.session_state.messages[i]["content"] = new_content
                    st.session_state.editing_message_index = None
                    update_session_messages(st.session_state.current_session_id, list(st.session_state.messages))
                    st.rerun()
            with col2:
                if st.button(t["cancel"], key=f"cancel_{i}"):
                    st.session_state.editing_message_index = None
                    st.rerun()
        else:
            st.markdown(message["content"])
            if message["role"] == "user":
                if st.button("✏️", key=f"edit_{i}"):
                    st.session_state.editing_message_index = i
                    st.rerun()

# Accept user input
if prompt := st.chat_input(t["input_placeholder"]):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=st.session_state.user_avatar):
        st.markdown(prompt)

    # Smart Title Generation
    if len(st.session_state.messages) == 1:
        try:
            # Use a separate lightweight call to generate title
            lm_title = dspy.LM("gemini/gemini-2.5-flash", api_key=os.getenv("GEMINI_API_KEY"))
            with dspy.context(lm=lm_title):
                title_gen = dspy.Predict("messages -> title")
                title_response = title_gen(messages=str(prompt))
                new_title = title_response.title
                # Ensure title is short
                if len(new_title) > 20:
                    new_title = new_title[:20] + "..."
                update_session_title(st.session_state.current_session_id, new_title)
        except Exception:
            # Fallback
            new_title = prompt[:20] + "..." if len(prompt) > 20 else prompt
            update_session_title(st.session_state.current_session_id, new_title)

    with st.chat_message("assistant", avatar="🤖"):
        past_messages = st.session_state.messages[:-1]
        lm = dspy.LM("gemini/gemini-2.5-flash", api_key=os.getenv("GEMINI_API_KEY"))
        
        wiki_assistant_agent = WikiAssistantAgent(language=language_code)
        
        with dspy.context(lm=lm):
            response = wiki_assistant_agent(
                question=prompt, past_messages=past_messages, language=language_code
            )
        st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    try:
        update_session_messages(st.session_state.current_session_id, list(st.session_state.messages))
    except Exception as e:
        st.error(f"Error updating chat history: {e}")
