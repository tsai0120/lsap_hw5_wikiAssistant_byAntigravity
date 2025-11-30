from config import BACKEND_URL
import requests


from config import BACKEND_URL
import requests


def get_sessions() -> list[dict]:
    """Retrieve all sessions from the backend."""
    response = requests.get(f"{BACKEND_URL}/sessions")
    if response.status_code != 200:
        return []
    data = response.json()
    return data.get("sessions", [])


def create_session(title: str = "New Chat") -> dict:
    """Create a new session."""
    response = requests.post(f"{BACKEND_URL}/sessions", params={"title": title})
    if response.status_code != 200:
        raise ValueError(f"Error creating session: {response.text}")
    return response.json()


def get_session_messages(session_id: str) -> list[dict[str, str]]:
    """Retrieve messages for a specific session."""
    response = requests.get(f"{BACKEND_URL}/sessions/{session_id}")
    if response.status_code != 200:
        raise ValueError(f"Error retrieving session: {response.text}")
    data = response.json()
    return data.get("session", {}).get("messages", [])


def update_session_messages(session_id: str, messages: list[dict[str, str]]) -> None:
    """Update messages for a specific session."""
    response = requests.put(f"{BACKEND_URL}/sessions/{session_id}", json=messages)
    if response.status_code != 200:
        raise ValueError(f"Error updating session: {response.text}")


def update_session_title(session_id: str, title: str) -> None:
    """Update title for a specific session."""
    response = requests.put(f"{BACKEND_URL}/sessions/{session_id}/title", params={"title": title})
    if response.status_code != 200:
        raise ValueError(f"Error updating session title: {response.text}")


def delete_session(session_id: str) -> None:
    """Delete a specific session."""
    response = requests.delete(f"{BACKEND_URL}/sessions/{session_id}")
    if response.status_code != 200:
        raise ValueError(f"Error deleting session: {response.text}")
