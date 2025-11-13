from config import BACKEND_URL
import requests


def get_chat_history() -> list[dict[str, str]]:
    """Retrieve chat history from the backend."""
    response = requests.get(f"{BACKEND_URL}/history")
    if response.status_code != 200:
        raise ValueError(f"Error retrieving chat history: {response.text}")
    data = response.json()
    return data.get("chat_history", [])


def update_chat_history(history: list[dict[str, str]]) -> None:
    """Update chat history in the backend."""
    response = requests.post(f"{BACKEND_URL}/history", json=history)
    if response.status_code != 200:
        raise ValueError(f"Error updating chat history: {response.text}")


def clear_chat_history() -> None:
    """Clear chat history in the backend."""
    response = requests.delete(f"{BACKEND_URL}/history")
    if response.status_code != 200:
        raise ValueError(f"Error clearing chat history: {response.text}")
