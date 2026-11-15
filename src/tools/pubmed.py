"""
PubMed Search Tool via NCBI Entrez E-utilities.
Queries PubMed, parses JSON/XML summaries, and returns standardized study records.
"""

import urllib.parse
import xml.etree.ElementTree as ET
from typing import List, Dict, Any
from ..config import Settings
from ..utils import http_get


def search_pubmed(query: str, max_results: int = 25) -> List[Dict[str, Any]]:
    """
    Search PubMed via NCBI Entrez E-utilities.
    Returns list of normalized study dicts.
    """
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    api_key_param = f"&api_key={Settings.NCBI_API_KEY}" if Settings.NCBI_API_KEY else ""
    
    try:
        # Step 1: ESearch to obtain PMIDs
        esearch_url = (
            f"{base_url}esearch.fcgi?db=pubmed&term={urllib.parse.quote(query)}"
            f"&retmax={max_results}&retmode=json{api_key_param}"
        )
        resp = http_get(esearch_url, timeout=12)
        if resp.status_code != 200:
            return []
        
        data = resp.json()
        id_list = data.get("esearchresult", {}).get("idlist", [])
        if not id_list:
            return []
        
        # Step 2: EFetch for structured XML (with abstracts)
        efetch_url = (
            f"{base_url}efetch.fcgi?db=pubmed&id={','.join(id_list)}"
            f"&retmode=xml{api_key_param}"
        )
        fetch_resp = http_get(efetch_url, timeout=15)
        if fetch_resp.status_code != 200:
            return []
        
        return parse_pubmed_xml(fetch_resp.content)
    except Exception as e:
        print(f"[PubMed Tool] Error during search: {e}")
        return []


def parse_pubmed_xml(xml_content: bytes) -> List[Dict[str, Any]]:
    """Parse PubMed efetch XML into standardized study dictionaries."""
    studies = []
    if not xml_content or xml_content == b"<empty></empty>":
        return []
    try:
        root = ET.fromstring(xml_content)
        for article in root.findall(".//PubmedArticle"):
            medline = article.find("MedlineCitation")
            if medline is None:
                continue
            
            pmid_elem = medline.find("PMID")
            pmid = pmid_elem.text if pmid_elem is not None else ""
            
            art = medline.find("Article")
            if art is None:
                continue
            
            title_elem = art.find("ArticleTitle")
            title = "".join(title_elem.itertext()).strip() if title_elem is not None else ""
            
            # Abstract
            abstract_parts = []
            abstract_elem = art.find("Abstract")
            if abstract_elem is not None:
                for text_elem in abstract_elem.findall("AbstractText"):
                    label = text_elem.get("Label", "")
                    part_text = "".join(text_elem.itertext()).strip()
                    if label:
                        abstract_parts.append(f"{label}: {part_text}")
                    else:
                        abstract_parts.append(part_text)
            abstract = "\n".join(abstract_parts)
            
            # Authors
            authors = []
            author_list = art.find("AuthorList")
            if author_list is not None:
                for au in author_list.findall("Author"):
                    last = au.find("LastName")
                    fore = au.find("ForeName")
                    name = f"{fore.text} {last.text}" if fore is not None and last is not None else (last.text if last is not None else "")
                    if name:
                        authors.append(name)
            
            # Year
            year = ""
            pub_date = art.find(".//JournalIssue/PubDate")
            if pub_date is not None:
                year_elem = pub_date.find("Year")
                if year_elem is not None:
                    year = year_elem.text
            
            # DOI
            doi = ""
            for el_id in art.findall(".//ELocationID"):
                if el_id.get("EIdType") == "doi":
                    doi = el_id.text
            
            studies.append({
                "id": f"PMID:{pmid}",
                "source": "PubMed",
                "title": title,
                "authors": authors,
                "year": year,
                "abstract": abstract,
                "doi": doi or "",
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else "",
                "pdf_url": None,
                "full_text": None
            })
    except Exception as e:
        print(f"[PubMed XML Parser] Parsing error: {e}")
    return studies
