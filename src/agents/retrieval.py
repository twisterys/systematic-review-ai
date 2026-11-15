"""
Retrieval Agent.
Executes database searches in parallel across PubMed, arXiv, Semantic Scholar, and OpenAlex.
Performs programmatic deduplication and builds the RAG index.
"""

from typing import Dict, Any, List, Tuple
from ..tools import (
    search_pubmed,
    search_arxiv,
    search_semantic_scholar,
    search_openalex,
    deduplicate_studies
)
from ..rag import PaperVectorStore


def run_retrieval_agent(
    search_strategies: Dict[str, str],
    vector_store: PaperVectorStore,
    max_per_source: int = 15
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], int]:
    """
    Executes search across academic sources, merges results, deduplicates, and indexes.

    Raises:
        ConnectionError: If no studies could be retrieved from any academic database.

    Returns:
        (raw_studies, deduplicated_studies, duplicates_removed_count)
    """
    raw_studies: List[Dict[str, Any]] = []

    # 1. PubMed
    if "pubmed" in search_strategies:
        pm_results = search_pubmed(search_strategies["pubmed"], max_results=max_per_source)
        raw_studies.extend(pm_results)

    # 2. arXiv
    if "arxiv" in search_strategies:
        ax_results = search_arxiv(search_strategies["arxiv"], max_results=max_per_source)
        raw_studies.extend(ax_results)

    # 3. Semantic Scholar
    if "semantic_scholar" in search_strategies:
        s2_results = search_semantic_scholar(search_strategies["semantic_scholar"], max_results=max_per_source)
        raw_studies.extend(s2_results)

    # 4. OpenAlex
    if "openalex" in search_strategies:
        oa_results = search_openalex(search_strategies["openalex"], max_results=max_per_source)
        raw_studies.extend(oa_results)

    # If offline or zero results from live networks, raise an explicit error
    if not raw_studies:
        raise ConnectionError(
            "❌ Échec de la récupération académique : Aucun article n'a pu être extrait depuis PubMed, arXiv, Semantic Scholar ou OpenAlex.\n"
            "Veuillez vérifier :\n"
            "1. Votre connexion Internet.\n"
            "2. La configuration de vos clés API dans le fichier .env (NCBI_API_KEY, SEMANTIC_SCHOLAR_API_KEY).\n"
            "3. L'exactitude des termes et mots-clés de recherche formulés."
        )

    # Deduplicate
    deduplicated_studies, dup_count = deduplicate_studies(raw_studies)

    # Index into RAG vector store
    vector_store.add_papers(deduplicated_studies)

    return raw_studies, deduplicated_studies, dup_count
