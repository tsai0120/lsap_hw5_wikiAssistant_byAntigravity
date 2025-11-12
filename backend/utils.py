import requests
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer, util
from typing import Union


def get_wiki_text_from_url(url: str) -> str:

    try:
        session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(max_retries=3)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        response = session.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
    except requests.RequestException as e:
        raise ValueError(f"Failed to retrieve content from URL: {url}. Error: {e}")

    if not response.ok:
        # fallback to mobile Wikipedia if available
        if "wikipedia.org" in url:
            mobile_url = url.replace("en.wikipedia.org", "en.m.wikipedia.org")
            try:
                response = session.get(
                    mobile_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10
                )
            except requests.RequestException as e:
                raise ValueError(
                    f"Failed to retrieve content from URL: {url}. Error: {e}"
                )
            if not response.ok:
                raise ValueError(
                    f"Failed to retrieve content from URL: {url}. Status: {response.status_code} {response.reason}"
                )
        else:
            raise ValueError(
                f"Failed to retrieve content from URL: {url}. Status: {response.status_code} {response.reason}"
            )

    soup = BeautifulSoup(response.content, "html.parser")
    paragraphs = soup.find_all("p")
    wiki_text = "\n".join(
        paragraph.get_text() for paragraph in paragraphs if paragraph.get_text().strip()
    )

    return wiki_text


def search_for_wikipedia_page_url(query: str, top_k: int = 3) -> Union[list[str], None]:
    # search for the most relevant Wikipedia page for the given query using Wikipedia's search API
    search_url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "format": "json",
        "srlimit": top_k,
    }

    # provide a User-Agent header to avoid 403 Forbidden responses from the Wikipedia API
    headers = {"User-Agent": "wiki-assistant/1.0 (https://github.com)"} 

    try:
        response = requests.get(search_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        raise ValueError(f"Failed to search Wikipedia for query: {query}. Error: {e}")
    data = response.json()
    search_results = data.get("query", {}).get("search", [])
    if not search_results:
        return None
    page_urls = [
        f"https://en.wikipedia.org/wiki/{result['title'].replace(' ', '_')}"
        for result in search_results
    ]
    return page_urls


def split_text_into_chunks(
    text: str, chunk_size: int = 1000, overlap: int = 200
) -> list[str]:
    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap

    return chunks


def query_chunks_with_query(
    chunks: list[str],
    query: str,
    embedding_model: str = "all-MiniLM-L6-v2",
    top_k: int = 5,
) -> Union[list[str], None]:

    model = SentenceTransformer(embedding_model)
    query_embedding = model.encode(query, convert_to_tensor=True)
    chunk_embeddings = model.encode(chunks, convert_to_tensor=True)

    top_results = util.semantic_search(query_embedding, chunk_embeddings, top_k=top_k)[
        0
    ]

    if not top_results:
        return None
    relevant_chunks = [chunks[result["corpus_id"]] for result in top_results]

    return relevant_chunks
