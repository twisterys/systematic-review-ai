"""
arXiv Search Tool using the arXiv Atom API.
Queries preprints across CS, AI, Math, and Quantitative Biology.
"""

import urllib.parse
import xml.etree.ElementTree as ET
from typing import List, Dict, Any
from ..utils import http_get


def search_arxiv(query: str, max_results: int = 25) -> List[Dict[str, Any]]:
    """
    Search arXiv via public Atom XML API.
    Returns normalized study dicts.
    """
    clean_query = urllib.parse.quote(query)
    url = f"https://export.arxiv.org/api/query?search_query=all:{clean_query}&start=0&max_results={max_results}"
    
    try:
        resp = http_get(url, timeout=15)
        if resp.status_code != 200:
            return []
        
        root = ET.fromstring(resp.content)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        studies = []
        
        for entry in root.findall("atom:entry", ns):
            id_elem = entry.find("atom:id", ns)
            raw_id = id_elem.text if id_elem is not None else ""
            arxiv_id = raw_id.split("/abs/")[-1]
            
            title_elem = entry.find("atom:title", ns)
            title = title_elem.text.strip().replace("\n", " ") if title_elem is not None else ""
            
            summary_elem = entry.find("atom:summary", ns)
            abstract = summary_elem.text.strip().replace("\n", " ") if summary_elem is not None else ""
            
            published_elem = entry.find("atom:published", ns)
            year = published_elem.text[:4] if published_elem is not None else ""
            
            authors = []
            for author in entry.findall("atom:author", ns):
                name_elem = author.find("atom:name", ns)
                if name_elem is not None and name_elem.text:
                    authors.append(name_elem.text.strip())
            
            pdf_url = None
            for link in entry.findall("atom:link", ns):
                if link.get("title") == "pdf":
                    pdf_url = link.get("href")
            
            studies.append({
                "id": f"arXiv:{arxiv_id}",
                "source": "arXiv",
                "title": title,
                "authors": authors,
                "year": year,
                "abstract": abstract,
                "doi": "",
                "url": raw_id,
                "pdf_url": pdf_url,
                "full_text": None
            })
            
        return studies
    except Exception as e:
        print(f"[arXiv Tool] Search error: {e}")
        return []
