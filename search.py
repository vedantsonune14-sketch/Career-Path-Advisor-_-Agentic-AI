from pathlib import Path

from tavily import TavilyClient
import os
from dotenv import load_dotenv

PROJECT_DIR = Path(__file__).resolve().parent
load_dotenv(PROJECT_DIR / ".env")
load_dotenv(PROJECT_DIR / "venv" / ".env")


def _get_secret(name: str) -> str:
    """Get key from environment first, then Streamlit secrets."""
    value = os.getenv(name)
    if value and value.strip():
        return value
    try:
        import streamlit as st
        return str(st.secrets.get(name, "")).strip()
    except Exception:
        return ""


def get_tavily_client():
    api_key = _get_secret("TAVILY_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Missing TAVILY_API_KEY. Add it in Streamlit secrets or .env."
        )
    return TavilyClient(api_key=api_key)


def search_job_market(target_role: str, degree: str, interests: str) -> list[dict]:
    """
    Fires 3 targeted searches to get rich, current job market data.
    Returns a list of result dicts with title, content, url.
    """
    client = get_tavily_client()

    queries = [
        f"{target_role} required skills 2025 India freshers",
        f"top companies hiring {target_role} India 2025 campus placement",
        f"how to become {target_role} after {degree} roadmap upskilling",
    ]

    results = []
    for query in queries:
        try:
            response = client.search(query, max_results=3)
            for r in response.get("results", []):
                results.append({
                    "title": r.get("title", ""),
                    "content": r.get("content", ""),
                    "url": r.get("url", ""),
                    "query": query,
                })
        except Exception as e:
            results.append({
                "title": f"Search failed for: {query}",
                "content": str(e),
                "url": "",
                "query": query,
            })

    return results


def search_followup(query: str) -> list[dict]:
    """Used by the ReAct loop for agent-driven follow-up searches."""
    client = get_tavily_client()
    try:
        response = client.search(query, max_results=3)
        return [
            {
                "title": r.get("title", ""),
                "content": r.get("content", ""),
                "url": r.get("url", ""),
                "query": query,
            }
            for r in response.get("results", [])
        ]
    except Exception as e:
        return [{"title": "Search error", "content": str(e), "url": "", "query": query}]
