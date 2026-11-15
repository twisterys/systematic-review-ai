"""
OpenAlex Search Tool.
OpenAlex indexes over 250 million works globally with open access links and concepts.
Works without an API key (using courteous pool).
"""

from typing import List, Dict, Any
import urllib.parse
from ..config import Settings
from ..utils import http_get


def search_openalex(query: str, max_results: int = 25) -> List[Dict[str, Any]]:
    """
    Search OpenAlex works endpoint.
    Returns normalized study dicts.
    """
    email = Settings.OPENALEX_EMAIL or "researcher@example.com"
    clean_query = urllib.parse.quote(query)
    url = f"https://api.openalex.org/works?search={clean_query}&per-page={min(max_results, 50)}&mailto={email}"

    try:
        resp = http_get(url, timeout=12)
        if resp.status_code != 200:
            return []

        results = resp.json().get("results", [])
        studies = []
        for item in results:
            doi = (item.get("doi") or "").replace("https://doi.org/", "")
            
            # Reconstruct abstract from inverted index if needed
            abstract = ""
            inv_index = item.get("abstract_inverted_index")
            if inv_index:
                words = {}
                for word, pos_list in inv_index.items():
                    for pos in pos_list:
                        words[pos] = word
                abstract = " ".join(words[i] for i in sorted(words.keys()))

            authors = []
            for authorship in (item.get("authorships") or []):
                author_obj = authorship.get("author") or {}
                name = author_obj.get("display_name")
                if name:
                    authors.append(name)

            open_access = item.get("open_access") or {}
            pdf_url = open_access.get("oa_url")

            studies.append({
                "id": f"OpenAlex:{item.get('id', '').split('/')[-1]}",
                "source": "OpenAlex",
                "title": item.get("display_name") or item.get("title") or "",
                "authors": authors,
                "year": str(item.get("publication_year") or ""),
                "abstract": abstract,
                "doi": doi,
                "url": item.get("doi") or item.get("id") or "",
                "pdf_url": pdf_url,
                "full_text": None
            })
        return studies
    except Exception as e:
        print(f"[OpenAlex Tool] Error: {e}")
        return []
