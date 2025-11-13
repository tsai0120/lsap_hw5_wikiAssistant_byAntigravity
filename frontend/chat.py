import streamlit as st
import dspy
import os

from agent import WikiAssistantAgent
from config import USERNAME

wiki_assistant_agent = WikiAssistantAgent()

from utils import get_chat_history, update_chat_history, clear_chat_history


# Initialize chat history if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("Wikipedia Chat Assistant")
st.markdown(
    """ Hello {user}! Ask me anything about Wikipedia articles. """.format(
        user=USERNAME
    )
)


def clear_history_callback():
    clear_chat_history()
    st.session_state.messages.clear()


st.button("Clear Chat History", on_click=clear_history_callback)

if not st.session_state.messages:
    # Load chat history from backend on first run
    try:
        history = get_chat_history()
        st.session_state.messages = history.copy()
    except Exception as e:
        st.error(f"Error loading chat history: {e}")
        st.session_state.messages = []


# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Say something"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Simulate assistant response
    with st.chat_message("assistant"):
        past_messages = st.session_state.messages[:-1]  # Exclude current user message
        lm = dspy.LM("gemini/gemini-2.5-flash", api_key=os.getenv("GEMINI_API_KEY"))
        with dspy.context(lm=lm):
            response = wiki_assistant_agent(
                question=prompt, past_messages=past_messages
            )
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
    # Update chat history in backend
    try:
        update_chat_history(list(st.session_state.messages))
    except Exception as e:
        st.error(f"Error updating chat history: {e}")
