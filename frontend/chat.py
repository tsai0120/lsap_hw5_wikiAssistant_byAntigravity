import streamlit as st
import dspy
import os

from agent import WikiAssistantAgent

wiki_assistant_agent = WikiAssistantAgent()

# Initialize chat history if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("Wikipedia Chat Assistant")

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
        response = wiki_assistant_agent(question=prompt, past_messages=past_messages)
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})


