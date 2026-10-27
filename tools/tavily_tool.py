
import os
from urllib.parse import urlparse

from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

api_key = os.getenv("TAVILY_API_KEY")
client = TavilyClient(api_key=api_key) if api_key else None


def tavily_search(query: str) -> str:
    """Search for relevant web results and return concise Markdown links."""

    if client is None:
        return (
            "Hotel search is unavailable because TAVILY_API_KEY "
            "is not configured."
        )

    try:
        response = client.search(
            query=query,
            search_depth="advanced",
            max_results=5,
            include_answer=False,
        )
    except Exception:
        return (
            "Hotel search is temporarily unavailable. "
            "Please try again later."
        )

    results = response.get("results") or []
    if not results:
        return "No relevant accommodation results were found."

    formatted = []
    seen_urls = set()

    for item in results:
        title = (item.get("title") or "").strip()
        url = (item.get("url") or "").strip()
        snippet = " ".join(
            (item.get("content") or "").split()
        )

        if not title or not url:
            continue

        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            continue

        normalized_url = url.rstrip("/")
        if normalized_url in seen_urls:
            continue
        seen_urls.add(normalized_url)

        if len(snippet) > 240:
            snippet = snippet[:240].rsplit(" ", 1)[0] + "..."

        formatted.append(f"### [{title}]({url})")
        if snippet:
            formatted.append(snippet)
        formatted.append(f"[View website / listing]({url})")
        formatted.append("")

    if not formatted:
        return "No usable accommodation links were found."

    return "\n".join(formatted).strip()
