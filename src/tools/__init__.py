from .pubmed import search_pubmed
from .arxiv_tool import search_arxiv
from .semantic_scholar import search_semantic_scholar
from .openalex import search_openalex
from .dedup import deduplicate_studies, normalize_title, is_title_duplicate
from .pdf_parser import extract_text_from_pdf_url

__all__ = [
    "search_pubmed",
    "search_arxiv",
    "search_semantic_scholar",
    "search_openalex",
    "deduplicate_studies",
    "normalize_title",
    "is_title_duplicate",
    "extract_text_from_pdf_url"
]
