"""
Semantic Scholar Graph API Tool.
Provides academic search with citation graph tracking and open-access links.
"""

from typing import List, Dict, Any
from ..config import Settings
from ..utils import http_get
import urllib.parse


def search_semantic_scholar(query: str, max_results: int = 25) -> List[Dict[str, Any]]:
    """
    Search Semantic Scholar Graph API.
    Returns normalized study dicts.
    """
    clean_q = urllib.parse.quote(query)
    fields = "paperId,title,abstract,authors,year,externalIds,openAccessPdf,url"
    url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={clean_q}&limit={min(max_results, 50)}&fields={fields}"
    
    headers = {}
    if Settings.SEMANTIC_SCHOLAR_API_KEY:
        headers["x-api-key"] = Settings.SEMANTIC_SCHOLAR_API_KEY

    try:
        resp = http_get(url, headers=headers, timeout=12)
        if resp.status_code != 200:
            return []

        data = resp.json().get("data", [])
        studies = []
        for item in data:
            ext_ids = item.get("externalIds") or {}
            authors = [a.get("name", "") for a in (item.get("authors") or []) if a.get("name")]
            pdf_info = item.get("openAccessPdf") or {}

            studies.append({
                "id": f"S2:{item.get('paperId')}",
                "source": "SemanticScholar",
                "title": item.get("title", ""),
                "authors": authors,
                "year": str(item.get("year", "")) if item.get("year") else "",
                "abstract": item.get("abstract", "") or "",
                "doi": ext_ids.get("DOI", ""),
                "url": item.get("url", ""),
                "pdf_url": pdf_info.get("url"),
                "full_text": None
            })
        return studies
    except Exception as e:
        print(f"[Semantic Scholar Tool] Error: {e}")
        return []
