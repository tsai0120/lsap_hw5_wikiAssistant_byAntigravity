from typing import Union

from fastapi import FastAPI

from utils import (
    get_wiki_text_from_url,
    split_text_into_chunks,
    query_chunks_with_query,
    search_for_wikipedia_page_url,
)

app = FastAPI()

import json
import os

HISTORY_FILE = "data/chat_history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f)

chat_history = load_history()

@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Welcome to the Wiki Assistant API"}


@app.get("/query")
def query_wiki(url: str, query: str) -> dict[str, Union[list[str] | str, None]]:
    try:
        wiki_text = get_wiki_text_from_url(url)
        chunks = split_text_into_chunks(wiki_text)
        relevant_chunks = query_chunks_with_query(chunks, query)
        return {"relevant_chunks": relevant_chunks}
    except Exception as e:
        return {"error": str(e)}


@app.get("/explore")
def explore_relevant_wiki_pages(query: str, language: str = "en") -> dict[str, Union[list[str] | str, None]]:
    try:
        page_urls = search_for_wikipedia_page_url(query, language=language)
        if page_urls is None:
            return {"page_urls": []}
        return {"page_urls": page_urls}
    except Exception as e:
        return {"error": str(e)}


@app.get("/history")
def get_history() -> dict[str, list[dict[str, str]]]:
    global chat_history
    chat_history = load_history() # Reload to ensure freshness if modified externally
    return {"chat_history": chat_history}


@app.post("/history")
def modify_history(history: list[dict[str, str]]) -> dict[str, str]:
    global chat_history
    chat_history = history
    save_history(chat_history)
    return {"message": "Chat history updated successfully"}


@app.delete("/history")
def clear_history() -> dict[str, str]:
    global chat_history
    chat_history = []
    save_history(chat_history)
    return {"message": "Chat history cleared successfully"}
