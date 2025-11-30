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

import uuid
from datetime import datetime

HISTORY_FILE = "data/chat_history.json"

def load_data():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                data = json.load(f)
                # Check if data is in the new format (dict with "sessions")
                if isinstance(data, dict) and "sessions" in data:
                    return data
                # If it's a list (old format) or other invalid format, reset
                print("Detected old or invalid data format. Resetting chat history.")
                return {"sessions": {}}
        except Exception as e:
            print(f"Error loading data: {e}. Resetting chat history.")
            return {"sessions": {}}
    return {"sessions": {}}

def save_data(data):
    with open(HISTORY_FILE, "w") as f:
        json.dump(data, f)

# Initialize data
db = load_data()
if "folders" not in db:
    db["folders"] = {}
    save_data(db)

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


# Session & Folder Management Endpoints

@app.get("/folders")
def get_folders() -> dict[str, list[dict]]:
    global db
    db = load_data()
    folders_list = []
    for folder_id, folder_data in db.get("folders", {}).items():
        folders_list.append({
            "id": folder_id,
            "name": folder_data.get("name", "New Folder"),
            "created_at": folder_data.get("created_at", "")
        })
    folders_list.sort(key=lambda x: x["created_at"])
    return {"folders": folders_list}

@app.post("/folders")
def create_folder(name: str) -> dict[str, str]:
    global db
    folder_id = str(uuid.uuid4())
    db.setdefault("folders", {})[folder_id] = {
        "name": name,
        "created_at": datetime.now().isoformat()
    }
    save_data(db)
    return {"folder_id": folder_id, "name": name}

@app.delete("/folders/{folder_id}")
def delete_folder(folder_id: str) -> dict:
    global db
    if folder_id in db.get("folders", {}):
        # Move sessions in this folder to root (None)
        for session in db.get("sessions", {}).values():
            if session.get("folder_id") == folder_id:
                session["folder_id"] = None
        del db["folders"][folder_id]
        save_data(db)
    return {"message": "Folder deleted"}

@app.get("/sessions")
def get_sessions() -> dict[str, list[dict]]:
    global db
    db = load_data() # Reload to ensure freshness
    sessions_list = []
    for session_id, session_data in db.get("sessions", {}).items():
        sessions_list.append({
            "id": session_id,
            "title": session_data.get("title", "New Chat"),
            "folder_id": session_data.get("folder_id"),
            "created_at": session_data.get("created_at", "")
        })
    # Sort by created_at desc
    sessions_list.sort(key=lambda x: x["created_at"], reverse=True)
    return {"sessions": sessions_list}

@app.post("/sessions")
def create_session(title: str = "New Chat", folder_id: Union[str, None] = None) -> dict[str, str]:
    global db
    session_id = str(uuid.uuid4())
    db.setdefault("sessions", {})[session_id] = {
        "title": title,
        "folder_id": folder_id,
        "messages": [],
        "created_at": datetime.now().isoformat()
    }
    save_data(db)
    return {"session_id": session_id, "title": title}

@app.get("/sessions/{session_id}")
def get_session(session_id: str) -> dict:
    global db
    db = load_data()
    session = db.get("sessions", {}).get(session_id)
    if not session:
        return {"error": "Session not found"}
    return {"session": session}

@app.put("/sessions/{session_id}")
def update_session(session_id: str, messages: list[dict[str, str]]) -> dict:
    global db
    if session_id not in db.get("sessions", {}):
        return {"error": "Session not found"}
    db["sessions"][session_id]["messages"] = messages
    save_data(db)
    return {"message": "Session updated"}

@app.put("/sessions/{session_id}/title")
def update_session_title(session_id: str, title: str) -> dict:
    global db
    if session_id not in db.get("sessions", {}):
        return {"error": "Session not found"}
    db["sessions"][session_id]["title"] = title
    save_data(db)
    return {"message": "Title updated"}

@app.put("/sessions/{session_id}/folder")
def update_session_folder(session_id: str, folder_id: Union[str, None]) -> dict:
    global db
    if session_id not in db.get("sessions", {}):
        return {"error": "Session not found"}
    db["sessions"][session_id]["folder_id"] = folder_id
    save_data(db)
    return {"message": "Session folder updated"}

@app.delete("/sessions/{session_id}")
def delete_session(session_id: str) -> dict:
    global db
    if session_id in db.get("sessions", {}):
        del db["sessions"][session_id]
        save_data(db)
    return {"message": "Session deleted"}
