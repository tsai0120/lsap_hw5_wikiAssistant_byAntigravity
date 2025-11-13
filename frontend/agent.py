from dotenv import load_dotenv
import dspy
import requests
import os


load_dotenv()

from config import BACKEND_URL



def search_for_relevant_wiki_pages(keyword: str) -> list[str]:
    """
    Search for relevant Wikipedia URLs given a keyword.
    The keyword should be short and concise.
    For example, "Python" is a good keyword, while "Tell me about Python programming language" is not.
    Only accept one keyword per search, and return a list of relevant Wikipedia page URLs.
    Try to search for a general keyword rather than a specific one.
    """


    response = requests.get(f"{BACKEND_URL}/explore", params={"query": keyword})
    if response.status_code != 200:
        raise ValueError(f"Error searching for Wikipedia pages: {response.text}")
    data = response.json()
    return data.get("page_urls", [])


def search_for_relevant_chunks(url: str, query: str) -> list[str]:
    """Search for relevant chunks in a Wikipedia page given a URL and query."""

    response = requests.get(f"{BACKEND_URL}/query", params={"url": url, "query": query})
    if response.status_code != 200:
        raise ValueError(f"Error querying Wikipedia page: {response.text}")
    data = response.json()
    return data.get("relevant_chunks", [])


class QASignature(dspy.Signature):
    """Given a user question and chat history, return an answer."""

    past_messages: list = dspy.InputField(desc="Chat history as a list of messages")
    question: str = dspy.InputField(desc="User question to be answered")
    answer: str = dspy.OutputField(desc="Answer to the user question")


class WikiAssistantAgent(dspy.Module):
    def __init__(self, max_iterations: int = 10):
        self.max_iterations = max_iterations
        self.agent = dspy.ReAct(
            QASignature,
            tools=[
                search_for_relevant_wiki_pages,
                search_for_relevant_chunks,
            ],
            max_iters=self.max_iterations,
        )

    def forward(self, question, past_messages):
        return self.agent(past_messages=past_messages, question=question).answer
